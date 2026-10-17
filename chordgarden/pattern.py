from dataclasses import dataclass
from math import cos, gcd, pi, sin
import random

from chordgarden.palettes import PALETTES


@dataclass(frozen=True)
class Thread:
    layer: int
    start: int
    end: int
    color: str
    opacity: float
    width: float


@dataclass(frozen=True)
class Pattern:
    title: str
    seed: int
    pins: int
    layers: int
    palette: str
    size: int
    center: float
    radius: float
    points: tuple[tuple[float, float], ...]
    threads: tuple[Thread, ...]


def generate_pattern(
    seed: int,
    pins: int = 72,
    layers: int = 4,
    palette: str = "aurora",
    title: str = "Untitled pattern",
    size: int = 900,
) -> Pattern:
    if not 16 <= pins <= 192:
        raise ValueError("Jumlah pin harus berada pada rentang 16–192.")
    if not 1 <= layers <= 8:
        raise ValueError("Jumlah lapisan harus berada pada rentang 1–8.")
    if not 500 <= size <= 1600:
        raise ValueError("Ukuran kanvas harus berada pada rentang 500–1600 piksel.")
    if palette not in PALETTES:
        choices = ", ".join(PALETTES)
        raise ValueError(f"Palet tidak dikenal: {palette}. Pilihan: {choices}")
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Judul karya tidak boleh kosong.")

    rng = random.Random(seed)
    center = size / 2
    radius = size * 0.395
    rotation = rng.random() * 2 * pi
    points = tuple(
        (
            round(center + radius * cos(rotation + 2 * pi * index / pins), 3),
            round(center + radius * sin(rotation + 2 * pi * index / pins), 3),
        )
        for index in range(pins)
    )
    multipliers = [value for value in range(2, pins) if gcd(value, pins) == 1]
    threads = []
    colors = PALETTES[palette]["threads"]
    for layer in range(layers):
        multiplier = rng.choice(multipliers)
        offset = rng.randrange(1, pins)
        pairs = {
            tuple(sorted((start, (multiplier * start + offset) % pins)))
            for start in range(pins)
            if start != (multiplier * start + offset) % pins
        }
        opacity = round(0.28 + 0.16 * (layer + 1) / layers, 3)
        width = round(max(0.45, 1.4 - layer * 0.12), 2)
        color = colors[layer % len(colors)]
        threads.extend(
            Thread(layer, start, end, color, opacity, width)
            for start, end in sorted(pairs)
        )

    return Pattern(
        title=clean_title,
        seed=seed,
        pins=pins,
        layers=layers,
        palette=palette,
        size=size,
        center=center,
        radius=radius,
        points=points,
        threads=tuple(threads),
    )
