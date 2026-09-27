"""Interactive Profiles menu for Pivotctl."""

import os

try:
    from ui.colours import Colour, colour_text

except ModuleNotFoundError:
    from colours import Colour, colour_text

from core.config import get_setting
from core.profiles import (
    delete_profile,
    display_profile,
    list_profiles,
    load_profile,
    profile_exists,
    save_profile,
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


def success(message):
    """Display a success message."""

    print(
        colour_text(
            f"\n[+] {message}",
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


def warning(message):
    """Display a warning message."""

    print(
        colour_text(
            f"\n[!] {message}",
            Colour.BRIGHT_YELLOW,
        )
    )


def info(message):
    """Display an informational message."""

    print(
        colour_text(
            f"\n[*] {message}",
            Colour.BRIGHT_CYAN,
        )
    )


def show_profile_summary():
    """Display available profiles."""

    profiles = list_profiles()

    print(
        f" Saved Profiles : "
        f"{colour_text(str(len(profiles)), Colour.BRIGHT_CYAN)}"
    )

    if not profiles:
        print(
            colour_text(
                "\n No profiles saved.",
                Colour.BRIGHT_YELLOW,
            )
        )
        return

    print()

    for index, profile_name in enumerate(
        profiles,
        start=1,
    ):
        print(
            f" [{index}] {profile_name}"
        )


def show_profiles_menu():
    """Display the Profiles menu."""

    clear_screen()

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                          PROFILES",
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

    show_profile_summary()

    print(
        """
 [1] Save Current Profile
 [2] Load Profile
 [3] View Profile
 [4] Delete Profile

 [R] Refresh
 [B] Back
"""
    )


def choose_profile():
    """Prompt the user to select a profile."""

    profiles = list_profiles()

    if not profiles:
        warning(
            "No profiles are currently saved."
        )
        return None

    print()

    for index, profile_name in enumerate(
        profiles,
        start=1,
    ):
        print(
            f" [{index}] {profile_name}"
        )

    print(
        "\n [B] Cancel"
    )

    selection = input(
        colour_text(
            "\n Profile ID > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip().lower()

    if selection == "b":
        info(
            "Selection cancelled."
        )
        return None

    try:
        index = int(selection) - 1

        if (
            index < 0
            or index >= len(profiles)
        ):
            raise IndexError

        return profiles[index]

    except (
        ValueError,
        IndexError,
    ):
        error(
            "Invalid profile selection."
        )
        return None


def save_profile_menu():
    """Save current Pivotctl state."""

    print(
        colour_text(
            "\nSAVE CURRENT PROFILE",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    name = input(
        " Profile Name: "
    ).strip()

    if not name:
        error(
            "Profile name cannot be empty."
        )
        return

    overwrite = False

    try:
        exists = profile_exists(
            name
        )

    except ValueError as exception:
        error(
            str(exception)
        )
        return

    if exists:

        warning(
            f"Profile already exists: {name}"
        )

        confirmation = input(
            " Overwrite profile [y/N]: "
        ).strip().lower()

        if confirmation not in (
            "y",
            "yes",
        ):
            info(
                "Save cancelled."
            )
            return

        overwrite = True

    try:
        save_profile(
            name,
            overwrite=overwrite,
        )

        success(
            f"Profile saved: {name}"
        )

    except (
        ValueError,
        OSError,
    ) as exception:
        error(
            str(exception)
        )


def load_profile_menu():
    """Load a saved Pivotctl profile."""

    print(
        colour_text(
            "\nLOAD PROFILE",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    name = choose_profile()

    if name is None:
        return

    warning(
        "Loading this profile will replace "
        "the current Pivotctl-managed Hosts, "
        "ProxyChains and Pivot state."
    )

    confirmation = input(
        " Continue [y/N]: "
    ).strip().lower()

    if confirmation not in (
        "y",
        "yes",
    ):
        info(
            "Profile load cancelled."
        )
        return

    try:
        load_profile(
            name
        )

        success(
            f"Profile loaded: {name}"
        )

    except (
        ValueError,
        OSError,
    ) as exception:
        error(
            str(exception)
        )


def view_profile_menu():
    """Display a saved profile summary."""

    print(
        colour_text(
            "\nVIEW PROFILE",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    name = choose_profile()

    if name is None:
        return

    try:
        clear_screen()

        print(
            colour_text(
                "═" * 64,
                Colour.BRIGHT_GREEN,
            )
        )

        print(
            colour_text(
                "                      PROFILE DETAILS",
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

        display_profile(
            name
        )

    except (
        ValueError,
        OSError,
    ) as exception:
        error(
            str(exception)
        )


def delete_profile_menu():
    """Delete a saved profile."""

    print(
        colour_text(
            "\nDELETE PROFILE",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    name = choose_profile()

    if name is None:
        return

    warning(
        f"About to permanently delete "
        f"profile: {name}"
    )

    confirmation = input(
        " Confirm deletion [y/N]: "
    ).strip().lower()

    if confirmation not in (
        "y",
        "yes",
    ):
        info(
            "Deletion cancelled."
        )
        return

    try:
        delete_profile(
            name
        )

        success(
            f"Profile deleted: {name}"
        )

    except (
        ValueError,
        OSError,
    ) as exception:
        error(
            str(exception)
        )


def profiles_menu():
    """Run the interactive Profiles menu."""

    while True:

        try:
            show_profiles_menu()

            choice = input(
                colour_text(
                    " pivot/profiles > ",
                    Colour.BRIGHT_GREEN,
                )
            ).strip().lower()

            if choice == "1":
                save_profile_menu()
                pause()

            elif choice == "2":
                load_profile_menu()
                pause()

            elif choice == "3":
                view_profile_menu()
                pause()

            elif choice == "4":
                delete_profile_menu()
                pause()

            elif choice == "r":
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
    profiles_menu()