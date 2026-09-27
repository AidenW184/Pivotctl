"""Configuration Test interface for Pivotctl."""

import os

try:
    from ui.colours import Colour, colour_text

except ModuleNotFoundError:
    from colours import Colour, colour_text

from core.config import get_setting
from core.tester import (
    FAIL,
    PASS,
    WARN,
    count_results,
    run_configuration_tests,
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
    """Wait before returning to the main menu."""

    input(
        colour_text(
            "\n Press Enter to continue...",
            Colour.BRIGHT_GREEN,
        )
    )


def status_colour(status):
    """Return the terminal colour for a test status."""

    if status == PASS:
        return Colour.BRIGHT_GREEN

    if status == WARN:
        return Colour.BRIGHT_YELLOW

    return Colour.BRIGHT_RED


def display_result(result):
    """Display one diagnostic result."""

    status = result["status"]

    label = colour_text(
        f"[{status}]",
        status_colour(status),
    )

    print(
        f"{label} "
        f"{result['name']:<24} "
        f"{result['message']}"
    )


def display_summary(counts):
    """Display diagnostic totals."""

    print()

    print(
        "─" * 72
    )

    pass_text = colour_text(
        f"{counts[PASS]} PASS",
        Colour.BRIGHT_GREEN,
    )

    warn_text = colour_text(
        f"{counts[WARN]} WARN",
        Colour.BRIGHT_YELLOW,
    )

    fail_text = colour_text(
        f"{counts[FAIL]} FAIL",
        Colour.BRIGHT_RED,
    )

    print(
        f" Result: "
        f"{pass_text} | "
        f"{warn_text} | "
        f"{fail_text}"
    )

    if counts[FAIL]:

        print(
            colour_text(
                "\n[-] Configuration has "
                "one or more failures.",
                Colour.BRIGHT_RED,
            )
        )

    elif counts[WARN]:

        print(
            colour_text(
                "\n[!] Configuration is usable, "
                "but warnings were detected.",
                Colour.BRIGHT_YELLOW,
            )
        )

    else:

        print(
            colour_text(
                "\n[+] All configuration "
                "checks passed.",
                Colour.BRIGHT_GREEN,
            )
        )


def test_configuration_menu():
    """Run and display Pivotctl diagnostics."""

    clear_screen()

    print(
        colour_text(
            "═" * 72,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                      CONFIGURATION TEST",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 72,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "\n[*] Running Pivotctl diagnostics...\n",
            Colour.BRIGHT_CYAN,
        )
    )

    try:

        results = (
            run_configuration_tests()
        )

    except Exception as exception:

        print(
            colour_text(
                f"[-] Diagnostic failure: "
                f"{exception}",
                Colour.BRIGHT_RED,
            )
        )

        pause()
        return

    for result in results:
        display_result(
            result
        )

    counts = count_results(
        results
    )

    display_summary(
        counts
    )

    pause()


if __name__ == "__main__":
    test_configuration_menu()