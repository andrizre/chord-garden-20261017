from html import escape
import os
from pathlib import Path
import tempfile

from chordgarden.palettes import PALETTES
from chordgarden.pattern import Pattern


def render_svg(pattern: Pattern) -> str:
    palette = PALETTES[pattern.palette]
    title = escape(pattern.title)
    description = escape(
        f"Seni string-art dengan {pattern.pins} pin, {pattern.layers} lapisan, "
        f"seed {pattern.seed}, dan palet {pattern.palette}."
    )
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{pattern.size}" height="{pattern.size}" viewBox="0 0 {pattern.size} {pattern.size}" role="img" aria-labelledby="art-title art-description">',
        f"<title id=\"art-title\">{title}</title>",
        f'<desc id="art-description">{description}</desc>',
        f'<rect width="100%" height="100%" fill="{palette["paper"]}"/>',
        f'<text x="42" y="48" fill="{palette["ink"]}" font-family="Georgia, serif" font-size="24">{title}</text>',
        f'<text x="42" y="72" fill="{palette["ink"]}" opacity="0.72" font-family="sans-serif" font-size="12">{pattern.palette} · seed {pattern.seed} · {pattern.pins} pins · {pattern.layers} layers</text>',
        f'<circle cx="{pattern.center:.3f}" cy="{pattern.center:.3f}" r="{pattern.radius:.3f}" fill="none" stroke="{palette["ink"]}" stroke-opacity="0.18" stroke-width="1"/>',
        '<g fill="none" stroke-linecap="round">',
    ]
    for thread in pattern.threads:
        x1, y1 = pattern.points[thread.start]
        x2, y2 = pattern.points[thread.end]
        lines.append(
            f'<line data-layer="{thread.layer}" data-start="{thread.start}" data-end="{thread.end}" '
            f'x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="{thread.color}" stroke-opacity="{thread.opacity:.3f}" stroke-width="{thread.width:.2f}"/>'
        )
    lines.extend(["</g>", '<g fill="{0}" fill-opacity="0.9">'.format(palette["ink"])])
    lines.extend(
        f'<circle cx="{x:.3f}" cy="{y:.3f}" r="2.15"/>' for x, y in pattern.points
    )
    lines.extend(["</g>", "</svg>", ""])
    return "\n".join(lines)


def write_svg(path: str | Path, content: str) -> Path:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return target
