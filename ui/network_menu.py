"""Interactive Network Status menu for Pivotctl."""

import os

try:
    from ui.colours import Colour, colour_text
except ModuleNotFoundError:
    from colours import Colour, colour_text

from core.config import get_setting
from core.hosts import get_managed_hosts
from core.network import (
    display_interfaces,
    display_routes,
    display_vpn_status,
    get_network_summary,
)
from core.pivots import pivot_manager
from core.proxychains import (
    get_chain_mode,
    get_proxies,
    get_proxy_dns,
)


def clear_screen():
    """Clear the terminal when enabled."""

    try:
        enabled = get_setting(
            "interface",
            "clear_screen",
        )
    except (
        KeyError,
        ValueError,
        OSError,
    ):
        enabled = True

    if enabled:
        os.system(
            "cls"
            if os.name == "nt"
            else "clear"
        )


def pause():
    """Pause before returning to the menu."""

    input(
        colour_text(
            "\n Press Enter to continue...",
            Colour.BRIGHT_GREEN,
        )
    )


def error(message):
    """Display an error message."""

    print(
        colour_text(
            f"\n[-] {message}",
            Colour.BRIGHT_RED,
        )
    )


def show_header(title):
    """Display a standard Network Status header."""

    print(
        colour_text(
            "═" * 68,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            title.center(68),
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 68,
            Colour.BRIGHT_GREEN,
        )
    )

    print()


def show_network_overview():
    """Display the main Pivotctl network overview."""

    clear_screen()

    show_header(
        "NETWORK STATUS"
    )

    try:
        summary = get_network_summary()

    except RuntimeError as exception:
        error(
            str(exception)
        )
        return

    try:
        hosts = get_managed_hosts()
        proxies = get_proxies()
        pivots = pivot_manager.get_pivots()

        chain_mode = get_chain_mode()
        proxy_dns = get_proxy_dns()

    except (
        FileNotFoundError,
        ValueError,
        OSError,
        PermissionError,
    ) as exception:
        error(
            str(exception)
        )
        return

    default_route = summary[
        "default_route"
    ]

    print(
        colour_text(
            " LOCAL NETWORK",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        f"  Interfaces        : "
        f"{len(summary['interfaces'])}"
    )

    print(
        f"  Active Interfaces : "
        f"{len(summary['active_interfaces'])}"
    )

    print(
        f"  Routes            : "
        f"{len(summary['routes'])}"
    )

    print(
        f"  VPN / Tunnels     : "
        f"{len(summary['vpn_interfaces'])}"
    )

    if default_route:

        print(
            f"  Default Interface : "
            f"{default_route['interface']}"
        )

        print(
            f"  Default Gateway   : "
            f"{default_route['gateway']}"
        )

        print(
            f"  Local Source      : "
            f"{default_route['source']}"
        )

    else:

        print(
            "  Default Interface : -"
        )

        print(
            "  Default Gateway   : -"
        )

        print(
            "  Local Source      : -"
        )

    if summary["vpn_interfaces"]:

        tunnel_names = ", ".join(
            interface["name"]
            for interface
            in summary["vpn_interfaces"]
        )

        print(
            f"  Tunnel Interfaces : "
            f"{tunnel_names}"
        )

    else:

        print(
            "  Tunnel Interfaces : -"
        )

    print()

    print(
        colour_text(
            " PIVOTCTL STATE",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        f"  Managed Hosts     : "
        f"{len(hosts)}"
    )

    print(
        f"  Proxy Chain       : "
        f"{chain_mode}"
    )

    print(
        f"  Proxy DNS         : "
        f"{'enabled' if proxy_dns else 'disabled'}"
    )

    print(
        f"  Proxies           : "
        f"{len(proxies)}"
    )

    print(
        f"  Pivots            : "
        f"{len(pivots)}"
    )

    networks = sum(
        len(
            pivot.get(
                "networks",
                [],
            )
        )
        for pivot in pivots
    )

    print(
        f"  Pivot Networks    : "
        f"{networks}"
    )


def show_network_menu():
    """Display Network Status menu options."""

    print(
        """
 [1] Full Interface Details
 [2] Routing Table
 [3] VPN / Tunnel Interfaces
 [4] Pivotctl Configuration
 [5] Pivot Topology

 [R] Refresh
 [B] Back
"""
    )


def display_interface_screen():
    """Display full interface details."""

    clear_screen()

    show_header(
        "INTERFACE DETAILS"
    )

    try:
        display_interfaces()

    except RuntimeError as exception:
        error(
            str(exception)
        )


def display_routes_screen():
    """Display the routing table."""

    clear_screen()

    show_header(
        "ROUTING TABLE"
    )

    try:
        display_routes()

    except RuntimeError as exception:
        error(
            str(exception)
        )


def display_vpn_screen():
    """Display VPN and tunnel interfaces."""

    clear_screen()

    show_header(
        "VPN / TUNNEL INTERFACES"
    )

    try:
        display_vpn_status()

    except RuntimeError as exception:
        error(
            str(exception)
        )


def display_pivotctl_configuration():
    """Display Pivotctl configuration state."""

    clear_screen()

    show_header(
        "PIVOTCTL CONFIGURATION"
    )

    hosts = get_managed_hosts()
    proxies = get_proxies()
    pivots = pivot_manager.get_pivots()

    print(
        f" Managed Hosts : {len(hosts)}"
    )

    print(
        f" Chain Mode    : "
        f"{get_chain_mode()}"
    )

    print(
        f" Proxy DNS     : "
        f"{'enabled' if get_proxy_dns() else 'disabled'}"
    )

    print(
        f" Proxies       : {len(proxies)}"
    )

    print(
        f" Pivots        : {len(pivots)}"
    )

    networks = sum(
        len(
            pivot.get(
                "networks",
                [],
            )
        )
        for pivot in pivots
    )

    print(
        f" Pivot Networks: {networks}"
    )

    if hosts:

        print(
            colour_text(
                "\n MANAGED HOSTS",
                Colour.BRIGHT_CYAN,
            )
        )

        print(
            " " + "─" * 54
        )

        for host in hosts:

            names = " ".join(
                host["hostnames"]
            )

            print(
                f"  {host['ip']:<20} "
                f"{names}"
            )

    else:

        print(
            colour_text(
                "\n No Pivotctl managed hosts.",
                Colour.BRIGHT_YELLOW,
            )
        )

    if proxies:

        print(
            colour_text(
                "\n PROXIES",
                Colour.BRIGHT_CYAN,
            )
        )

        print(
            " " + "─" * 54
        )

        for index, proxy in enumerate(
            proxies,
            start=1,
        ):

            print(
                f"  [{index}] "
                f"{proxy['type']:<8} "
                f"{proxy['host']}:"
                f"{proxy['port']}"
            )

    else:

        print(
            colour_text(
                "\n No proxies configured.",
                Colour.BRIGHT_YELLOW,
            )
        )

    if pivots:

        print(
            colour_text(
                "\n PIVOTS",
                Colour.BRIGHT_CYAN,
            )
        )

        print(
            " " + "─" * 54
        )

        for pivot in pivots:

            print(
                f"  [{pivot['id']}] "
                f"{pivot['name']:<16} "
                f"{pivot['address']:<18} "
                f"{pivot['tool']}"
            )

    else:

        print(
            colour_text(
                "\n No pivots configured.",
                Colour.BRIGHT_YELLOW,
            )
        )

    print()


def display_topology_screen():
    """Display current Pivotctl pivot topology."""

    clear_screen()

    show_header(
        "PIVOT TOPOLOGY"
    )

    pivot_manager.display_topology()


def network_menu():
    """Run the interactive Network Status menu."""

    while True:

        try:
            show_network_overview()
            show_network_menu()

            choice = input(
                colour_text(
                    " pivot/network > ",
                    Colour.BRIGHT_GREEN,
                )
            ).strip().lower()

            if choice == "1":
                display_interface_screen()
                pause()

            elif choice == "2":
                display_routes_screen()
                pause()

            elif choice == "3":
                display_vpn_screen()
                pause()

            elif choice == "4":
                display_pivotctl_configuration()
                pause()

            elif choice == "5":
                display_topology_screen()
                pause()

            elif choice in (
                "6",
                "r",
            ):
                continue

            elif choice == "b":
                return

            else:
                error(
                    "Invalid selection. "
                    "Please try again."
                )
                pause()

        except (
            FileNotFoundError,
            ValueError,
            TypeError,
            IndexError,
            PermissionError,
            OSError,
        ) as exception:

            error(
                str(exception)
            )
            pause()


if __name__ == "__main__":
    network_menu()