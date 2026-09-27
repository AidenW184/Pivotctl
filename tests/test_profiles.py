"""Tests for Pivotctl profile management."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.profiles import (
    PROFILE_VERSION,
    delete_profile,
    get_profile_path,
    list_profiles,
    load_profile,
    profile_exists,
    read_profile,
    save_profile,
    validate_profile,
    validate_profile_name,
)


class ProfilesTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.profiles_dir = Path(self.temp_dir.name) / "profiles"
        self.profiles_dir.mkdir()

        self.hosts = [
            {
                "ip": "10.10.10.10",
                "hostnames": ["target.htb", "target"],
            }
        ]

        self.proxies = [
            {
                "type": "socks5",
                "host": "127.0.0.1",
                "port": 1080,
            }
        ]

        self.pivots = [
            {
                "id": 1,
                "name": "pivot01",
                "address": "10.10.10.10",
                "networks": ["172.16.10.0/24"],
                "tool": "ssh",
                "parent_id": None,
                "local_port": 1080,
                "notes": "",
            }
        ]

        self.settings_patch = patch(
            "core.profiles.get_setting",
            side_effect=self.fake_get_setting,
        )

        self.hosts_patch = patch(
            "core.profiles.get_managed_hosts",
            return_value=self.hosts,
        )

        self.chain_patch = patch(
            "core.profiles.get_chain_mode",
            return_value="strict_chain",
        )

        self.dns_patch = patch(
            "core.profiles.get_proxy_dns",
            return_value=True,
        )

        self.proxies_patch = patch(
            "core.profiles.get_proxies",
            return_value=self.proxies,
        )

        self.pivots_patch = patch(
            "core.profiles.pivot_manager.get_pivots",
            return_value=self.pivots,
        )

        self.settings_patch.start()
        self.hosts_patch.start()
        self.chain_patch.start()
        self.dns_patch.start()
        self.proxies_patch.start()
        self.pivots_patch.start()

    def tearDown(self):
        patch.stopall()
        self.temp_dir.cleanup()

    def fake_get_setting(self, section, key):
        if (section, key) == (
            "paths",
            "profiles_directory",
        ):
            return str(self.profiles_dir)

        raise KeyError(
            f"Unexpected setting: {section}.{key}"
        )

    def valid_profile(self, name="test-lab"):
        return {
            "profile_version": PROFILE_VERSION,
            "name": name,
            "hosts": self.hosts,
            "proxychains": {
                "chain_mode": "strict_chain",
                "proxy_dns": True,
                "proxies": self.proxies,
            },
            "pivots": self.pivots,
        }

    def test_validate_profile_name(self):
        self.assertTrue(
            validate_profile_name("test-lab")
        )
        self.assertTrue(
            validate_profile_name("lab_01")
        )
        self.assertTrue(
            validate_profile_name("lab.test")
        )

        self.assertFalse(
            validate_profile_name("")
        )
        self.assertFalse(
            validate_profile_name("bad profile")
        )
        self.assertFalse(
            validate_profile_name("../profile")
        )
        self.assertFalse(
            validate_profile_name(123)
        )

    def test_get_profile_path(self):
        path = get_profile_path("test-lab")

        self.assertEqual(
            path,
            self.profiles_dir / "test-lab.json",
        )

    def test_invalid_profile_name_raises(self):
        with self.assertRaises(ValueError):
            get_profile_path("../bad")

    def test_save_profile(self):
        path = save_profile("test-lab")

        self.assertTrue(path.is_file())
        self.assertTrue(
            profile_exists("test-lab")
        )

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        self.assertEqual(
            data["profile_version"],
            PROFILE_VERSION,
        )
        self.assertEqual(
            data["name"],
            "test-lab",
        )
        self.assertEqual(
            data["hosts"],
            self.hosts,
        )
        self.assertEqual(
            data["proxychains"]["proxies"],
            self.proxies,
        )
        self.assertEqual(
            data["pivots"],
            self.pivots,
        )

    def test_save_existing_profile_requires_overwrite(self):
        save_profile("test-lab")

        with self.assertRaises(ValueError):
            save_profile("test-lab")

    def test_save_profile_overwrite(self):
        save_profile("test-lab")

        path = save_profile(
            "test-lab",
            overwrite=True,
        )

        self.assertTrue(path.is_file())

    def test_list_profiles(self):
        save_profile("zulu")
        save_profile("alpha")
        save_profile("middle")

        self.assertEqual(
            list_profiles(),
            [
                "alpha",
                "middle",
                "zulu",
            ],
        )

    def test_read_profile(self):
        save_profile("test-lab")

        profile = read_profile("test-lab")

        self.assertEqual(
            profile["name"],
            "test-lab",
        )
        self.assertEqual(
            profile["hosts"],
            self.hosts,
        )

    def test_read_missing_profile_raises(self):
        with self.assertRaises(ValueError):
            read_profile("missing")

    def test_read_invalid_json_raises(self):
        path = get_profile_path("broken")

        path.write_text(
            "{ definitely not json",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            read_profile("broken")

    def test_validate_profile(self):
        self.assertTrue(
            validate_profile(
                self.valid_profile()
            )
        )

    def test_validate_profile_missing_field(self):
        profile = self.valid_profile()
        del profile["hosts"]

        with self.assertRaises(ValueError):
            validate_profile(profile)

    def test_validate_profile_wrong_version(self):
        profile = self.valid_profile()
        profile["profile_version"] = 999

        with self.assertRaises(ValueError):
            validate_profile(profile)

    def test_validate_profile_invalid_proxy_dns(self):
        profile = self.valid_profile()
        profile["proxychains"]["proxy_dns"] = "yes"

        with self.assertRaises(ValueError):
            validate_profile(profile)

    def test_validate_profile_invalid_proxies(self):
        profile = self.valid_profile()
        profile["proxychains"]["proxies"] = {}

        with self.assertRaises(ValueError):
            validate_profile(profile)

    def test_delete_profile(self):
        save_profile("test-lab")

        path = delete_profile("test-lab")

        self.assertFalse(path.exists())
        self.assertFalse(
            profile_exists("test-lab")
        )

    def test_delete_missing_profile_raises(self):
        with self.assertRaises(ValueError):
            delete_profile("missing")

    def test_load_profile_reads_and_applies_profile(self):
        profile = self.valid_profile()

        path = get_profile_path("test-lab")
        path.write_text(
            json.dumps(profile),
            encoding="utf-8",
        )

        with patch(
            "core.profiles.apply_profile",
            return_value=True,
        ) as apply_mock:

            loaded = load_profile("test-lab")

        self.assertEqual(
            loaded,
            profile,
        )

        apply_mock.assert_called_once_with(
            profile
        )


if __name__ == "__main__":
    unittest.main()