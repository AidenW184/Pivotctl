#!/usr/bin/env python3

"""Pivotctl - Network Pivot Configuration Manager."""

from ui.menu import main_menu


def main():
    """Launch Pivotctl."""

    main_menu()


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print(
            "\n\n[!] Pivotctl interrupted by user."
        )

        print(
            "[+] Goodbye.\n"
        )