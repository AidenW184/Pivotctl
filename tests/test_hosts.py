"""Tests for Pivotctl hosts management."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.hosts import (
    add_host,
    edit_host,
    get_managed_hosts,
    normalise_hostnames,
    parse_hosts,
    remove_host,
    remove_hostname,
    replace_managed_block,
    validate_hostname,
    validate_ip,
)


START_MARKER = "# >>> PIVOTCTL MANAGED HOSTS >>>"
END_MARKER = "# <<< PIVOTCTL MANAGED HOSTS <<<"


class HostsTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.hosts_path = Path(self.temp_dir.name) / "hosts"

        self.hosts_path.write_text(
            "127.0.0.1 localhost\n"
            "127.0.1.1 test-machine\n",
            encoding="utf-8",
        )

        self.settings = {
            ("hosts", "managed_block_start"): START_MARKER,
            ("hosts", "managed_block_end"): END_MARKER,
            ("hosts", "backup_before_write"): False,
        }

        self.setting_patch = patch(
            "core.hosts.get_setting",
            side_effect=lambda section, key: self.settings[(section, key)],
        )

        self.setting_patch.start()

    def tearDown(self):
        self.setting_patch.stop()
        self.temp_dir.cleanup()

    def test_validate_ip(self):
        self.assertTrue(validate_ip("10.10.10.10"))
        self.assertTrue(validate_ip("2001:db8::1"))
        self.assertFalse(validate_ip("999.999.999.999"))
        self.assertFalse(validate_ip("not-an-ip"))

    def test_validate_hostname(self):
        self.assertTrue(validate_hostname("dc01"))
        self.assertTrue(validate_hostname("dc01.example.htb"))
        self.assertTrue(validate_hostname("example.htb."))

        self.assertFalse(validate_hostname(""))
        self.assertFalse(validate_hostname("-invalid.htb"))
        self.assertFalse(validate_hostname("invalid_.htb"))

    def test_normalise_hostnames(self):
        result = normalise_hostnames(
            [
                "dc01.example.htb",
                "dc01",
                "dc01.example.htb",
            ]
        )

        self.assertEqual(
            result,
            [
                "dc01.example.htb",
                "dc01",
            ],
        )

    def test_normalise_hostnames_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            normalise_hostnames(["valid.htb", "bad_hostname"])

        with self.assertRaises(TypeError):
            normalise_hostnames(123)

    def test_parse_hosts(self):
        entries = parse_hosts(self.hosts_path)

        self.assertEqual(len(entries), 2)

        self.assertEqual(
            entries[0],
            {
                "ip": "127.0.0.1",
                "hostnames": ["localhost"],
            },
        )

    def test_add_host_creates_managed_block(self):
        add_host(
            "10.10.10.10",
            ["target.htb", "target"],
            self.hosts_path,
        )

        entries = get_managed_hosts(self.hosts_path)

        self.assertEqual(
            entries,
            [
                {
                    "ip": "10.10.10.10",
                    "hostnames": [
                        "target.htb",
                        "target",
                    ],
                }
            ],
        )

        contents = self.hosts_path.read_text(encoding="utf-8")

        self.assertIn(START_MARKER, contents)
        self.assertIn(END_MARKER, contents)

    def test_add_host_merges_hostnames_for_existing_ip(self):
        add_host(
            "10.10.10.10",
            "target.htb",
            self.hosts_path,
        )

        add_host(
            "10.10.10.10",
            "target",
            self.hosts_path,
        )

        entries = get_managed_hosts(self.hosts_path)

        self.assertEqual(
            entries[0]["hostnames"],
            [
                "target.htb",
                "target",
            ],
        )

    def test_add_duplicate_hostname_raises(self):
        add_host(
            "10.10.10.10",
            "target.htb",
            self.hosts_path,
        )

        with self.assertRaises(ValueError):
            add_host(
                "10.10.10.10",
                "target.htb",
                self.hosts_path,
            )

    def test_remove_host(self):
        add_host(
            "10.10.10.10",
            "target.htb",
            self.hosts_path,
        )

        removed, _ = remove_host(
            0,
            self.hosts_path,
        )

        self.assertEqual(
            removed["ip"],
            "10.10.10.10",
        )

        self.assertEqual(
            get_managed_hosts(self.hosts_path),
            [],
        )

    def test_remove_hostname(self):
        add_host(
            "10.10.10.10",
            [
                "target.htb",
                "target",
            ],
            self.hosts_path,
        )

        remove_hostname(
            0,
            "target",
            self.hosts_path,
        )

        entries = get_managed_hosts(self.hosts_path)

        self.assertEqual(
            entries[0]["hostnames"],
            ["target.htb"],
        )

    def test_remove_final_hostname_removes_entry(self):
        add_host(
            "10.10.10.10",
            "target.htb",
            self.hosts_path,
        )

        remove_hostname(
            0,
            "target.htb",
            self.hosts_path,
        )

        self.assertEqual(
            get_managed_hosts(self.hosts_path),
            [],
        )

    def test_edit_host(self):
        add_host(
            "10.10.10.10",
            "old.htb",
            self.hosts_path,
        )

        old_entry, _ = edit_host(
            0,
            "10.10.10.20",
            ["new.htb", "new"],
            self.hosts_path,
        )

        self.assertEqual(
            old_entry,
            {
                "ip": "10.10.10.10",
                "hostnames": ["old.htb"],
            },
        )

        entries = get_managed_hosts(self.hosts_path)

        self.assertEqual(
            entries,
            [
                {
                    "ip": "10.10.10.20",
                    "hostnames": [
                        "new.htb",
                        "new",
                    ],
                }
            ],
        )

    def test_invalid_host_index_raises(self):
        add_host(
            "10.10.10.10",
            "target.htb",
            self.hosts_path,
        )

        with self.assertRaises(IndexError):
            remove_host(
                1,
                self.hosts_path,
            )

    def test_replace_managed_block_rejects_malformed_markers(self):
        malformed = (
            "127.0.0.1 localhost\n"
            f"{START_MARKER}\n"
            "10.10.10.10 target.htb\n"
        )

        with self.assertRaises(ValueError):
            replace_managed_block(
                malformed,
                [],
            )


if __name__ == "__main__":
    unittest.main()