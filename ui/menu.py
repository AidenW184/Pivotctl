"""Main interactive menu for Pivotctl."""

import os
import socket

try:
    from ui.banner import show_banner
    from ui.colours import Colour, colour_text
    from ui.hosts_menu import hosts_menu
    from ui.proxychains_menu import proxychains_menu
    from ui.pivots_menu import pivot_menu
    from ui.profiles_menu import profiles_menu
    from ui.network_menu import network_menu
    from ui.test_menu import test_configuration_menu

except ModuleNotFoundError:
    from banner import show_banner
    from colours import Colour, colour_text
    from hosts_menu import hosts_menu
    from proxychains_menu import proxychains_menu
    from pivots_menu import pivot_menu
    from profiles_menu import profiles_menu
    from network_menu import network_menu
    from test_menu import test_configuration_menu

from core.config import get_setting
from core.hosts import get_managed_hosts
from core.network import get_network_summary
from core.pivots import pivot_manager
from core.proxychains import (
    get_chain_mode,
    get_proxies,
    get_proxy_dns,
)


def clear_screen():
    """Clear the terminal when enabled in settings."""

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


def get_dashboard_data():
    """Collect information displayed on the main dashboard."""

    data = {
        "hostname": socket.gethostname(),
        "interface": "-",
        "local_ip": "-",
        "gateway": "-",
        "vpn": "None",
        "managed_hosts": 0,
        "chain_mode": "-",
        "proxy_dns": "-",
        "proxy": "None",
        "pivots": 0,
        "pivot_networks": 0,
    }

    try:
        summary = get_network_summary()

        default_route = summary.get(
            "default_route"
        )

        if default_route:
            data["interface"] = (
                default_route.get(
                    "interface"
                )
                or "-"
            )

            data["local_ip"] = (
                default_route.get(
                    "source"
                )
                or "-"
            )

            data["gateway"] = (
                default_route.get(
                    "gateway"
                )
                or "-"
            )

        vpn_interfaces = summary.get(
            "vpn_interfaces",
            [],
        )

        if vpn_interfaces:
            data["vpn"] = ", ".join(
                interface["name"]
                for interface
                in vpn_interfaces
            )

    except (
        RuntimeError,
        OSError,
        ValueError,
    ):
        pass

    try:
        data["managed_hosts"] = len(
            get_managed_hosts()
        )

    except (
        OSError,
        ValueError,
    ):
        data["managed_hosts"] = "?"

    try:
        data["chain_mode"] = (
            get_chain_mode()
        )

        data["proxy_dns"] = (
            "enabled"
            if get_proxy_dns()
            else "disabled"
        )

        proxies = get_proxies()

        if proxies:
            proxy = proxies[0]

            data["proxy"] = (
                f"{proxy['type']} "
                f"{proxy['host']}:"
                f"{proxy['port']}"
            )

            if len(proxies) > 1:
                data["proxy"] += (
                    f" (+{len(proxies) - 1})"
                )

    except (
        OSError,
        ValueError,
    ):
        pass

    try:
        pivots = pivot_manager.get_pivots()

        data["pivots"] = len(
            pivots
        )

        data["pivot_networks"] = sum(
            len(
                pivot.get(
                    "networks",
                    [],
                )
            )
            for pivot in pivots
        )

    except (
        TypeError,
        ValueError,
    ):
        pass

    return data


def show_dashboard():
    """Display current system and Pivotctl state."""

    data = get_dashboard_data()

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                         PIVOT STATUS",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print()

    print(
        colour_text(
            " SYSTEM",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        f"  Host          : "
        f"{data['hostname']}"
    )

    print(
        f"  Interface     : "
        f"{data['interface']}"
    )

    print(
        f"  Local IP      : "
        f"{data['local_ip']}"
    )

    print(
        f"  Gateway       : "
        f"{data['gateway']}"
    )

    print(
        f"  VPN / Tunnel  : "
        f"{data['vpn']}"
    )

    print()

    print(
        colour_text(
            " PIVOTCTL",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        f"  Managed Hosts : "
        f"{data['managed_hosts']}"
    )

    print(
        f"  Proxy Chain   : "
        f"{data['chain_mode']}"
    )

    print(
        f"  Proxy DNS     : "
        f"{data['proxy_dns']}"
    )

    print(
        f"  Proxy         : "
        f"{data['proxy']}"
    )

    print(
        f"  Pivots        : "
        f"{data['pivots']}"
    )

    print(
        f"  Pivot Networks: "
        f"{data['pivot_networks']}"
    )

    print()


def show_main_menu():
    """Display the main Pivotctl menu."""

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                           MAIN MENU",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        """
 [1] Hosts Manager
 [2] ProxyChains Manager
 [3] Pivot Manager
 [4] Profiles
 [5] Network Status
 [6] Test Configuration

 [R] Refresh
 [Q] Quit
"""
    )


def draw_main_screen():
    """Draw the complete main Pivotctl screen."""

    clear_screen()

    show_banner()
    show_dashboard()
    show_main_menu()


def pause(message):
    """Display a message and wait before redrawing."""

    print(
        colour_text(
            f"\n[-] {message}",
            Colour.BRIGHT_RED,
        )
    )

    input(
        colour_text(
            "\n Press Enter to continue...",
            Colour.BRIGHT_GREEN,
        )
    )


def main_menu():
    """Run the main interactive menu loop."""

    while True:

        draw_main_screen()

        choice = input(
            colour_text(
                " pivot > ",
                Colour.BRIGHT_GREEN,
            )
        ).strip().lower()

        if choice == "1":
            hosts_menu()

        elif choice == "2":
            proxychains_menu()

        elif choice == "3":
            pivot_menu()

        elif choice == "4":
            profiles_menu()

        elif choice == "5":
            network_menu()

        elif choice == "6":
            test_configuration_menu()

        elif choice == "r":
            continue

        elif choice == "q":
            clear_screen()

            print(
                colour_text(
                    "\n[+] Goodbye.\n",
                    Colour.BRIGHT_GREEN,
                )
            )

            return

        else:
            pause(
                "Invalid selection. "
                "Please try again."
            )


if __name__ == "__main__":
    main_menu()