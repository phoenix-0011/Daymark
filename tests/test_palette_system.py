from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_PATH = ROOT / "daymark" / "theme.py"


def _theme_constants_and_palettes():
    module = ast.parse(THEME_PATH.read_text(encoding="utf-8"))
    constants: dict[str, str] = {}
    palette_node = None
    for node in module.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value.value, str):
                    constants[target.id] = node.value.value
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "PALETTES"
        ):
            palette_node = node.value
    if palette_node is None:
        raise AssertionError("PALETTES was not found")

    class ReplaceNames(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in constants:
                return ast.copy_location(ast.Constant(constants[node.id]), node)
            return node

    return ast.literal_eval(ReplaceNames().visit(palette_node))


def _luminance(color: str) -> float:
    values = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in values
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class PaletteSystemTests(unittest.TestCase):
    def setUp(self):
        self.palettes = _theme_constants_and_palettes()

    def test_three_complete_palettes_exist(self):
        self.assertEqual(
            set(self.palettes),
            {"warm_sage", "sky_blue", "aristocratic_green"},
        )
        for modes in self.palettes.values():
            self.assertEqual(set(modes), {"light", "dark"})

    def test_every_palette_has_all_semantic_roles(self):
        required = {
            "window", "sidebar", "surface", "surface_alt", "surface_hover",
            "text", "muted", "faint", "border", "accent", "accent_hover",
            "accent_pressed", "accent_soft", "on_accent", "danger",
            "danger_soft", "on_danger", "overlay",
            *(f"category_{index}" for index in range(1, 7)),
        }
        hex_pattern = re.compile(r"^#[0-9A-F]{6}$")
        for name, modes in self.palettes.items():
            for mode, colors in modes.items():
                self.assertTrue(required.issubset(colors), f"{name}/{mode}")
                for role in required:
                    self.assertRegex(colors[role], hex_pattern, f"{name}/{mode}/{role}")

    def test_core_text_contrast_is_readable(self):
        for name, modes in self.palettes.items():
            for mode, colors in modes.items():
                self.assertGreaterEqual(
                    _contrast(colors["text"], colors["window"]), 7.0,
                    f"primary text {name}/{mode}",
                )
                self.assertGreaterEqual(
                    _contrast(colors["muted"], colors["window"]), 4.5,
                    f"muted text {name}/{mode}",
                )
                self.assertGreaterEqual(
                    _contrast(colors["on_accent"], colors["accent"]), 4.5,
                    f"accent foreground {name}/{mode}",
                )
                self.assertGreaterEqual(
                    _contrast(colors["on_danger"], colors["danger"]), 4.5,
                    f"danger foreground {name}/{mode}",
                )

    def test_settings_and_persistence_hooks_exist(self):
        window = (ROOT / "daymark" / "window.py").read_text(encoding="utf-8")
        dialogs = (ROOT / "daymark" / "dialogs.py").read_text(encoding="utf-8")
        i18n = (ROOT / "daymark" / "i18n.py").read_text(encoding="utf-8")
        self.assertIn('self.settings.value("colorPalette"', window)
        self.assertIn('self.settings.setValue("colorPalette"', window)
        self.assertIn("palette_changer=self.change_palette", window)
        self.assertIn("self.palette_select = SoftSelect()", dialogs)
        for key in ("palette_warm_sage", "palette_sky_blue", "palette_aristocratic_green"):
            self.assertIn(f'"{key}"', i18n)


if __name__ == "__main__":
    unittest.main()
