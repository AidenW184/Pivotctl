"""Hosts file management for Pivotctl."""

import ipaddress
import re
from pathlib import Path

from core.backup import create_backup
from core.config import get_setting


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_hosts_path():
    """Return the configured hosts file path."""

    configured_path = Path(
        get_setting("paths", "hosts_file")
    )

    if configured_path.is_absolute():
        return configured_path

    return PROJECT_ROOT / configured_path


def get_managed_markers():
    """Return Pivotctl managed-block markers."""

    start_marker = get_setting(
        "hosts",
        "managed_block_start"
    )

    end_marker = get_setting(
        "hosts",
        "managed_block_end"
    )

    return start_marker, end_marker


def read_hosts(hosts_path=None):
    """Read and return raw hosts file contents."""

    if hosts_path is None:
        hosts_path = get_hosts_path()

    hosts_path = Path(hosts_path)

    if not hosts_path.exists():
        raise FileNotFoundError(
            f"Hosts file does not exist: {hosts_path}"
        )

    if not hosts_path.is_file():
        raise ValueError(
            f"Hosts path is not a file: {hosts_path}"
        )

    return hosts_path.read_text(
        encoding="utf-8"
    )


def parse_hosts(hosts_path=None):
    """Parse all hosts entries into structured data."""

    contents = read_hosts(hosts_path)
    entries = []

    for line in contents.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        line = line.split("#", 1)[0].strip()
        parts = line.split()

        if len(parts) < 2:
            continue

        entries.append({
            "ip": parts[0],
            "hostnames": parts[1:]
        })

    return entries


def validate_ip(ip_address):
    """Validate an IPv4 or IPv6 address."""

    try:
        ipaddress.ip_address(ip_address)
        return True

    except ValueError:
        return False


def validate_hostname(hostname):
    """Validate a hostname or FQDN."""

    if not isinstance(hostname, str):
        return False

    hostname = hostname.strip()

    if not hostname:
        return False

    if len(hostname) > 253:
        return False

    hostname = hostname.rstrip(".")

    labels = hostname.split(".")

    label_pattern = re.compile(
        r"^[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
    )

    return all(
        label_pattern.fullmatch(label)
        for label in labels
    )


def normalise_hostnames(hostnames):
    """
    Convert hostname input into a validated list.

    Accepts:
        "example.htb"

    Or:
        [
            "example.htb",
            "dc01.example.htb",
            "dc01"
        ]
    """

    if isinstance(hostnames, str):
        hostnames = [hostnames]

    elif isinstance(hostnames, (list, tuple, set)):
        hostnames = list(hostnames)

    else:
        raise TypeError(
            "Hostnames must be a string or "
            "a list/tuple/set of strings."
        )

    cleaned_hostnames = []

    for hostname in hostnames:

        if not isinstance(hostname, str):
            raise ValueError(
                f"Invalid hostname: {hostname}"
            )

        hostname = hostname.strip().rstrip(".")

        if not validate_hostname(hostname):
            raise ValueError(
                f"Invalid hostname: {hostname}"
            )

        if hostname not in cleaned_hostnames:
            cleaned_hostnames.append(hostname)

    if not cleaned_hostnames:
        raise ValueError(
            "At least one hostname is required."
        )

    return cleaned_hostnames


def validate_host_entry(ip_address, hostnames):
    """Validate an IP address and one or more hostnames."""

    if not validate_ip(ip_address):
        raise ValueError(
            f"Invalid IP address: {ip_address}"
        )

    return normalise_hostnames(hostnames)


def get_managed_hosts(hosts_path=None):
    """Return entries inside the Pivotctl managed block."""

    contents = read_hosts(hosts_path)

    start_marker, end_marker = get_managed_markers()

    lines = contents.splitlines()

    inside_block = False
    entries = []

    for line in lines:

        stripped = line.strip()

        if stripped == start_marker:
            inside_block = True
            continue

        if stripped == end_marker:
            inside_block = False
            break

        if not inside_block:
            continue

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        entry_line = stripped.split(
            "#",
            1
        )[0].strip()

        parts = entry_line.split()

        if len(parts) < 2:
            continue

        entries.append({
            "ip": parts[0],
            "hostnames": parts[1:]
        })

    return entries


def build_managed_block(entries):
    """Build the Pivotctl managed hosts block."""

    start_marker, end_marker = get_managed_markers()

    lines = [start_marker]

    for entry in entries:

        ip_address = entry["ip"]

        hostnames = " ".join(
            entry["hostnames"]
        )

        lines.append(
            f"{ip_address}\t{hostnames}"
        )

    lines.append(end_marker)

    return "\n".join(lines)


def replace_managed_block(contents, entries):
    """Replace or create the Pivotctl managed block."""

    start_marker, end_marker = get_managed_markers()

    new_block = build_managed_block(entries)

    start_count = contents.count(start_marker)
    end_count = contents.count(end_marker)

    if start_count != end_count:
        raise ValueError(
            "Malformed Pivotctl managed block: "
            "start/end markers do not match."
        )

    if start_count > 1:
        raise ValueError(
            "Multiple Pivotctl managed blocks detected."
        )

    if start_count == 0:

        if contents and not contents.endswith("\n"):
            contents += "\n"

        if contents:
            contents += "\n"

        return contents + new_block + "\n"

    start_index = contents.index(
        start_marker
    )

    end_index = contents.index(
        end_marker,
        start_index
    )

    end_index += len(
        end_marker
    )

    before = contents[:start_index]
    after = contents[end_index:]

    return (
        before
        + new_block
        + after
    )


def write_managed_hosts(entries, hosts_path=None):
    """Write Pivotctl-managed hosts entries."""

    if hosts_path is None:
        hosts_path = get_hosts_path()

    hosts_path = Path(hosts_path)

    if not hosts_path.exists():
        raise FileNotFoundError(
            f"Hosts file does not exist: {hosts_path}"
        )

    validated_entries = []

    for entry in entries:

        ip_address = entry["ip"]

        hostnames = validate_host_entry(
            ip_address,
            entry["hostnames"]
        )

        validated_entries.append({
            "ip": ip_address,
            "hostnames": hostnames
        })

    original_contents = read_hosts(
        hosts_path
    )

    new_contents = replace_managed_block(
        original_contents,
        validated_entries
    )

    if new_contents == original_contents:
        return None

    backup_enabled = get_setting(
        "hosts",
        "backup_before_write"
    )

    backup_path = None

    if backup_enabled:
        backup_path = create_backup(
            hosts_path
        )

    hosts_path.write_text(
        new_contents,
        encoding="utf-8"
    )

    return backup_path


def add_host(
    ip_address,
    hostnames,
    hosts_path=None
):
    """
    Add one or more hostnames.

    If the IP already exists inside the Pivotctl
    managed block, new hostnames are merged into
    the existing entry.
    """

    hostnames = validate_host_entry(
        ip_address,
        hostnames
    )

    entries = get_managed_hosts(
        hosts_path
    )

    for entry in entries:

        if entry["ip"] != ip_address:
            continue

        new_hostnames = [
            hostname
            for hostname in hostnames
            if hostname not in entry["hostnames"]
        ]

        if not new_hostnames:
            raise ValueError(
                "All supplied hostnames already exist "
                f"for {ip_address}."
            )

        entry["hostnames"].extend(
            new_hostnames
        )

        return write_managed_hosts(
            entries,
            hosts_path
        )

    entries.append({
        "ip": ip_address,
        "hostnames": hostnames
    })

    return write_managed_hosts(
        entries,
        hosts_path
    )


def remove_host(index, hosts_path=None):
    """Remove an entire managed host entry by index."""

    entries = get_managed_hosts(
        hosts_path
    )

    if not entries:
        raise ValueError(
            "No Pivotctl managed hosts exist."
        )

    if index < 0 or index >= len(entries):
        raise IndexError(
            "Host index is out of range."
        )

    removed_entry = entries.pop(
        index
    )

    backup_path = write_managed_hosts(
        entries,
        hosts_path
    )

    return removed_entry, backup_path


def remove_hostname(
    index,
    hostname,
    hosts_path=None
):
    """
    Remove one hostname from a managed entry.

    If the final hostname is removed, the entire
    IP entry is removed.
    """

    entries = get_managed_hosts(
        hosts_path
    )

    if index < 0 or index >= len(entries):
        raise IndexError(
            "Host index is out of range."
        )

    hostname = hostname.strip().rstrip(".")

    entry = entries[index]

    if hostname not in entry["hostnames"]:
        raise ValueError(
            f"Hostname does not exist: {hostname}"
        )

    entry["hostnames"].remove(
        hostname
    )

    if not entry["hostnames"]:
        entries.pop(index)

    backup_path = write_managed_hosts(
        entries,
        hosts_path
    )

    return backup_path


def edit_host(
    index,
    ip_address,
    hostnames,
    hosts_path=None
):
    """Edit an entire managed host entry by index."""

    hostnames = validate_host_entry(
        ip_address,
        hostnames
    )

    entries = get_managed_hosts(
        hosts_path
    )

    if index < 0 or index >= len(entries):
        raise IndexError(
            "Host index is out of range."
        )

    old_entry = {
        "ip": entries[index]["ip"],
        "hostnames": list(
            entries[index]["hostnames"]
        )
    }

    for current_index, entry in enumerate(
        entries
    ):

        if current_index == index:
            continue

        if entry["ip"] != ip_address:
            continue

        merged_hostnames = list(
            entry["hostnames"]
        )

        for hostname in hostnames:

            if hostname not in merged_hostnames:
                merged_hostnames.append(
                    hostname
                )

        entry["hostnames"] = merged_hostnames

        entries.pop(index)

        backup_path = write_managed_hosts(
            entries,
            hosts_path
        )

        return old_entry, backup_path

    entries[index] = {
        "ip": ip_address,
        "hostnames": hostnames
    }

    backup_path = write_managed_hosts(
        entries,
        hosts_path
    )

    return old_entry, backup_path


def display_parsed_hosts(hosts_path=None):
    """Display all parsed hosts entries."""

    entries = parse_hosts(
        hosts_path
    )

    print()
    print(
        "ADDRESS              HOSTNAME(S)"
    )
    print("-" * 65)

    for entry in entries:

        hostnames = ", ".join(
            entry["hostnames"]
        )

        print(
            f"{entry['ip']:<20} "
            f"{hostnames}"
        )

    print()


def display_managed_hosts(hosts_path=None):
    """Display Pivotctl-managed hosts entries."""

    entries = get_managed_hosts(
        hosts_path
    )

    print()
    print(
        "PIVOTCTL MANAGED HOSTS"
    )
    print("-" * 75)

    if not entries:
        print(
            "No managed hosts."
        )
        print()
        return

    print(
        f"{'ID':<6}"
        f"{'ADDRESS':<20}"
        f"{'HOSTNAME(S)'}"
    )

    print("-" * 75)

    for index, entry in enumerate(
        entries,
        start=1
    ):

        hostnames = ", ".join(
            entry["hostnames"]
        )

        print(
            f"{index:<6}"
            f"{entry['ip']:<20}"
            f"{hostnames}"
        )

    print()


if __name__ == "__main__":

    try:

        print(
            f"Hosts file: "
            f"{get_hosts_path()}"
        )

        display_managed_hosts()

    except (
        FileNotFoundError,
        ValueError,
        TypeError,
        PermissionError
    ) as error:

        print(
            f"[!] {error}"
        )