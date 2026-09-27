"""Configuration management for Pivotctl."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.json"


def load_config():
    """Load and return Pivotctl configuration."""

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Pivotctl configuration file not found: {CONFIG_PATH}"
        )

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            return json.load(config_file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in configuration file: {error}"
        ) from error


def get_setting(section, key):
    """Return a setting from a configuration section."""

    config = load_config()

    if section not in config:
        raise KeyError(
            f"Configuration section not found: {section}"
        )

    if key not in config[section]:
        raise KeyError(
            f"Configuration setting not found: {section}.{key}"
        )

    return config[section][key]


if __name__ == "__main__":
    config = load_config()

    print("Pivotctl configuration loaded successfully.")
    print(f"Application: {config['application']['name']}")
    print(f"Version:     {config['application']['version']}")