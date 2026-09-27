"""Interactive Pivot Manager menu for Pivotctl."""

import os

try:
    from ui.colours import Colour, colour_text

except ModuleNotFoundError:
    from colours import Colour, colour_text

from core.config import get_setting
from core.pivots import (
    VALID_PIVOT_TOOLS,
    pivot_manager,
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


def show_pivot_summary():
    """Display the currently configured pivots."""

    pivots = pivot_manager.get_pivots()

    network_count = sum(
        len(
            pivot.get(
                "networks",
                [],
            )
        )
        for pivot in pivots
    )

    print(
        f" Current Pivots   : "
        f"{colour_text(str(len(pivots)), Colour.BRIGHT_CYAN)}"
    )

    print(
        f" Reachable Nets   : "
        f"{colour_text(str(network_count), Colour.BRIGHT_CYAN)}"
    )

    if not pivots:
        print(
            colour_text(
                "\n No pivots configured.",
                Colour.BRIGHT_YELLOW,
            )
        )
        return

    print()

    print(
        f" {'ID':<4}"
        f"{'NAME':<16}"
        f"{'ADDRESS':<20}"
        f"{'TOOL':<12}"
        f"{'PARENT':<8}"
        f"{'PORT'}"
    )

    print(
        " " + "─" * 68
    )

    for pivot in pivots:

        parent = (
            str(pivot["parent_id"])
            if pivot["parent_id"] is not None
            else "-"
        )

        port = (
            str(pivot["local_port"])
            if pivot["local_port"] is not None
            else "-"
        )

        print(
            f" {pivot['id']:<4}"
            f"{pivot['name']:<16}"
            f"{pivot['address']:<20}"
            f"{pivot['tool']:<12}"
            f"{parent:<8}"
            f"{port}"
        )


def show_pivot_menu():
    """Display the Pivot Manager menu."""

    clear_screen()

    print(
        colour_text(
            "═" * 72,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                          PIVOT MANAGER",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 72,
            Colour.BRIGHT_GREEN,
        )
    )

    print()

    show_pivot_summary()

    print(
        """
 [1] Add Pivot
 [2] Edit Pivot
 [3] Remove Pivot
 [4] Add Reachable Network
 [5] Remove Reachable Network
 [6] View Topology
 [7] View Pivot Details

 [R] Refresh
 [B] Back
"""
    )


def parse_networks(value):
    """Parse a comma-separated network list."""

    return [
        network.strip()
        for network in value.split(",")
        if network.strip()
    ]


def choose_pivot():
    """Prompt for a pivot ID."""

    pivots = pivot_manager.get_pivots()

    if not pivots:
        warning(
            "No pivots are currently configured."
        )
        return None

    value = input(
        colour_text(
            " Pivot ID > ",
            Colour.BRIGHT_GREEN,
        )
    ).strip()

    try:
        pivot_id = int(value)

        return pivot_manager.get_pivot(
            pivot_id
        )

    except ValueError as exception:
        error(
            str(exception)
        )
        return None


def add_pivot_menu():
    """Interactively add a pivot."""

    print(
        colour_text(
            "\nADD PIVOT",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    name = input(
        " Name: "
    ).strip()

    address = input(
        " Pivot IP Address: "
    ).strip()

    networks_input = input(
        " Reachable Network(s) "
        "[comma separated]: "
    ).strip()

    print(
        "\n Supported Tools: "
        + ", ".join(
            VALID_PIVOT_TOOLS
        )
    )

    tool = input(
        " Pivot Tool [ssh]: "
    ).strip().lower()

    if not tool:
        tool = "ssh"

    parent_input = input(
        " Parent Pivot ID "
        "[Enter for none]: "
    ).strip()

    parent_id = (
        parent_input
        if parent_input
        else None
    )

    port_input = input(
        " Local Port "
        "[Enter for none]: "
    ).strip()

    local_port = (
        port_input
        if port_input
        else None
    )

    notes = input(
        " Notes [optional]: "
    ).strip()

    try:
        pivot = pivot_manager.add_pivot(
            name=name,
            address=address,
            networks=parse_networks(
                networks_input
            ),
            tool=tool,
            parent_id=parent_id,
            local_port=local_port,
            notes=notes,
        )

        success(
            f"Pivot added: "
            f"{pivot['name']} "
            f"({pivot['address']})"
        )

    except ValueError as exception:
        error(
            str(exception)
        )


def edit_pivot_menu():
    """Interactively edit an existing pivot."""

    print(
        colour_text(
            "\nEDIT PIVOT",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    pivot = choose_pivot()

    if pivot is None:
        return

    print(
        "\nPress Enter to keep the current value."
    )

    name = input(
        f" Name [{pivot['name']}]: "
    ).strip()

    address = input(
        f" Address [{pivot['address']}]: "
    ).strip()

    current_networks = ", ".join(
        pivot["networks"]
    )

    networks_input = input(
        f" Networks [{current_networks}]: "
    ).strip()

    tool = input(
        f" Tool [{pivot['tool']}]: "
    ).strip().lower()

    current_parent = (
        str(pivot["parent_id"])
        if pivot["parent_id"] is not None
        else "none"
    )

    print(
        "\n Parent controls:"
        "\n   Enter = keep current"
        "\n   none  = remove parent"
        "\n   ID    = set parent"
    )

    parent_input = input(
        f" Parent [{current_parent}]: "
    ).strip()

    current_port = (
        str(pivot["local_port"])
        if pivot["local_port"] is not None
        else "none"
    )

    print(
        "\n Port controls:"
        "\n   Enter = keep current"
        "\n   none  = remove port"
        "\n   PORT  = set port"
    )

    port_input = input(
        f" Local Port [{current_port}]: "
    ).strip()

    notes = input(
        f" Notes [{pivot['notes']}]: "
    ).strip()

    changes = {}

    if name:
        changes["name"] = name

    if address:
        changes["address"] = address

    if networks_input:
        changes["networks"] = (
            parse_networks(
                networks_input
            )
        )

    if tool:
        changes["tool"] = tool

    if parent_input:

        if parent_input.lower() == "none":
            changes["parent_id"] = ""

        else:
            changes["parent_id"] = (
                parent_input
            )

    if port_input:

        if port_input.lower() == "none":
            changes["local_port"] = ""

        else:
            changes["local_port"] = (
                port_input
            )

    if notes:
        changes["notes"] = notes

    if not changes:
        info(
            "No changes requested."
        )
        return

    try:
        updated = pivot_manager.edit_pivot(
            pivot["id"],
            **changes,
        )

        success(
            f"Pivot updated: "
            f"{updated['name']}"
        )

    except ValueError as exception:
        error(
            str(exception)
        )


def remove_pivot_menu():
    """Interactively remove a pivot."""

    print(
        colour_text(
            "\nREMOVE PIVOT",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    pivot = choose_pivot()

    if pivot is None:
        return

    warning(
        f"About to remove pivot "
        f"{pivot['name']} "
        f"({pivot['address']})."
    )

    confirmation = input(
        " Confirm removal [y/N]: "
    ).strip().lower()

    if confirmation not in (
        "y",
        "yes",
    ):
        info(
            "Removal cancelled."
        )
        return

    try:
        removed = (
            pivot_manager.remove_pivot(
                pivot["id"]
            )
        )

        success(
            f"Pivot removed: "
            f"{removed['name']}"
        )

    except ValueError as exception:
        error(
            str(exception)
        )


def add_network_menu():
    """Add a reachable network to a pivot."""

    print(
        colour_text(
            "\nADD REACHABLE NETWORK",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    pivot = choose_pivot()

    if pivot is None:
        return

    network = input(
        " Network: "
    ).strip()

    try:
        added = pivot_manager.add_network(
            pivot["id"],
            network,
        )

        success(
            f"Network added to "
            f"{pivot['name']}: {added}"
        )

    except ValueError as exception:
        error(
            str(exception)
        )


def remove_network_menu():
    """Remove a reachable network from a pivot."""

    print(
        colour_text(
            "\nREMOVE REACHABLE NETWORK",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        "─" * 56
    )

    pivot = choose_pivot()

    if pivot is None:
        return

    if not pivot["networks"]:
        warning(
            f"{pivot['name']} has no "
            f"reachable networks."
        )
        return

    print(
        f"\n Networks reachable through "
        f"{pivot['name']}:"
    )

    for index, network in enumerate(
        pivot["networks"],
        start=1,
    ):
        print(
            f" [{index}] {network}"
        )

    selection = input(
        "\n Network ID: "
    ).strip()

    try:
        index = int(selection) - 1

        if (
            index < 0
            or index >= len(
                pivot["networks"]
            )
        ):
            raise IndexError

        network = pivot[
            "networks"
        ][index]

    except (
        ValueError,
        IndexError,
    ):
        error(
            "Invalid network selection."
        )
        return

    try:
        removed = (
            pivot_manager.remove_network(
                pivot["id"],
                network,
            )
        )

        success(
            f"Network removed from "
            f"{pivot['name']}: {removed}"
        )

    except ValueError as exception:
        error(
            str(exception)
        )


def view_topology_menu():
    """Display the current pivot topology."""

    clear_screen()

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                       PIVOT TOPOLOGY",
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

    pivot_manager.display_topology()


def view_pivot_details_menu():
    """Display detailed information for one pivot."""

    pivot = choose_pivot()

    if pivot is None:
        return

    clear_screen()

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    print(
        colour_text(
            "                       PIVOT DETAILS",
            Colour.BRIGHT_CYAN,
        )
    )

    print(
        colour_text(
            "═" * 64,
            Colour.BRIGHT_GREEN,
        )
    )

    parent_name = "None"

    if pivot["parent_id"] is not None:

        try:
            parent = pivot_manager.get_pivot(
                pivot["parent_id"]
            )

            parent_name = (
                f"{parent['name']} "
                f"(ID {parent['id']})"
            )

        except ValueError:
            parent_name = (
                f"Unknown "
                f"(ID {pivot['parent_id']})"
            )

    port = (
        str(pivot["local_port"])
        if pivot["local_port"] is not None
        else "None"
    )

    print(
        f"""
 ID         : {pivot['id']}
 Name       : {pivot['name']}
 Address    : {pivot['address']}
 Tool       : {pivot['tool']}
 Parent     : {parent_name}
 Local Port : {port}
 Notes      : {pivot['notes'] or 'None'}

 Reachable Networks:
"""
    )

    if pivot["networks"]:

        for network in pivot["networks"]:
            print(
                f"   - {network}"
            )

    else:
        print(
            "   None"
        )

    print()


def pivot_menu():
    """Run the interactive Pivot Manager."""

    while True:

        show_pivot_menu()

        choice = input(
            colour_text(
                " pivot/pivots > ",
                Colour.BRIGHT_GREEN,
            )
        ).strip().lower()

        if choice == "1":
            add_pivot_menu()
            pause()

        elif choice == "2":
            edit_pivot_menu()
            pause()

        elif choice == "3":
            remove_pivot_menu()
            pause()

        elif choice == "4":
            add_network_menu()
            pause()

        elif choice == "5":
            remove_network_menu()
            pause()

        elif choice == "6":
            view_topology_menu()
            pause()

        elif choice == "7":
            view_pivot_details_menu()
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


# Alias matching the naming style used by
# the other Pivotctl menu modules.
pivots_menu = pivot_menu


if __name__ == "__main__":
    pivot_menu()