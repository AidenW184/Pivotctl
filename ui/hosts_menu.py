"""Interactive Hosts Manager menu for Pivotctl."""

import os

from core.config import get_setting
from core.hosts import (
    add_host,
    display_managed_hosts,
    display_parsed_hosts,
    edit_host,
    get_managed_hosts,
    remove_host,
    remove_hostname,
)

from ui.colours import Colour, colour_text


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
    """Wait for the user before redrawing."""

    input(
        colour_text(
            "\n Press Enter to continue...",
            Colour.BRIGHT_GREEN,
        )
    )


def show_hosts_menu():
    """Display the Hosts Manager menu."""

    clear_screen()

    print(
        colour_text(
            "═" * 58,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                     HOSTS MANAGER",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 58,
            Colour.BRIGHT_GREEN,
        )
    )

    display_managed_hosts()

    print(
        """
 [1] Add Host
 [2] Edit Host
 [3] Remove Host
 [4] Remove Hostname / Alias
 [5] View All Hosts

 [B] Back
"""
    )


def prompt_hostnames():
    """Prompt for one or more space-separated hostnames."""

    raw_hostnames = input(
        colour_text(
            " Hostname(s) > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    if not raw_hostnames:
        raise ValueError(
            "At least one hostname is required."
        )

    return raw_hostnames.split()


def prompt_host_id(entries):
    """Prompt for a displayed host ID."""

    if not entries:
        raise ValueError(
            "No Pivotctl managed hosts exist."
        )

    raw_id = input(
        colour_text(
            " Host ID > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    try:
        host_id = int(raw_id)

    except ValueError as error:
        raise ValueError(
            "Host ID must be a number."
        ) from error

    index = host_id - 1

    if (
        index < 0
        or index >= len(entries)
    ):
        raise ValueError(
            f"Host ID must be between "
            f"1 and {len(entries)}."
        )

    return index


def add_host_interactive():
    """Interactively add a managed host."""

    print(
        colour_text(
            "\n[*] Add Host",
            Colour.BRIGHT_CYAN,
        )
    )

    ip_address = input(
        colour_text(
            " IP Address  > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    hostnames = prompt_hostnames()

    backup_path = add_host(
        ip_address,
        hostnames,
    )

    print(
        colour_text(
            "\n[+] Host configuration updated.",
            Colour.BRIGHT_GREEN,
        )
    )

    if backup_path:
        print(
            colour_text(
                f"[+] Backup created: "
                f"{backup_path.name}",
                Colour.BRIGHT_GREEN,
            )
        )


def edit_host_interactive():
    """Interactively edit a managed host."""

    entries = get_managed_hosts()

    if not entries:
        raise ValueError(
            "No Pivotctl managed hosts exist."
        )

    print(
        colour_text(
            "\n[*] Edit Host",
            Colour.BRIGHT_CYAN,
        )
    )

    index = prompt_host_id(
        entries
    )

    current = entries[index]

    print(
        colour_text(
            f"[*] Current IP: "
            f"{current['ip']}",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            f"[*] Current hostname(s): "
            f"{', '.join(current['hostnames'])}",
            Colour.BRIGHT_CYAN,
        )
    )

    ip_address = input(
        colour_text(
            " New IP Address > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    hostnames = prompt_hostnames()

    old_entry, backup_path = edit_host(
        index,
        ip_address,
        hostnames,
    )

    print(
        colour_text(
            "\n[+] Host configuration updated.",
            Colour.BRIGHT_GREEN,
        )
    )

    if backup_path:
        print(
            colour_text(
                f"[+] Backup created: "
                f"{backup_path.name}",
                Colour.BRIGHT_GREEN,
            )
        )


def remove_host_interactive():
    """Interactively remove an entire managed host."""

    entries = get_managed_hosts()

    if not entries:
        raise ValueError(
            "No Pivotctl managed hosts exist."
        )

    print(
        colour_text(
            "\n[*] Remove Host",
            Colour.BRIGHT_CYAN,
        )
    )

    index = prompt_host_id(
        entries
    )

    selected = entries[index]

    print(
        colour_text(
            f"[!] Selected: "
            f"{selected['ip']} "
            f"{' '.join(selected['hostnames'])}",
            Colour.BRIGHT_YELLOW,
        )
    )

    confirmation = input(
        colour_text(
            " Remove this host? [y/N] > ",
            Colour.BRIGHT_YELLOW,
        )
    ).strip().lower()

    if confirmation != "y":
        print(
            colour_text(
                "[*] Removal cancelled.",
                Colour.BRIGHT_CYAN,
            )
        )
        return

    removed_entry, backup_path = remove_host(
        index
    )

    print(
        colour_text(
            "\n[-] Host removed.",
            Colour.BRIGHT_RED,
        )
    )

    if backup_path:
        print(
            colour_text(
                f"[+] Backup created: "
                f"{backup_path.name}",
                Colour.BRIGHT_GREEN,
            )
        )


def remove_hostname_interactive():
    """Interactively remove one hostname or alias."""

    entries = get_managed_hosts()

    if not entries:
        raise ValueError(
            "No Pivotctl managed hosts exist."
        )

    print(
        colour_text(
            "\n[*] Remove Hostname / Alias",
            Colour.BRIGHT_CYAN,
        )
    )

    index = prompt_host_id(
        entries
    )

    selected = entries[index]

    print(
        colour_text(
            f"[*] Hostnames: "
            f"{', '.join(selected['hostnames'])}",
            Colour.BRIGHT_CYAN,
        )
    )

    hostname = input(
        colour_text(
            " Hostname to remove > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    confirmation = input(
        colour_text(
            f" Remove '{hostname}'? "
            f"[y/N] > ",
            Colour.BRIGHT_YELLOW,
        )
    ).strip().lower()

    if confirmation != "y":
        print(
            colour_text(
                "[*] Removal cancelled.",
                Colour.BRIGHT_CYAN,
            )
        )
        return

    backup_path = remove_hostname(
        index,
        hostname,
    )

    print(
        colour_text(
            "\n[-] Hostname removed.",
            Colour.BRIGHT_RED,
        )
    )

    if backup_path:
        print(
            colour_text(
                f"[+] Backup created: "
                f"{backup_path.name}",
                Colour.BRIGHT_GREEN,
            )
        )


def hosts_menu():
    """Run the interactive Hosts Manager."""

    while True:

        try:
            show_hosts_menu()

            choice = input(
                colour_text(
                    " hosts > ",
                    Colour.BRIGHT_GREEN,
                )
            ).strip().lower()

            if choice == "1":
                add_host_interactive()
                pause()

            elif choice == "2":
                edit_host_interactive()
                pause()

            elif choice == "3":
                remove_host_interactive()
                pause()

            elif choice == "4":
                remove_hostname_interactive()
                pause()

            elif choice == "5":
                clear_screen()

                print(
                    colour_text(
                        "═" * 58,
                        Colour.BRIGHT_GREEN,
                    )
                )

                print(
                    colour_text(
                        "                      ALL HOSTS",
                        Colour.BRIGHT_CYAN,
                    )
                )

                print(
                    colour_text(
                        "═" * 58,
                        Colour.BRIGHT_GREEN,
                    )
                )

                print()

                display_parsed_hosts()
                pause()

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
    hosts_menu()