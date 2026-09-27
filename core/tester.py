"""Configuration diagnostics for Pivotctl."""

import socket
from pathlib import Path

from core.config import get_setting
from core.hosts import (
    get_hosts_path,
    get_managed_hosts,
    read_hosts,
)
from core.network import (
    get_default_route,
    get_vpn_interfaces,
)
from core.pivots import pivot_manager
from core.profiles import get_profiles_directory
from core.proxychains import (
    get_chain_mode,
    get_proxies,
    get_proxy_dns,
    get_proxychains_path,
    read_proxychains,
)


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


def make_result(
    name,
    status,
    message,
):
    """Create a diagnostic result."""

    return {
        "name": name,
        "status": status,
        "message": message,
    }


def test_hosts_configuration():
    """Test the configured hosts file."""

    try:
        hosts_path = Path(
            get_hosts_path()
        )

        if not hosts_path.exists():
            return make_result(
                "Hosts configuration",
                FAIL,
                f"File not found: {hosts_path}",
            )

        read_hosts()

        hosts = get_managed_hosts()

        return make_result(
            "Hosts configuration",
            PASS,
            (
                f"{len(hosts)} managed "
                f"host entr"
                f"{'y' if len(hosts) == 1 else 'ies'}."
            ),
        )

    except (
        OSError,
        ValueError,
    ) as exception:

        return make_result(
            "Hosts configuration",
            FAIL,
            str(exception),
        )


def test_proxychains_configuration():
    """Test the configured ProxyChains file."""

    try:
        proxychains_path = Path(
            get_proxychains_path()
        )

        if not proxychains_path.exists():
            return make_result(
                "ProxyChains config",
                FAIL,
                f"File not found: {proxychains_path}",
            )

        read_proxychains()

        chain_mode = get_chain_mode()
        proxy_dns = get_proxy_dns()
        proxies = get_proxies()

        return make_result(
            "ProxyChains config",
            PASS,
            (
                f"{chain_mode}, "
                f"proxy_dns "
                f"{'enabled' if proxy_dns else 'disabled'}, "
                f"{len(proxies)} "
                f"prox"
                f"{'y' if len(proxies) == 1 else 'ies'}."
            ),
        )

    except (
        OSError,
        ValueError,
    ) as exception:

        return make_result(
            "ProxyChains config",
            FAIL,
            str(exception),
        )


def check_tcp_port(
    host,
    port,
    timeout=0.5,
):
    """Check whether a TCP port accepts a connection."""

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            return True

    except (
        OSError,
        socket.timeout,
    ):
        return False


def test_proxy_ports():
    """Test configured ProxyChains proxy ports."""

    try:
        proxies = get_proxies()

    except (
        OSError,
        ValueError,
    ) as exception:

        return [
            make_result(
                "Proxy port test",
                FAIL,
                str(exception),
            )
        ]

    if not proxies:
        return [
            make_result(
                "Proxy port test",
                WARN,
                "No proxies configured.",
            )
        ]

    results = []

    for proxy in proxies:

        host = proxy["host"]
        port = proxy["port"]
        proxy_type = proxy["type"]

        if check_tcp_port(
            host,
            port,
        ):

            results.append(
                make_result(
                    (
                        f"Proxy "
                        f"{host}:{port}"
                    ),
                    PASS,
                    (
                        f"{proxy_type} TCP "
                        f"port is accepting "
                        f"connections."
                    ),
                )
            )

        else:

            results.append(
                make_result(
                    (
                        f"Proxy "
                        f"{host}:{port}"
                    ),
                    WARN,
                    (
                        f"{proxy_type} TCP "
                        f"port is not currently "
                        f"accepting connections."
                    ),
                )
            )

    return results


def test_default_route():
    """Test whether an IPv4 default route exists."""

    try:
        route = get_default_route()

        if route is None:
            return make_result(
                "Default route",
                WARN,
                "No IPv4 default route detected.",
            )

        return make_result(
            "Default route",
            PASS,
            (
                f"{route['interface']} via "
                f"{route['gateway']} "
                f"({route['source']})."
            ),
        )

    except RuntimeError as exception:

        return make_result(
            "Default route",
            FAIL,
            str(exception),
        )


def test_vpn_status():
    """Test whether a VPN/tunnel interface is present."""

    try:
        interfaces = get_vpn_interfaces()

        if not interfaces:
            return make_result(
                "VPN / Tunnel",
                WARN,
                "No VPN or tunnel interface detected.",
            )

        names = ", ".join(
            interface["name"]
            for interface in interfaces
        )

        return make_result(
            "VPN / Tunnel",
            PASS,
            f"Detected: {names}.",
        )

    except RuntimeError as exception:

        return make_result(
            "VPN / Tunnel",
            FAIL,
            str(exception),
        )


def test_pivot_topology():
    """Validate the current in-memory pivot topology."""

    pivots = pivot_manager.get_pivots()

    if not pivots:
        return make_result(
            "Pivot topology",
            WARN,
            "No pivots currently configured.",
        )

    pivot_ids = {
        pivot["id"]
        for pivot in pivots
    }

    for pivot in pivots:

        parent_id = pivot.get(
            "parent_id"
        )

        if (
            parent_id is not None
            and parent_id not in pivot_ids
        ):
            return make_result(
                "Pivot topology",
                FAIL,
                (
                    f"Pivot {pivot['name']} "
                    f"references missing parent "
                    f"ID {parent_id}."
                ),
            )

        networks = pivot.get(
            "networks",
            []
        )

        if not networks:
            return make_result(
                "Pivot topology",
                FAIL,
                (
                    f"Pivot {pivot['name']} "
                    f"has no reachable networks."
                ),
            )

    return make_result(
        "Pivot topology",
        PASS,
        (
            f"{len(pivots)} pivot"
            f"{'' if len(pivots) == 1 else 's'} "
            f"configured."
        ),
    )


def test_profiles_directory():
    """Test the profiles directory."""

    try:
        path = get_profiles_directory()

        if not path.exists():
            return make_result(
                "Profiles directory",
                FAIL,
                f"Directory does not exist: {path}",
            )

        if not path.is_dir():
            return make_result(
                "Profiles directory",
                FAIL,
                f"Not a directory: {path}",
            )

        profiles = list(
            path.glob("*.json")
        )

        return make_result(
            "Profiles directory",
            PASS,
            (
                f"{len(profiles)} saved "
                f"profile"
                f"{'' if len(profiles) == 1 else 's'}."
            ),
        )

    except OSError as exception:

        return make_result(
            "Profiles directory",
            FAIL,
            str(exception),
        )


def test_backup_directory():
    """Test the configured backup directory."""

    try:
        configured_path = get_setting(
            "paths",
            "backups_directory",
        )

        path = Path(
            configured_path
        )

        if not path.is_absolute():

            project_root = (
                Path(__file__)
                .resolve()
                .parent
                .parent
            )

            path = (
                project_root
                / path
            )

        if not path.exists():

            return make_result(
                "Backup directory",
                WARN,
                f"Directory does not exist: {path}",
            )

        if not path.is_dir():

            return make_result(
                "Backup directory",
                FAIL,
                f"Not a directory: {path}",
            )

        backups = [
            item
            for item in path.iterdir()
            if item.is_file()
        ]

        return make_result(
            "Backup directory",
            PASS,
            (
                f"{len(backups)} backup "
                f"file"
                f"{'' if len(backups) == 1 else 's'}."
            ),
        )

    except (
        OSError,
        KeyError,
    ) as exception:

        return make_result(
            "Backup directory",
            FAIL,
            str(exception),
        )


def run_configuration_tests():
    """Run all Pivotctl configuration diagnostics."""

    results = [
        test_hosts_configuration(),
        test_proxychains_configuration(),
    ]

    results.extend(
        test_proxy_ports()
    )

    results.extend(
        [
            test_default_route(),
            test_vpn_status(),
            test_pivot_topology(),
            test_profiles_directory(),
            test_backup_directory(),
        ]
    )

    return results


def count_results(results):
    """Count PASS, WARN and FAIL results."""

    return {
        PASS: sum(
            result["status"] == PASS
            for result in results
        ),
        WARN: sum(
            result["status"] == WARN
            for result in results
        ),
        FAIL: sum(
            result["status"] == FAIL
            for result in results
        ),
    }


if __name__ == "__main__":

    results = run_configuration_tests()

    for result in results:

        print(
            f"[{result['status']}] "
            f"{result['name']}: "
            f"{result['message']}"
        )

    counts = count_results(
        results
    )

    print()
    print(
        f"PASS: {counts[PASS]} | "
        f"WARN: {counts[WARN]} | "
        f"FAIL: {counts[FAIL]}"
    )