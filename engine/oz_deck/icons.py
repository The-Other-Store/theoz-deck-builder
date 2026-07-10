"""
icons.py - Icones Lucide (lucide.dev) rendues en PNG teinte a la charte.

Les vrais SVG Lucide sont pre-rasterises hors runtime en PNG maitres (trait
blanc, fond transparent) dans assets/icons/ via dev/icons/build_icons.sh. Au
runtime, icon_png() charge le maitre et le teinte a la couleur demandee avec
Pillow uniquement (aucune dependance SVG). L'orange est reserve aux
frictions/anomalies.

API stable : icon_png(name, color=(r,g,b,a), px) -> chemin PNG.
Pour ajouter des icones : editer dev/icons/icons.txt puis relancer build_icons.sh.
"""

from __future__ import annotations
import os
import tempfile
from PIL import Image

_CACHE: dict = {}
_ICON_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")

# Alias : noms herites / conviviaux -> nom de fichier maitre (canonique Lucide).
# Conserves pour ne pas casser les plans existants apres les renommages Lucide.
_ALIASES = {
    "bar-chart-3": "chart-column",
    "line-chart": "chart-line",
    "pie-chart": "chart-pie",
    "check-circle-2": "circle-check-big",
    "alert-triangle": "triangle-alert",
    "filter": "funnel",
}


def _masters() -> list[str]:
    if not os.path.isdir(_ICON_DIR):
        return []
    return sorted(f[:-4] for f in os.listdir(_ICON_DIR) if f.endswith(".png"))


# Icones utilisables dans les plans : fichiers maitres + alias herites.
AVAILABLE = sorted(set(_masters()) | set(_ALIASES))


def _master_path(name: str) -> str | None:
    fname = _ALIASES.get(name, name)
    path = os.path.join(_ICON_DIR, fname + ".png")
    return path if os.path.exists(path) else None


def icon_png(name: str, color=(255, 255, 255, 255), px: int = 240) -> str:
    """Rend l'icone `name` teintee a `color` (RGBA), en PNG de `px` de cote."""
    color = tuple(int(c) for c in color)
    if len(color) == 3:
        color = color + (255,)
    key = (name, color, px)
    if key in _CACHE and os.path.exists(_CACHE[key]):
        return _CACHE[key]

    master = _master_path(name)
    if master is not None:
        im = Image.open(master).convert("RGBA")
        alpha = im.getchannel("A")
        if color[3] != 255:
            alpha = alpha.point(lambda a: a * color[3] // 255)
        tinted = Image.new("RGBA", im.size, (color[0], color[1], color[2], 0))
        tinted.putalpha(alpha)
        im = tinted.resize((px, px), Image.LANCZOS)
    else:
        # Repli : icone manquante -> pastille neutre, le rendu ne casse jamais.
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(im).ellipse([px * 0.36, px * 0.36, px * 0.64, px * 0.64],
                                   fill=(color[0], color[1], color[2], color[3]))

    path = os.path.join(tempfile.gettempdir(),
                        f"ozicon_{_ALIASES.get(name, name)}_{color[0]}{color[1]}{color[2]}{color[3]}_{px}.png")
    im.save(path)
    _CACHE[key] = path
    return path


def hex_to_rgba(hexstr: str):
    hexstr = hexstr.lstrip("#")
    return (int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16), 255)
