import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from chordgarden.palettes import PALETTES
from chordgarden.pattern import generate_pattern
from chordgarden.svg import render_svg, write_svg

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PatternTests(unittest.TestCase):
    def test_same_seed_produces_same_geometry(self) -> None:
        first = generate_pattern(20261017, pins=80, layers=4, palette="aurora")
        second = generate_pattern(20261017, pins=80, layers=4, palette="aurora")
        self.assertEqual(first, second)

    def test_different_seeds_change_the_art(self) -> None:
        first = generate_pattern(12, pins=72, layers=3)
        second = generate_pattern(13, pins=72, layers=3)
        self.assertNotEqual(first.points, second.points)
        self.assertNotEqual(first.threads, second.threads)

    def test_points_stay_on_the_circle(self) -> None:
        pattern = generate_pattern(7, pins=32, layers=2)
        self.assertEqual(len(pattern.points), pattern.pins)
        for x, y in pattern.points:
            with self.subTest(point=(x, y)):
                distance = ((x - pattern.center) ** 2 + (y - pattern.center) ** 2) ** 0.5
                self.assertAlmostEqual(distance, pattern.radius, places=2)

    def test_each_layer_has_unique_valid_chords(self) -> None:
        pattern = generate_pattern(8, pins=48, layers=5)
        by_layer = {layer: [] for layer in range(pattern.layers)}
        for thread in pattern.threads:
            by_layer[thread.layer].append((thread.start, thread.end))
            self.assertLess(thread.start, thread.end)
            self.assertLess(thread.end, pattern.pins)
        for pairs in by_layer.values():
            self.assertGreater(len(pairs), 0)
            self.assertEqual(len(pairs), len(set(pairs)))

    def test_parameter_boundaries_and_invalid_values(self) -> None:
        for options in (
            {"pins": 15},
            {"pins": 193},
            {"layers": 0},
            {"layers": 9},
            {"size": 499},
            {"size": 1601},
            {"palette": "infrared"},
            {"title": "   "},
        ):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    generate_pattern(1, **options)

    def test_all_palettes_have_valid_colors(self) -> None:
        import re

        for name, palette in PALETTES.items():
            with self.subTest(palette=name):
                self.assertEqual(len(palette["threads"]), 5)
                for color in (palette["paper"], palette["ink"], *palette["threads"]):
                    self.assertRegex(color, re.compile(r"^#[0-9A-Fa-f]{6}$"))


class SvgTests(unittest.TestCase):
    def test_svg_is_well_formed_and_matches_pattern(self) -> None:
        pattern = generate_pattern(41, pins=40, layers=3, palette="moss", title="Garden < 1 & 2")
        content = render_svg(pattern)
        root = ET.fromstring(content)
        namespace = "{http://www.w3.org/2000/svg}"
        lines = [element for element in root.iter() if element.tag == f"{namespace}line"]
        circles = [element for element in root.iter() if element.tag == f"{namespace}circle"]
        self.assertEqual(len(lines), len(pattern.threads))
        self.assertEqual(len(circles), pattern.pins + 1)
        self.assertEqual(root.find(f"{namespace}title").text, "Garden < 1 & 2")
        self.assertIn("&lt; 1 &amp; 2", content)

    def test_atomic_file_writer_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "art.svg"
            content = render_svg(generate_pattern(91, pins=24, layers=1))
            self.assertEqual(write_svg(output, content), output)
            self.assertEqual(ET.parse(output).getroot().tag, "{http://www.w3.org/2000/svg}svg")


class CliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        return subprocess.run(
            [sys.executable, "-m", "chordgarden", *arguments],
            cwd=PROJECT_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_palette_command_lists_every_palette(self) -> None:
        result = self.run_cli("palettes")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in PALETTES:
            self.assertIn(name, result.stdout)

    def test_generate_command_writes_svg(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "chords.svg"
            result = self.run_cli(
                "generate", "--seed", "20261017", "--pins", "64", "--layers", "3",
                "--palette", "tideline", "--title", "Blue Current", "--output", str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            root = ET.parse(output).getroot()
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("Seed: 20261017", result.stdout)
            self.assertIn("Pin: 64", result.stdout)
            self.assertIn("Palet: tideline", result.stdout)

    def test_invalid_pin_count_returns_clear_error(self) -> None:
        result = self.run_cli("generate", "--pins", "8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Jumlah pin harus", result.stderr)


if __name__ == "__main__":
    unittest.main()
