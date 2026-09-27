"""Profile management for Pivotctl."""

import json
import re
from copy import deepcopy
from pathlib import Path

from core.config import get_setting
from core.hosts import (
    get_managed_hosts,
    write_managed_hosts,
)
from core.proxychains import (
    add_proxy,
    get_chain_mode,
    get_proxies,
    get_proxy_dns,
    remove_proxy,
    set_chain_mode,
    set_proxy_dns,
)
from core.pivots import pivot_manager


PROFILE_VERSION = 1


def get_profiles_directory():
    """Return the configured profiles directory."""

    configured_path = get_setting(
        "paths",
        "profiles_directory",
    )

    path = Path(configured_path)

    if not path.is_absolute():
        project_root = (
            Path(__file__).resolve().parent.parent
        )

        path = project_root / path

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def validate_profile_name(name):
    """Validate a profile name."""

    if not isinstance(name, str):
        return False

    name = name.strip()

    if not name:
        return False

    return bool(
        re.fullmatch(
            r"[A-Za-z0-9._-]+",
            name,
        )
    )


def get_profile_path(name):
    """Return the path for a profile."""

    name = name.strip()

    if not validate_profile_name(name):
        raise ValueError(
            "Profile names may only contain "
            "letters, numbers, dots, "
            "underscores and hyphens."
        )

    return (
        get_profiles_directory()
        / f"{name}.json"
    )


def profile_exists(name):
    """Check whether a profile exists."""

    return get_profile_path(
        name
    ).is_file()


def list_profiles():
    """Return available profile names."""

    profiles_directory = (
        get_profiles_directory()
    )

    return sorted(
        path.stem
        for path in profiles_directory.glob(
            "*.json"
        )
        if path.is_file()
    )


def build_profile(name):
    """Build a profile from current state."""

    name = name.strip()

    if not validate_profile_name(name):
        raise ValueError(
            "Profile names may only contain "
            "letters, numbers, dots, "
            "underscores and hyphens."
        )

    return {
        "profile_version": PROFILE_VERSION,
        "name": name,
        "hosts": deepcopy(
            get_managed_hosts()
        ),
        "proxychains": {
            "chain_mode": get_chain_mode(),
            "proxy_dns": get_proxy_dns(),
            "proxies": deepcopy(
                get_proxies()
            ),
        },
        "pivots": deepcopy(
            pivot_manager.get_pivots()
        ),
    }


def save_profile(
    name,
    overwrite=False,
):
    """Save current Pivotctl state as a profile."""

    profile_path = get_profile_path(
        name
    )

    if (
        profile_path.exists()
        and not overwrite
    ):
        raise ValueError(
            f"Profile already exists: {name}"
        )

    profile = build_profile(
        name
    )

    temporary_path = (
        profile_path.with_suffix(
            ".json.tmp"
        )
    )

    try:
        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as profile_file:

            json.dump(
                profile,
                profile_file,
                indent=4,
            )

            profile_file.write("\n")

        temporary_path.replace(
            profile_path
        )

    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return profile_path


def read_profile(name):
    """Read and validate a saved profile."""

    profile_path = get_profile_path(
        name
    )

    if not profile_path.exists():
        raise ValueError(
            f"Profile does not exist: {name}"
        )

    try:
        with profile_path.open(
            "r",
            encoding="utf-8",
        ) as profile_file:

            profile = json.load(
                profile_file
            )

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid profile JSON: {name}"
        ) from error

    validate_profile(
        profile
    )

    return profile


def validate_profile(profile):
    """Validate the basic profile structure."""

    if not isinstance(
        profile,
        dict,
    ):
        raise ValueError(
            "Profile must contain "
            "a JSON object."
        )

    required_keys = {
        "profile_version",
        "name",
        "hosts",
        "proxychains",
        "pivots",
    }

    missing = (
        required_keys
        - set(profile)
    )

    if missing:
        raise ValueError(
            "Profile is missing required "
            "fields: "
            + ", ".join(
                sorted(missing)
            )
        )

    if (
        profile["profile_version"]
        != PROFILE_VERSION
    ):
        raise ValueError(
            "Unsupported profile version: "
            f"{profile['profile_version']}"
        )

    if not validate_profile_name(
        profile["name"]
    ):
        raise ValueError(
            "Invalid profile name."
        )

    if not isinstance(
        profile["hosts"],
        list,
    ):
        raise ValueError(
            "Profile hosts must be a list."
        )

    proxychains = profile[
        "proxychains"
    ]

    if not isinstance(
        proxychains,
        dict,
    ):
        raise ValueError(
            "Profile proxychains section "
            "must be an object."
        )

    proxy_keys = {
        "chain_mode",
        "proxy_dns",
        "proxies",
    }

    missing_proxy_keys = (
        proxy_keys
        - set(proxychains)
    )

    if missing_proxy_keys:
        raise ValueError(
            "ProxyChains profile section "
            "is missing fields: "
            + ", ".join(
                sorted(
                    missing_proxy_keys
                )
            )
        )

    if not isinstance(
        proxychains["proxy_dns"],
        bool,
    ):
        raise ValueError(
            "proxy_dns must be true "
            "or false."
        )

    if not isinstance(
        proxychains["proxies"],
        list,
    ):
        raise ValueError(
            "Profile proxies must be a list."
        )

    if not isinstance(
        profile["pivots"],
        list,
    ):
        raise ValueError(
            "Profile pivots must be a list."
        )

    return True


def clear_proxies():
    """Remove all currently configured proxies."""

    proxies = get_proxies()

    for index in range(
        len(proxies) - 1,
        -1,
        -1,
    ):
        remove_proxy(
            index
        )


def clear_pivots():
    """Clear the in-memory pivot topology."""

    pivot_manager.pivots.clear()


def restore_pivots(pivots):
    """Restore pivots from profile data."""

    clear_pivots()

    remaining = deepcopy(
        pivots
    )

    old_to_new_ids = {}

    while remaining:

        progress = False

        for pivot in remaining[:]:

            old_parent = pivot.get(
                "parent_id"
            )

            if (
                old_parent is not None
                and old_parent
                not in old_to_new_ids
            ):
                continue

            parent_id = None

            if old_parent is not None:
                parent_id = (
                    old_to_new_ids[
                        old_parent
                    ]
                )

            restored = (
                pivot_manager.add_pivot(
                    name=pivot["name"],
                    address=pivot["address"],
                    networks=pivot[
                        "networks"
                    ],
                    tool=pivot.get(
                        "tool",
                        "ssh",
                    ),
                    parent_id=parent_id,
                    local_port=pivot.get(
                        "local_port"
                    ),
                    notes=pivot.get(
                        "notes",
                        "",
                    ),
                )
            )

            old_to_new_ids[
                pivot["id"]
            ] = restored["id"]

            remaining.remove(
                pivot
            )

            progress = True

        if not progress:
            raise ValueError(
                "Profile contains invalid "
                "pivot parent relationships."
            )


def apply_profile(profile):
    """Apply profile state to Pivotctl."""

    validate_profile(
        profile
    )

    write_managed_hosts(
        deepcopy(
            profile["hosts"]
        )
    )

    proxychains = profile[
        "proxychains"
    ]

    set_chain_mode(
        proxychains["chain_mode"]
    )

    set_proxy_dns(
        proxychains["proxy_dns"]
    )

    clear_proxies()

    for proxy in proxychains[
        "proxies"
    ]:

        add_proxy(
            proxy["type"],
            proxy["host"],
            proxy["port"],
        )

    restore_pivots(
        profile["pivots"]
    )

    return True


def load_profile(name):
    """Load and apply a saved profile."""

    profile = read_profile(
        name
    )

    apply_profile(
        profile
    )

    return profile


def delete_profile(name):
    """Delete a saved profile."""

    profile_path = get_profile_path(
        name
    )

    if not profile_path.exists():
        raise ValueError(
            f"Profile does not exist: {name}"
        )

    profile_path.unlink()

    return profile_path


def display_profile(name):
    """Display a saved profile summary."""

    profile = read_profile(
        name
    )

    print()
    print(
        f"PROFILE: {profile['name']}"
    )

    print("-" * 70)

    print(
        f"Version     : "
        f"{profile['profile_version']}"
    )

    print(
        f"Hosts       : "
        f"{len(profile['hosts'])}"
    )

    print(
        f"Chain Mode  : "
        f"{profile['proxychains']['chain_mode']}"
    )

    proxy_dns = (
        "enabled"
        if profile[
            "proxychains"
        ]["proxy_dns"]
        else "disabled"
    )

    print(
        f"Proxy DNS   : {proxy_dns}"
    )

    print(
        f"Proxies     : "
        f"{len(profile['proxychains']['proxies'])}"
    )

    print(
        f"Pivots      : "
        f"{len(profile['pivots'])}"
    )

    print()


if __name__ == "__main__":

    profiles = list_profiles()

    print()
    print("PIVOTCTL PROFILES")
    print("-" * 50)

    if not profiles:
        print(
            "No profiles saved."
        )

    else:
        for profile_name in profiles:
            print(
                f"- {profile_name}"
            )

    print()