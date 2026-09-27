"""ProxyChains configuration management for Pivotctl."""

import ipaddress
from pathlib import Path

from core.backup import create_backup
from core.config import get_setting


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VALID_CHAIN_MODES = (
    "dynamic_chain",
    "strict_chain",
    "round_robin_chain",
    "random_chain",
)

VALID_PROXY_TYPES = (
    "socks4",
    "socks5",
    "http",
)


def get_proxychains_path():
    """Return the configured ProxyChains file path."""

    configured_path = Path(
        get_setting("paths", "proxychains_file")
    )

    if configured_path.is_absolute():
        return configured_path

    return PROJECT_ROOT / configured_path


def read_proxychains(proxychains_path=None):
    """Read and return the ProxyChains configuration."""

    if proxychains_path is None:
        proxychains_path = get_proxychains_path()

    proxychains_path = Path(proxychains_path)

    if not proxychains_path.exists():
        raise FileNotFoundError(
            f"ProxyChains file does not exist: {proxychains_path}"
        )

    if not proxychains_path.is_file():
        raise ValueError(
            f"ProxyChains path is not a file: {proxychains_path}"
        )

    return proxychains_path.read_text(
        encoding="utf-8"
    )


def write_proxychains(contents, proxychains_path=None):
    """Safely write ProxyChains configuration."""

    if proxychains_path is None:
        proxychains_path = get_proxychains_path()

    proxychains_path = Path(proxychains_path)

    if not proxychains_path.exists():
        raise FileNotFoundError(
            f"ProxyChains file does not exist: {proxychains_path}"
        )

    original_contents = read_proxychains(
        proxychains_path
    )

    if contents == original_contents:
        return None

    backup_path = None

    if get_setting(
        "proxychains",
        "backup_before_write"
    ):
        backup_path = create_backup(
            proxychains_path
        )

    proxychains_path.write_text(
        contents,
        encoding="utf-8"
    )

    return backup_path


def get_chain_mode(proxychains_path=None):
    """Return the currently active chain mode."""

    contents = read_proxychains(
        proxychains_path
    )

    active_modes = []

    for line in contents.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        directive = stripped.split(
            "#",
            1
        )[0].strip()

        if directive in VALID_CHAIN_MODES:
            active_modes.append(directive)

    if not active_modes:
        return None

    if len(active_modes) > 1:
        raise ValueError(
            "Multiple active ProxyChains "
            "chain modes detected."
        )

    return active_modes[0]


def set_chain_mode(mode, proxychains_path=None):
    """Set the active ProxyChains chain mode."""

    mode = mode.strip().lower()

    if mode not in VALID_CHAIN_MODES:
        raise ValueError(
            f"Unsupported chain mode: {mode}"
        )

    contents = read_proxychains(
        proxychains_path
    )

    lines = contents.splitlines(
        keepends=True
    )

    found_modes = set()
    new_lines = []

    for line in lines:

        newline = "\n" if line.endswith("\n") else ""
        body = line.rstrip("\r\n")
        stripped = body.strip()

        matched_mode = None

        for chain_mode in VALID_CHAIN_MODES:

            if stripped == chain_mode:
                matched_mode = chain_mode
                break

            if stripped == f"#{chain_mode}":
                matched_mode = chain_mode
                break

            if stripped == f"# {chain_mode}":
                matched_mode = chain_mode
                break

        if matched_mode is None:
            new_lines.append(line)
            continue

        found_modes.add(matched_mode)

        if matched_mode == mode:
            new_lines.append(
                f"{mode}{newline}"
            )
        else:
            new_lines.append(
                f"#{matched_mode}{newline}"
            )

    if mode not in found_modes:
        raise ValueError(
            f"Chain directive not found "
            f"in configuration: {mode}"
        )

    new_contents = "".join(
        new_lines
    )

    return write_proxychains(
        new_contents,
        proxychains_path
    )


def get_proxy_dns(proxychains_path=None):
    """Return True if proxy_dns is enabled."""

    contents = read_proxychains(
        proxychains_path
    )

    for line in contents.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        directive = stripped.split(
            "#",
            1
        )[0].strip()

        if directive == "proxy_dns":
            return True

    return False


def set_proxy_dns(enabled, proxychains_path=None):
    """Enable or disable proxy_dns."""

    if not isinstance(enabled, bool):
        raise TypeError(
            "proxy_dns state must be True or False."
        )

    contents = read_proxychains(
        proxychains_path
    )

    lines = contents.splitlines(
        keepends=True
    )

    found = False
    new_lines = []

    for line in lines:

        newline = "\n" if line.endswith("\n") else ""
        body = line.rstrip("\r\n")
        stripped = body.strip()

        if stripped in (
            "proxy_dns",
            "#proxy_dns",
            "# proxy_dns",
        ):
            found = True

            if enabled:
                new_lines.append(
                    f"proxy_dns{newline}"
                )
            else:
                new_lines.append(
                    f"#proxy_dns{newline}"
                )

            continue

        new_lines.append(line)

    if not found:
        raise ValueError(
            "proxy_dns directive not found "
            "in configuration."
        )

    new_contents = "".join(
        new_lines
    )

    return write_proxychains(
        new_contents,
        proxychains_path
    )


def toggle_proxy_dns(proxychains_path=None):
    """Toggle the proxy_dns setting."""

    current_state = get_proxy_dns(
        proxychains_path
    )

    backup_path = set_proxy_dns(
        not current_state,
        proxychains_path
    )

    return not current_state, backup_path


def validate_proxy_type(proxy_type):
    """Validate a supported ProxyChains proxy type."""

    if not isinstance(proxy_type, str):
        return False

    return (
        proxy_type.strip().lower()
        in VALID_PROXY_TYPES
    )


def validate_proxy_host(host):
    """Validate a proxy hostname or IP address."""

    if not isinstance(host, str):
        return False

    host = host.strip()

    if not host:
        return False

    try:
        ipaddress.ip_address(host)
        return True

    except ValueError:
        pass

    if len(host) > 253:
        return False

    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789.-_"
    )

    return all(
        character in allowed
        for character in host
    )


def validate_proxy_port(port):
    """Validate a TCP port number."""

    try:
        port = int(port)

    except (TypeError, ValueError):
        return False

    return 1 <= port <= 65535


def validate_proxy(
    proxy_type,
    host,
    port
):
    """Validate a ProxyChains proxy entry."""

    proxy_type = proxy_type.strip().lower()
    host = host.strip()

    if not validate_proxy_type(
        proxy_type
    ):
        raise ValueError(
            f"Unsupported proxy type: {proxy_type}"
        )

    if not validate_proxy_host(
        host
    ):
        raise ValueError(
            f"Invalid proxy host: {host}"
        )

    if not validate_proxy_port(
        port
    ):
        raise ValueError(
            f"Invalid proxy port: {port}"
        )

    return {
        "type": proxy_type,
        "host": host,
        "port": int(port),
    }


def get_proxylist_index(lines):
    """Return the line index of [ProxyList]."""

    for index, line in enumerate(lines):

        if line.strip().lower() == "[proxylist]":
            return index

    raise ValueError(
        "[ProxyList] section not found."
    )


def get_proxies(proxychains_path=None):
    """Return active entries from [ProxyList]."""

    contents = read_proxychains(
        proxychains_path
    )

    lines = contents.splitlines()

    proxylist_index = get_proxylist_index(
        lines
    )

    proxies = []

    for line in lines[
        proxylist_index + 1:
    ]:

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            continue

        entry = stripped.split(
            "#",
            1
        )[0].strip()

        parts = entry.split()

        if len(parts) < 3:
            continue

        proxy_type = parts[0].lower()

        if proxy_type not in VALID_PROXY_TYPES:
            continue

        try:
            port = int(parts[2])

        except ValueError:
            continue

        proxy = {
            "type": proxy_type,
            "host": parts[1],
            "port": port,
        }

        if len(parts) >= 5:
            proxy["username"] = parts[3]
            proxy["password"] = parts[4]

        proxies.append(proxy)

    return proxies


def build_proxy_line(proxy):
    """Build a ProxyChains proxy-list line."""

    line = (
        f"{proxy['type']}\t"
        f"{proxy['host']}\t"
        f"{proxy['port']}"
    )

    if (
        proxy.get("username") is not None
        and proxy.get("password") is not None
    ):
        line += (
            f"\t{proxy['username']}"
            f"\t{proxy['password']}"
        )

    return line


def add_proxy(
    proxy_type,
    host,
    port,
    proxychains_path=None
):
    """Add a proxy to [ProxyList]."""

    proxy = validate_proxy(
        proxy_type,
        host,
        port
    )

    existing_proxies = get_proxies(
        proxychains_path
    )

    for existing in existing_proxies:

        if (
            existing["type"] == proxy["type"]
            and existing["host"] == proxy["host"]
            and existing["port"] == proxy["port"]
        ):
            raise ValueError(
                "Proxy already exists."
            )

    contents = read_proxychains(
        proxychains_path
    )

    lines = contents.splitlines(
        keepends=True
    )

    get_proxylist_index(lines)

    if contents and not contents.endswith("\n"):
        contents += "\n"

    contents += (
        build_proxy_line(proxy)
        + "\n"
    )

    return write_proxychains(
        contents,
        proxychains_path
    )


def remove_proxy(
    index,
    proxychains_path=None
):
    """Remove an active proxy by zero-based index."""

    proxies = get_proxies(
        proxychains_path
    )

    if not proxies:
        raise ValueError(
            "No active proxies exist."
        )

    if index < 0 or index >= len(proxies):
        raise IndexError(
            "Proxy index is out of range."
        )

    target = proxies[index]

    contents = read_proxychains(
        proxychains_path
    )

    lines = contents.splitlines(
        keepends=True
    )

    proxylist_index = get_proxylist_index(
        lines
    )

    active_index = -1
    new_lines = []
    removed = False

    for line_index, line in enumerate(lines):

        if line_index <= proxylist_index:
            new_lines.append(line)
            continue

        stripped = line.strip()

        if (
            not stripped
            or stripped.startswith("#")
        ):
            new_lines.append(line)
            continue

        entry = stripped.split(
            "#",
            1
        )[0].strip()

        parts = entry.split()

        if (
            len(parts) >= 3
            and parts[0].lower()
            in VALID_PROXY_TYPES
        ):
            active_index += 1

            if active_index == index:
                removed = True
                continue

        new_lines.append(line)

    if not removed:
        raise ValueError(
            "Proxy could not be located "
            "in configuration."
        )

    backup_path = write_proxychains(
        "".join(new_lines),
        proxychains_path
    )

    return target, backup_path


def edit_proxy(
    index,
    proxy_type,
    host,
    port,
    proxychains_path=None
):
    """Edit an active proxy by zero-based index."""

    replacement = validate_proxy(
        proxy_type,
        host,
        port
    )

    proxies = get_proxies(
        proxychains_path
    )

    if index < 0 or index >= len(proxies):
        raise IndexError(
            "Proxy index is out of range."
        )

    for current_index, existing in enumerate(
        proxies
    ):
        if current_index == index:
            continue

        if (
            existing["type"] == replacement["type"]
            and existing["host"] == replacement["host"]
            and existing["port"] == replacement["port"]
        ):
            raise ValueError(
                "Proxy already exists."
            )

    old_proxy = proxies[index]

    contents = read_proxychains(
        proxychains_path
    )

    lines = contents.splitlines(
        keepends=True
    )

    proxylist_index = get_proxylist_index(
        lines
    )

    active_index = -1
    new_lines = []
    edited = False

    for line_index, line in enumerate(lines):

        if line_index <= proxylist_index:
            new_lines.append(line)
            continue

        stripped = line.strip()

        if (
            not stripped
            or stripped.startswith("#")
        ):
            new_lines.append(line)
            continue

        entry = stripped.split(
            "#",
            1
        )[0].strip()

        parts = entry.split()

        if (
            len(parts) >= 3
            and parts[0].lower()
            in VALID_PROXY_TYPES
        ):
            active_index += 1

            if active_index == index:

                newline = (
                    "\n"
                    if line.endswith("\n")
                    else ""
                )

                new_lines.append(
                    build_proxy_line(
                        replacement
                    )
                    + newline
                )

                edited = True
                continue

        new_lines.append(line)

    if not edited:
        raise ValueError(
            "Proxy could not be located "
            "in configuration."
        )

    backup_path = write_proxychains(
        "".join(new_lines),
        proxychains_path
    )

    return old_proxy, backup_path


def display_proxychains_status(
    proxychains_path=None
):
    """Display current ProxyChains configuration."""

    chain_mode = get_chain_mode(
        proxychains_path
    )

    proxy_dns = get_proxy_dns(
        proxychains_path
    )

    proxies = get_proxies(
        proxychains_path
    )

    print()
    print("PROXYCHAINS STATUS")
    print("-" * 70)

    print(
        f"Chain Mode : "
        f"{chain_mode or 'Not configured'}"
    )

    print(
        f"Proxy DNS  : "
        f"{'Enabled' if proxy_dns else 'Disabled'}"
    )

    print()

    print(
        f"{'ID':<6}"
        f"{'TYPE':<12}"
        f"{'HOST':<30}"
        f"{'PORT'}"
    )

    print("-" * 70)

    if not proxies:
        print("No active proxies.")
        print()
        return

    for index, proxy in enumerate(
        proxies,
        start=1
    ):
        print(
            f"{index:<6}"
            f"{proxy['type']:<12}"
            f"{proxy['host']:<30}"
            f"{proxy['port']}"
        )

    print()


if __name__ == "__main__":

    try:
        print(
            f"ProxyChains file: "
            f"{get_proxychains_path()}"
        )

        display_proxychains_status()

    except (
        FileNotFoundError,
        ValueError,
        TypeError,
        IndexError,
        PermissionError
    ) as error:
        print(
            f"[!] {error}"
        )
        