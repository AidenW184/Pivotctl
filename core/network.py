"""Network discovery and status functions for Pivotctl."""

import json
import shutil
import subprocess


VPN_PREFIXES = (
    "tun",
    "tap",
    "wg",
    "ppp",
)


def check_ip_command():
    """Check whether the Linux 'ip' command is available."""

    if shutil.which("ip") is None:
        raise RuntimeError(
            "The 'ip' command was not found. "
            "Pivotctl requires the iproute2 package."
        )


def run_ip_command(arguments):
    """Run an iproute2 command and return parsed JSON output."""

    check_ip_command()

    command = ["ip", "-j"] + arguments

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            "Network command timed out."
        ) from error

    except subprocess.CalledProcessError as error:
        message = (
            error.stderr.strip()
            or "Unknown iproute2 error."
        )

        raise RuntimeError(
            f"Network command failed: {message}"
        ) from error

    try:
        return json.loads(
            result.stdout
        )

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Failed to parse iproute2 JSON output."
        ) from error


def get_interfaces():
    """Return information about local network interfaces."""

    raw_interfaces = run_ip_command(
        ["addr", "show"]
    )

    interfaces = []

    for interface in raw_interfaces:

        name = interface.get(
            "ifname",
            "unknown",
        )

        state = interface.get(
            "operstate",
            "UNKNOWN",
        )

        mtu = interface.get(
            "mtu"
        )

        ipv4_addresses = []
        ipv6_addresses = []

        for address in interface.get(
            "addr_info",
            [],
        ):

            family = address.get(
                "family"
            )

            local = address.get(
                "local"
            )

            prefixlen = address.get(
                "prefixlen"
            )

            if not local:
                continue

            formatted_address = (
                f"{local}/{prefixlen}"
            )

            if family == "inet":
                ipv4_addresses.append(
                    formatted_address
                )

            elif family == "inet6":
                ipv6_addresses.append(
                    formatted_address
                )

        interfaces.append(
            {
                "name": name,
                "state": state,
                "mtu": mtu,
                "ipv4": ipv4_addresses,
                "ipv6": ipv6_addresses,
            }
        )

    return interfaces


def get_routes():
    """Return the local IPv4 routing table."""

    raw_routes = run_ip_command(
        ["route", "show"]
    )

    routes = []

    for route in raw_routes:

        destination = route.get(
            "dst",
            "default",
        )

        gateway = route.get(
            "gateway",
            "-",
        )

        interface = route.get(
            "dev",
            "-",
        )

        source = route.get(
            "prefsrc",
            "-",
        )

        routes.append(
            {
                "destination": destination,
                "gateway": gateway,
                "interface": interface,
                "source": source,
            }
        )

    return routes


def get_default_route(routes=None):
    """Return the primary IPv4 default route."""

    if routes is None:
        routes = get_routes()

    for route in routes:

        if (
            route["destination"]
            == "default"
        ):
            return route

    return None


def get_vpn_interfaces(interfaces=None):
    """Return detected VPN or tunnel interfaces."""

    if interfaces is None:
        interfaces = get_interfaces()

    return [
        interface
        for interface in interfaces
        if interface[
            "name"
        ].lower().startswith(
            VPN_PREFIXES
        )
    ]


def get_active_interfaces(
    interfaces=None,
):
    """Return active local interfaces."""

    if interfaces is None:
        interfaces = get_interfaces()

    return [
        interface
        for interface in interfaces
        if interface[
            "state"
        ].upper() == "UP"
    ]


def get_network_summary():
    """Return a consolidated local network summary."""

    interfaces = get_interfaces()
    routes = get_routes()

    active_interfaces = (
        get_active_interfaces(
            interfaces
        )
    )

    vpn_interfaces = (
        get_vpn_interfaces(
            interfaces
        )
    )

    default_route = (
        get_default_route(
            routes
        )
    )

    return {
        "interfaces": interfaces,
        "active_interfaces": active_interfaces,
        "routes": routes,
        "vpn_interfaces": vpn_interfaces,
        "default_route": default_route,
    }


def display_interfaces(
    interfaces=None,
):
    """Display local interfaces in a readable table."""

    if interfaces is None:
        interfaces = get_interfaces()

    print()
    print(
        "NETWORK INTERFACES"
    )
    print("-" * 75)

    print(
        f"{'INTERFACE':<20}"
        f"{'STATE':<12}"
        f"{'IPv4':<28}"
        f"{'MTU'}"
    )

    print("-" * 75)

    if not interfaces:
        print(
            "No network interfaces detected."
        )
        print()
        return

    for interface in interfaces:

        ipv4 = (
            ", ".join(
                interface["ipv4"]
            )
            or "-"
        )

        print(
            f"{interface['name']:<20}"
            f"{interface['state']:<12}"
            f"{ipv4:<28}"
            f"{interface['mtu']}"
        )

    print()


def display_routes(
    routes=None,
):
    """Display the IPv4 routing table."""

    if routes is None:
        routes = get_routes()

    print()
    print(
        "ROUTING TABLE"
    )
    print("-" * 85)

    print(
        f"{'DESTINATION':<25}"
        f"{'GATEWAY':<20}"
        f"{'INTERFACE':<20}"
        f"{'SOURCE'}"
    )

    print("-" * 85)

    if not routes:
        print(
            "No IPv4 routes detected."
        )
        print()
        return

    for route in routes:

        print(
            f"{route['destination']:<25}"
            f"{route['gateway']:<20}"
            f"{route['interface']:<20}"
            f"{route['source']}"
        )

    print()


def display_vpn_status(
    vpn_interfaces=None,
):
    """Display detected VPN/tunnel interfaces."""

    if vpn_interfaces is None:
        vpn_interfaces = (
            get_vpn_interfaces()
        )

    print()
    print(
        "VPN / TUNNEL INTERFACES"
    )
    print("-" * 55)

    if not vpn_interfaces:

        print(
            "No VPN or tunnel "
            "interfaces detected."
        )

        print()
        return

    for interface in vpn_interfaces:

        ipv4 = (
            ", ".join(
                interface["ipv4"]
            )
            or "No IPv4 address"
        )

        print(
            f"{interface['name']:<15} "
            f"{interface['state']:<10} "
            f"{ipv4}"
        )

    print()


def display_default_route(
    default_route=None,
):
    """Display the primary default route."""

    if default_route is None:
        default_route = (
            get_default_route()
        )

    print()
    print(
        "DEFAULT ROUTE"
    )
    print("-" * 55)

    if default_route is None:

        print(
            "No IPv4 default route detected."
        )

        print()
        return

    print(
        f"Gateway   : "
        f"{default_route['gateway']}"
    )

    print(
        f"Interface : "
        f"{default_route['interface']}"
    )

    print(
        f"Source    : "
        f"{default_route['source']}"
    )

    print()


def display_network_summary():
    """Display a concise local network summary."""

    summary = get_network_summary()

    print()
    print(
        "LOCAL NETWORK SUMMARY"
    )
    print("-" * 55)

    print(
        f"Interfaces       : "
        f"{len(summary['interfaces'])}"
    )

    print(
        f"Active Interfaces: "
        f"{len(summary['active_interfaces'])}"
    )

    print(
        f"Routes           : "
        f"{len(summary['routes'])}"
    )

    print(
        f"VPN / Tunnels    : "
        f"{len(summary['vpn_interfaces'])}"
    )

    default_route = summary[
        "default_route"
    ]

    if default_route:

        print(
            f"Default Interface: "
            f"{default_route['interface']}"
        )

        print(
            f"Default Gateway  : "
            f"{default_route['gateway']}"
        )

        print(
            f"Default Source   : "
            f"{default_route['source']}"
        )

    else:

        print(
            "Default Interface: -"
        )

        print(
            "Default Gateway  : -"
        )

        print(
            "Default Source   : -"
        )

    if summary[
        "vpn_interfaces"
    ]:

        vpn_names = ", ".join(
            interface["name"]
            for interface
            in summary[
                "vpn_interfaces"
            ]
        )

        print(
            f"Tunnel Interfaces: "
            f"{vpn_names}"
        )

    else:

        print(
            "Tunnel Interfaces: -"
        )

    print()


def display_network_status():
    """Display complete local network status."""

    summary = get_network_summary()

    display_interfaces(
        summary["interfaces"]
    )

    display_routes(
        summary["routes"]
    )

    display_vpn_status(
        summary["vpn_interfaces"]
    )

    display_default_route(
        summary["default_route"]
    )


if __name__ == "__main__":

    try:
        display_network_status()

    except RuntimeError as error:
        print(
            f"[!] {error}"
        )