import argparse
from pathlib import Path
import secrets

from chordgarden.palettes import PALETTES
from chordgarden.pattern import generate_pattern
from chordgarden.svg import render_svg, write_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chord-garden",
        description="Buat seni string-art geometris yang dapat diulang sebagai SVG.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("palettes", help="daftar palet warna bawaan")

    generate = commands.add_parser("generate", help="hasilkan pola string-art SVG")
    generate.add_argument("--seed", type=int, help="seed untuk membuat karya yang sama")
    generate.add_argument("--pins", type=int, default=72, help="jumlah pin, 16–192")
    generate.add_argument("--layers", type=int, default=4, help="lapisan tali, 1–8")
    generate.add_argument("--palette", choices=tuple(PALETTES), default="aurora")
    generate.add_argument("--title", default="Untitled pattern", help="judul karya")
    generate.add_argument("--output", type=Path, help="lokasi SVG; nama otomatis bila kosong")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "palettes":
        for name, palette in PALETTES.items():
            print(f"{name:12} {palette['description']}")
        return

    seed = args.seed if args.seed is not None else secrets.randbits(32)
    try:
        pattern = generate_pattern(seed, args.pins, args.layers, args.palette, args.title)
        output = args.output or Path(f"chord-garden-{args.palette}-{seed}.svg")
        saved = write_svg(output, render_svg(pattern))
    except (OSError, ValueError) as error:
        parser.exit(2, f"chord-garden: error: {error}\n")
    print(f"Karya tersimpan: {saved}")
    print(
        f"Seed: {seed} | Pin: {pattern.pins} | Lapisan: {pattern.layers} | "
        f"Palet: {pattern.palette} | Garis: {len(pattern.threads)}"
    )
