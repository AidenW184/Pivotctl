"""Interactive ProxyChains Manager for Pivotctl."""

import os

try:
    from ui.colours import Colour, colour_text

except ModuleNotFoundError:
    from colours import Colour, colour_text

from core.config import get_setting
from core.proxychains import (
    add_proxy,
    edit_proxy,
    get_chain_mode,
    get_proxies,
    get_proxy_dns,
    read_proxychains,
    remove_proxy,
    set_chain_mode,
    toggle_proxy_dns,
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
    """Wait before redrawing the screen."""

    input(
        colour_text(
            "\n Press Enter to continue...",
            Colour.BRIGHT_GREEN,
        )
    )


def show_proxychains_status():
    """Display the current ProxyChains state."""

    chain_mode = get_chain_mode()
    proxy_dns = get_proxy_dns()
    proxies = get_proxies()

    clear_screen()

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                     PROXYCHAINS MANAGER",
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
        f" Current Chain : "
        f"{colour_text(chain_mode or 'Not configured', Colour.BRIGHT_CYAN)}"
    )

    dns_state = (
        colour_text(
            "enabled",
            Colour.BRIGHT_GREEN,
        )
        if proxy_dns
        else colour_text(
            "disabled",
            Colour.BRIGHT_RED,
        )
    )

    print(
        f" Proxy DNS     : {dns_state}"
    )

    print(
        f" Proxies       : {len(proxies)}"
    )

    print()

    print(
        f" {'ID':<5}"
        f"{'TYPE':<12}"
        f"{'HOST':<28}"
        f"{'PORT'}"
    )

    print(
        " " + "─" * 50
    )

    if not proxies:

        print(
            colour_text(
                " No active proxies.",
                Colour.BRIGHT_YELLOW,
            )
        )

    else:

        for index, proxy in enumerate(
            proxies,
            start=1,
        ):

            print(
                f" {index:<5}"
                f"{proxy['type']:<12}"
                f"{proxy['host']:<28}"
                f"{proxy['port']}"
            )

    print()


def show_proxychains_menu():
    """Display ProxyChains Manager options."""

    print(
        """
 [1] Add Proxy
 [2] Edit Proxy
 [3] Remove Proxy
 [4] Set Chain Mode
 [5] Toggle Proxy DNS
 [6] View Configuration

 [R] Refresh
 [B] Back
"""
    )


def add_proxy_menu():
    """Interactively add a proxy."""

    print(
        colour_text(
            "\n[*] Add Proxy",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "\n Supported types: "
        "socks4, socks5, http\n"
    )

    proxy_type = input(
        colour_text(
            " Proxy Type > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip().lower()

    host = input(
        colour_text(
            " Proxy Host > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    port = input(
        colour_text(
            " Proxy Port > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    backup_path = add_proxy(
        proxy_type,
        host,
        port,
    )

    print(
        colour_text(
            f"\n[+] Added "
            f"{proxy_type}://{host}:{port}",
            Colour.BRIGHT_GREEN,
        )
    )

    if backup_path:

        print(
            colour_text(
                f"[*] Backup: {backup_path}",
                Colour.BRIGHT_CYAN,
            )
        )


def edit_proxy_menu():
    """Interactively edit an existing proxy."""

    proxies = get_proxies()

    if not proxies:

        print(
            colour_text(
                "\n[!] No proxies available to edit.",
                Colour.BRIGHT_YELLOW,
            )
        )

        return

    print(
        colour_text(
            "\n[*] Edit Proxy",
            Colour.BRIGHT_CYAN,
        )
    )

    proxy_id = input(
        colour_text(
            " Proxy ID > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    try:
        index = int(proxy_id) - 1

    except ValueError as error:
        raise ValueError(
            "Proxy ID must be a number."
        ) from error

    if (
        index < 0
        or index >= len(proxies)
    ):
        raise IndexError(
            "Proxy ID is out of range."
        )

    current = proxies[index]

    print(
        colour_text(
            "\n[*] Press Enter to keep "
            "the current value.",
            Colour.BRIGHT_CYAN,
        )
    )

    proxy_type = input(
        f" Proxy Type [{current['type']}] > "
    ).strip().lower()

    host = input(
        f" Proxy Host [{current['host']}] > "
    ).strip()

    port = input(
        f" Proxy Port [{current['port']}] > "
    ).strip()

    if not proxy_type:
        proxy_type = current["type"]

    if not host:
        host = current["host"]

    if not port:
        port = current["port"]

    old_proxy, backup_path = edit_proxy(
        index,
        proxy_type,
        host,
        port,
    )

    print(
        colour_text(
            "\n[+] Proxy updated.",
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            f"[*] Previous: "
            f"{old_proxy['type']}://"
            f"{old_proxy['host']}:"
            f"{old_proxy['port']}",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            f"[*] Current : "
            f"{proxy_type}://"
            f"{host}:{port}",
            Colour.BRIGHT_CYAN,
        )
    )

    if backup_path:

        print(
            colour_text(
                f"[*] Backup: {backup_path}",
                Colour.BRIGHT_CYAN,
            )
        )


def remove_proxy_menu():
    """Interactively remove an existing proxy."""

    proxies = get_proxies()

    if not proxies:

        print(
            colour_text(
                "\n[!] No proxies available to remove.",
                Colour.BRIGHT_YELLOW,
            )
        )

        return

    print(
        colour_text(
            "\n[*] Remove Proxy",
            Colour.BRIGHT_CYAN,
        )
    )

    proxy_id = input(
        colour_text(
            " Proxy ID > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    try:
        index = int(proxy_id) - 1

    except ValueError as error:
        raise ValueError(
            "Proxy ID must be a number."
        ) from error

    if (
        index < 0
        or index >= len(proxies)
    ):
        raise IndexError(
            "Proxy ID is out of range."
        )

    proxy = proxies[index]

    print(
        colour_text(
            f"\n[!] Remove "
            f"{proxy['type']}://"
            f"{proxy['host']}:"
            f"{proxy['port']}?",
            Colour.BRIGHT_YELLOW,
        )
    )

    confirm = input(
        colour_text(
            " Confirm [y/N] > ",
            Colour.BRIGHT_YELLOW,
        )
    ).strip().lower()

    if confirm != "y":

        print(
            colour_text(
                "\n[*] Removal cancelled.",
                Colour.BRIGHT_CYAN,
            )
        )

        return

    removed_proxy, backup_path = remove_proxy(
        index
    )

    print(
        colour_text(
            f"\n[-] Removed "
            f"{removed_proxy['type']}://"
            f"{removed_proxy['host']}:"
            f"{removed_proxy['port']}",
            Colour.BRIGHT_RED,
        )
    )

    if backup_path:

        print(
            colour_text(
                f"[*] Backup: {backup_path}",
                Colour.BRIGHT_CYAN,
            )
        )


def set_chain_mode_menu():
    """Interactively change the ProxyChains mode."""

    current_mode = get_chain_mode()

    modes = {
        "1": "dynamic_chain",
        "2": "strict_chain",
        "3": "round_robin_chain",
        "4": "random_chain",
    }

    print(
        colour_text(
            "\n[*] Set Chain Mode",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        f"\n Current: {current_mode}\n"
    )

    print(
        """
 [1] dynamic_chain
 [2] strict_chain
 [3] round_robin_chain
 [4] random_chain

 [B] Cancel
"""
    )

    choice = input(
        colour_text(
            " chain > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip().lower()

    if choice == "b":
        return

    if choice not in modes:
        raise ValueError(
            "Invalid chain mode selection."
        )

    new_mode = modes[choice]

    if new_mode == current_mode:

        print(
            colour_text(
                f"\n[*] {new_mode} is already active.",
                Colour.BRIGHT_CYAN,
            )
        )

        return

    backup_path = set_chain_mode(
        new_mode
    )

    print(
        colour_text(
            f"\n[+] Chain mode set to "
            f"{new_mode}.",
            Colour.BRIGHT_GREEN,
        )
    )

    if backup_path:

        print(
            colour_text(
                f"[*] Backup: {backup_path}",
                Colour.BRIGHT_CYAN,
            )
        )


def toggle_proxy_dns_menu():
    """Interactively toggle ProxyChains DNS."""

    current_state = get_proxy_dns()

    current_text = (
        "enabled"
        if current_state
        else "disabled"
    )

    new_text = (
        "disabled"
        if current_state
        else "enabled"
    )

    print(
        colour_text(
            f"\n[!] Proxy DNS is currently "
            f"{current_text}.",
            Colour.BRIGHT_YELLOW,
        )
    )

    confirm = input(
        colour_text(
            f" Change to {new_text}? [y/N] > ",
            Colour.BRIGHT_YELLOW,
        )
    ).strip().lower()

    if confirm != "y":

        print(
            colour_text(
                "\n[*] No changes made.",
                Colour.BRIGHT_CYAN,
            )
        )

        return

    new_state, backup_path = (
        toggle_proxy_dns()
    )

    state_text = (
        "enabled"
        if new_state
        else "disabled"
    )

    print(
        colour_text(
            f"\n[+] Proxy DNS {state_text}.",
            Colour.BRIGHT_GREEN,
        )
    )

    if backup_path:

        print(
            colour_text(
                f"[*] Backup: {backup_path}",
                Colour.BRIGHT_CYAN,
            )
        )


def view_configuration_menu():
    """Display the complete ProxyChains file."""

    contents = read_proxychains()

    clear_screen()

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                 PROXYCHAINS CONFIGURATION",
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
    print(contents)

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )


def proxychains_menu():
    """Run the ProxyChains Manager."""

    while True:

        try:
            show_proxychains_status()
            show_proxychains_menu()

            choice = input(
                colour_text(
                    " proxychains > ",
                    Colour.BRIGHT_GREEN,
                )
            ).strip().lower()

            if choice == "1":
                add_proxy_menu()
                pause()

            elif choice == "2":
                edit_proxy_menu()
                pause()

            elif choice == "3":
                remove_proxy_menu()
                pause()

            elif choice == "4":
                set_chain_mode_menu()
                pause()

            elif choice == "5":
                toggle_proxy_dns_menu()
                pause()

            elif choice == "6":
                view_configuration_menu()
                pause()

            elif choice == "r":
                continue

            elif choice == "b":
                return

            else:

                print(
                    colour_text(
                        "\n[-] Invalid selection. "
                        "Please try again.",
                        Colour.BRIGHT_RED,
                    )
                )

                pause()

        except (
            FileNotFoundError,
            ValueError,
            TypeError,
            IndexError,
            PermissionError,
        ) as error:

            print(
                colour_text(
                    f"\n[-] {error}",
                    Colour.BRIGHT_RED,
                )
            )

            pause()


if __name__ == "__main__":
    proxychains_menu()