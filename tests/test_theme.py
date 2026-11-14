"""Offline checks for our package, not a replacement for Serein validation."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "catppuccin-mocha-blue.serein-extension"

# Official Mocha snapshot, palette v1.8.0:
# https://github.com/catppuccin/palette/blob/07d02aa110ef9eb7e7427afca5c73ba9cf7f8ebd/palette.json
MOCHA = {
    "rosewater": "#f5e0dc", "flamingo": "#f2cdcd", "pink": "#f5c2e7",
    "mauve": "#cba6f7", "red": "#f38ba8", "maroon": "#eba0ac",
    "peach": "#fab387", "yellow": "#f9e2af", "green": "#a6e3a1",
    "teal": "#94e2d5", "sky": "#89dceb", "sapphire": "#74c7ec",
    "blue": "#89b4fa", "lavender": "#b4befe", "text": "#cdd6f4",
    "subtext1": "#bac2de", "subtext0": "#a6adc8", "overlay2": "#9399b2",
    "overlay1": "#7f849c", "overlay0": "#6c7086", "surface2": "#585b70",
    "surface1": "#45475a", "surface0": "#313244", "base": "#1e1e2e",
    "mantle": "#181825", "crust": "#11111b",
}

ROLES = {
    "base": "crust", "sidebar": "mantle", "chat": "base",
    "raised": "surface0", "hover": "surface0", "selected": "surface0",
    "border": "surface1", "text_strong": "text", "text": "text",
    "muted": "subtext0", "link": "blue", "accent": "blue",
    "accent_text": "base", "positive": "green", "warning": "yellow",
    "danger": "red", "mention_bg": "surface0", "mention_text": "blue",
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def luminance(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in channels]
    return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background):
    low, high = sorted((luminance(foreground), luminance(background)))
    return (high + 0.05) / (low + 0.05)


class ThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"),
                                 object_pairs_hook=unique_object)

    def test_manifest_and_package_shape(self):
        self.assertEqual(set(self.package), {"manifest", "theme"})
        manifest = self.package["manifest"]
        self.assertEqual(set(manifest), {
            "api_version", "id", "name", "version", "author", "license",
            "source", "kind", "capabilities", "actions",
        })
        self.assertEqual(manifest["api_version"], 1)
        self.assertEqual(manifest["kind"], "theme")
        self.assertEqual(manifest["id"], "catppuccin-mocha-blue")
        self.assertEqual(manifest["name"], "Catppuccin")
        self.assertRegex(manifest["id"], r"^[a-z0-9][a-z0-9-]{0,63}$")
        for field in ("name", "version", "author", "license"):
            self.assertTrue(manifest[field].strip())
            self.assertLessEqual(len(manifest[field].encode("utf-8")), 128)
            self.assertFalse(any(ord(c) < 32 or ord(c) == 127
                                 for c in manifest[field]))
        self.assertEqual(manifest["license"], "MIT")
        source = manifest["source"]
        self.assertTrue(source == "" or source.startswith("https://"))

    def test_no_plugin_permissions_or_styling_changes(self):
        self.assertEqual(self.package["manifest"]["capabilities"], [])
        self.assertEqual(self.package["manifest"]["actions"], [])
        self.assertEqual(set(self.package["theme"]), {"dark", "light"})
        for mode in ("dark", "light"):
            self.assertEqual(set(self.package["theme"][mode]), {"colors"})

    def test_complete_identical_mode_maps(self):
        theme = self.package["theme"]
        self.assertEqual(theme["dark"], theme["light"])
        self.assertEqual(set(theme["dark"]["colors"]), set(ROLES))
        self.assertEqual(len(ROLES), 18)

    def test_exact_official_opaque_mocha_values(self):
        for mode in ("dark", "light"):
            for key, value in self.package["theme"][mode]["colors"].items():
                with self.subTest(mode=mode, token=key):
                    self.assertIsNotNone(re.fullmatch(r"#[0-9a-f]{6}", value))
                    self.assertIn(value, MOCHA.values())

    def test_intended_color_roles(self):
        expected = {token: MOCHA[color] for token, color in ROLES.items()}
        for mode in ("dark", "light"):
            self.assertEqual(self.package["theme"][mode]["colors"], expected)

    def test_opaque_normal_text_contrast(self):
        colors = self.package["theme"]["dark"]["colors"]
        pairs = [(foreground, background)
                 for foreground in ("text", "text_strong", "muted", "link")
                 for background in ("base", "sidebar", "chat", "raised",
                                    "hover", "selected")]
        pairs.extend([("accent_text", "accent"), ("mention_text", "mention_bg")])
        for foreground, background in pairs:
            with self.subTest(foreground=foreground, background=background):
                self.assertGreaterEqual(contrast(colors[foreground], colors[background]), 4.5)

    def test_package_size(self):
        self.assertLessEqual(PACKAGE.stat().st_size, 16 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
