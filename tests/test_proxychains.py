"""Tests for Pivotctl ProxyChains management."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.proxychains import (
    add_proxy,
    build_proxy_line,
    edit_proxy,
    get_chain_mode,
    get_proxies,
    get_proxy_dns,
    remove_proxy,
    set_chain_mode,
    set_proxy_dns,
    toggle_proxy_dns,
    validate_proxy,
    validate_proxy_host,
    validate_proxy_port,
    validate_proxy_type,
)


BASE_CONFIG = """# Pivotctl ProxyChains test configuration

strict_chain
#dynamic_chain
#round_robin_chain
#random_chain

proxy_dns

[ProxyList]
# test proxies below
"""


class ProxyChainsTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.proxychains_path = (
            Path(self.temp_dir.name) / "proxychains.conf"
        )

        self.proxychains_path.write_text(
            BASE_CONFIG,
            encoding="utf-8",
        )

        self.settings = {
            ("proxychains", "backup_before_write"): False,
        }

        self.setting_patch = patch(
            "core.proxychains.get_setting",
            side_effect=lambda section, key: self.settings[(section, key)],
        )

        self.setting_patch.start()

    def tearDown(self):
        self.setting_patch.stop()
        self.temp_dir.cleanup()

    def test_get_chain_mode(self):
        self.assertEqual(
            get_chain_mode(self.proxychains_path),
            "strict_chain",
        )

    def test_set_chain_mode(self):
        set_chain_mode(
            "dynamic_chain",
            self.proxychains_path,
        )

        self.assertEqual(
            get_chain_mode(self.proxychains_path),
            "dynamic_chain",
        )

        contents = self.proxychains_path.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "\ndynamic_chain\n",
            contents,
        )

        self.assertIn(
            "\n#strict_chain\n",
            contents,
        )

    def test_invalid_chain_mode_raises(self):
        with self.assertRaises(ValueError):
            set_chain_mode(
                "banana_chain",
                self.proxychains_path,
            )

    def test_get_proxy_dns_enabled(self):
        self.assertTrue(
            get_proxy_dns(self.proxychains_path)
        )

    def test_set_proxy_dns_disabled(self):
        set_proxy_dns(
            False,
            self.proxychains_path,
        )

        self.assertFalse(
            get_proxy_dns(self.proxychains_path)
        )

    def test_set_proxy_dns_enabled(self):
        set_proxy_dns(
            False,
            self.proxychains_path,
        )

        set_proxy_dns(
            True,
            self.proxychains_path,
        )

        self.assertTrue(
            get_proxy_dns(self.proxychains_path)
        )

    def test_toggle_proxy_dns(self):
        new_state, _ = toggle_proxy_dns(
            self.proxychains_path
        )

        self.assertFalse(new_state)
        self.assertFalse(
            get_proxy_dns(self.proxychains_path)
        )

        new_state, _ = toggle_proxy_dns(
            self.proxychains_path
        )

        self.assertTrue(new_state)
        self.assertTrue(
            get_proxy_dns(self.proxychains_path)
        )

    def test_set_proxy_dns_rejects_non_boolean(self):
        with self.assertRaises(TypeError):
            set_proxy_dns(
                "yes",
                self.proxychains_path,
            )

    def test_validate_proxy_type(self):
        self.assertTrue(
            validate_proxy_type("socks4")
        )
        self.assertTrue(
            validate_proxy_type("socks5")
        )
        self.assertTrue(
            validate_proxy_type("http")
        )

        self.assertFalse(
            validate_proxy_type("https")
        )
        self.assertFalse(
            validate_proxy_type(123)
        )

    def test_validate_proxy_host(self):
        self.assertTrue(
            validate_proxy_host("127.0.0.1")
        )
        self.assertTrue(
            validate_proxy_host("10.10.10.10")
        )
        self.assertTrue(
            validate_proxy_host("proxy.example.htb")
        )

        self.assertFalse(
            validate_proxy_host("")
        )
        self.assertFalse(
            validate_proxy_host("bad host!")
        )
        self.assertFalse(
            validate_proxy_host(123)
        )

    def test_validate_proxy_port(self):
        self.assertTrue(
            validate_proxy_port(1080)
        )
        self.assertTrue(
            validate_proxy_port("9050")
        )

        self.assertFalse(
            validate_proxy_port(0)
        )
        self.assertFalse(
            validate_proxy_port(65536)
        )
        self.assertFalse(
            validate_proxy_port("banana")
        )

    def test_validate_proxy(self):
        proxy = validate_proxy(
            "SOCKS5",
            "127.0.0.1",
            "1080",
        )

        self.assertEqual(
            proxy,
            {
                "type": "socks5",
                "host": "127.0.0.1",
                "port": 1080,
            },
        )

    def test_validate_proxy_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            validate_proxy(
                "https",
                "127.0.0.1",
                1080,
            )

        with self.assertRaises(ValueError):
            validate_proxy(
                "socks5",
                "bad host!",
                1080,
            )

        with self.assertRaises(ValueError):
            validate_proxy(
                "socks5",
                "127.0.0.1",
                70000,
            )

    def test_build_proxy_line(self):
        line = build_proxy_line(
            {
                "type": "socks5",
                "host": "127.0.0.1",
                "port": 1080,
            }
        )

        self.assertEqual(
            line,
            "socks5\t127.0.0.1\t1080",
        )

    def test_get_proxies_empty(self):
        self.assertEqual(
            get_proxies(self.proxychains_path),
            [],
        )

    def test_add_proxy(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        self.assertEqual(
            get_proxies(self.proxychains_path),
            [
                {
                    "type": "socks5",
                    "host": "127.0.0.1",
                    "port": 1080,
                }
            ],
        )

    def test_add_multiple_proxies(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        add_proxy(
            "http",
            "10.10.10.10",
            8080,
            self.proxychains_path,
        )

        proxies = get_proxies(
            self.proxychains_path
        )

        self.assertEqual(
            len(proxies),
            2,
        )

        self.assertEqual(
            proxies[1],
            {
                "type": "http",
                "host": "10.10.10.10",
                "port": 8080,
            },
        )

    def test_duplicate_proxy_raises(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        with self.assertRaises(ValueError):
            add_proxy(
                "socks5",
                "127.0.0.1",
                1080,
                self.proxychains_path,
            )

    def test_remove_proxy(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        removed, _ = remove_proxy(
            0,
            self.proxychains_path,
        )

        self.assertEqual(
            removed,
            {
                "type": "socks5",
                "host": "127.0.0.1",
                "port": 1080,
            },
        )

        self.assertEqual(
            get_proxies(self.proxychains_path),
            [],
        )

    def test_remove_proxy_invalid_index(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        with self.assertRaises(IndexError):
            remove_proxy(
                1,
                self.proxychains_path,
            )

    def test_remove_proxy_when_empty(self):
        with self.assertRaises(ValueError):
            remove_proxy(
                0,
                self.proxychains_path,
            )

    def test_edit_proxy(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        old_proxy, _ = edit_proxy(
            0,
            "http",
            "10.10.10.10",
            8080,
            self.proxychains_path,
        )

        self.assertEqual(
            old_proxy,
            {
                "type": "socks5",
                "host": "127.0.0.1",
                "port": 1080,
            },
        )

        self.assertEqual(
            get_proxies(self.proxychains_path),
            [
                {
                    "type": "http",
                    "host": "10.10.10.10",
                    "port": 8080,
                }
            ],
        )

    def test_edit_proxy_invalid_index(self):
        with self.assertRaises(IndexError):
            edit_proxy(
                0,
                "socks5",
                "127.0.0.1",
                1080,
                self.proxychains_path,
            )

    def test_edit_proxy_duplicate_raises(self):
        add_proxy(
            "socks5",
            "127.0.0.1",
            1080,
            self.proxychains_path,
        )

        add_proxy(
            "http",
            "10.10.10.10",
            8080,
            self.proxychains_path,
        )

        with self.assertRaises(ValueError):
            edit_proxy(
                0,
                "http",
                "10.10.10.10",
                8080,
                self.proxychains_path,
            )


if __name__ == "__main__":
    unittest.main()