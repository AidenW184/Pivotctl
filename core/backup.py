"""Backup and restore management for Pivotctl."""

from datetime import datetime
from pathlib import Path
import shutil

from core.config import get_setting


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_backup_directory():
    """Return the configured Pivotctl backup directory."""

    configured_path = Path(
        get_setting("paths", "backups_directory")
    )

    if configured_path.is_absolute():
        backup_directory = configured_path
    else:
        backup_directory = PROJECT_ROOT / configured_path

    backup_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return backup_directory


def create_backup(source_path):
    """Create a timestamped backup of a file."""

    source_path = Path(source_path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Cannot backup missing file: {source_path}"
        )

    if not source_path.is_file():
        raise ValueError(
            f"Backup source is not a file: {source_path}"
        )

    backup_directory = get_backup_directory()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    backup_name = (
        f"{source_path.name}.{timestamp}.bak"
    )

    backup_path = backup_directory / backup_name

    shutil.copy2(
        source_path,
        backup_path
    )

    return backup_path


def list_backups(filename=None):
    """Return available backups, newest first."""

    backup_directory = get_backup_directory()

    if filename:
        pattern = f"{filename}.*.bak"
    else:
        pattern = "*.bak"

    backups = list(
        backup_directory.glob(pattern)
    )

    return sorted(
        backups,
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )


def get_latest_backup(filename):
    """Return the newest backup for a filename."""

    backups = list_backups(filename)

    if not backups:
        return None

    return backups[0]


def restore_backup(backup_path, destination_path):
    """Restore a backup to a destination file."""

    backup_path = Path(backup_path)
    destination_path = Path(destination_path)

    backup_directory = get_backup_directory().resolve()

    if not backup_path.exists():
        raise FileNotFoundError(
            f"Backup does not exist: {backup_path}"
        )

    if not backup_path.is_file():
        raise ValueError(
            f"Backup path is not a file: {backup_path}"
        )

    # Only allow files from Pivotctl's backup directory.
    try:
        backup_path.resolve().relative_to(
            backup_directory
        )

    except ValueError as error:
        raise ValueError(
            "Refusing to restore a file outside "
            "the Pivotctl backup directory."
        ) from error

    # Preserve the current destination before restoring
    # over an existing file.
    safety_backup = None

    if destination_path.exists():
        if not destination_path.is_file():
            raise ValueError(
                f"Restore destination is not a file: "
                f"{destination_path}"
            )

        safety_backup = create_backup(
            destination_path
        )

    shutil.copy2(
        backup_path,
        destination_path
    )

    return safety_backup


def display_backups(filename=None):
    """Display available backups."""

    backups = list_backups(filename)

    print()
    print("PIVOTCTL BACKUPS")
    print("-" * 80)

    if not backups:
        print("No backups found.")
        print()
        return

    print(
        f"{'FILE':<50}"
        f"{'SIZE':>12}"
    )

    print("-" * 80)

    for backup in backups:
        size = backup.stat().st_size

        print(
            f"{backup.name:<50}"
            f"{size:>12} bytes"
        )

    print()


if __name__ == "__main__":
    try:
        display_backups()

    except (
        FileNotFoundError,
        ValueError,
        PermissionError
    ) as error:
        print(f"[!] {error}")