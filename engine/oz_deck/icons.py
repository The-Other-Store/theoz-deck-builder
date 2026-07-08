"""
icons.py - Icones facon Lucide (outline monochrome), rendues en PNG via PIL.

Charte : trace geometrique fin, epaisseur constante, monochrome. L'orange est
reserve aux frictions/anomalies. En prod, remplacer par les vrais SVG Lucide
rendus en PNG ; l'API (nom -> chemin PNG) reste identique.
"""

from __future__ import annotations
import os
import tempfile
from PIL import Image, ImageDraw

_CACHE: dict = {}

AVAILABLE = [
    "trending-up", "bar-chart-3", "line-chart", "pie-chart", "percent",
    "users", "circle-dollar-sign", "search", "shopping-cart", "check-circle-2",
    "alert-triangle", "smartphone", "mail", "globe", "clock", "sparkles",
]


def icon_png(name: str, color=(255, 255, 255, 255), px: int = 240) -> str:
    key = (name, color, px)
    if key in _CACHE and os.path.exists(_CACHE[key]):
        return _CACHE[key]
    S = px * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = int(S * 0.055)
    m = S * 0.18

    def line(pts):
        d.line(pts, fill=color, width=w, joint="curve")
        for x, y in pts:
            d.ellipse([x - w/2, y - w/2, x + w/2, y + w/2], fill=color)

    def circle(bbox):
        d.ellipse(bbox, outline=color, width=w)

    if name == "trending-up":
        line([(m, S*0.68), (S*0.42, S*0.42), (S*0.58, S*0.55), (S-m, S*0.30)])
        line([(S*0.70, S*0.30), (S-m, S*0.30), (S-m, S*0.52)])
    elif name == "bar-chart-3":
        for i, h in enumerate([0.30, 0.55, 0.42]):
            x = m + i * (S - 2*m) / 2.6
            d.rectangle([x, S-m-(S-2*m)*h, x + (S-2*m)*0.22, S-m], outline=color, width=w)
    elif name == "line-chart":
        line([(m, m), (m, S-m), (S-m, S-m)])
        line([(m*1.4, S*0.62), (S*0.42, S*0.40), (S*0.60, S*0.52), (S-m*1.2, S*0.28)])
    elif name == "pie-chart":
        circle([m, m, S-m, S-m])
        line([(S*0.5, S*0.5), (S*0.5, m)])
        line([(S*0.5, S*0.5), (S-m, S*0.5)])
    elif name == "percent":
        line([(m, S-m), (S-m, m)])
        circle([m, m, m + S*0.24, m + S*0.24])
        circle([S-m - S*0.24, S-m - S*0.24, S-m, S-m])
    elif name == "users":
        circle([m, S*0.16, m + S*0.30, S*0.16 + S*0.30])
        line([(m*0.8, S-m), (m*0.8, S*0.66), (m + S*0.34, S*0.66), (m + S*0.34, S-m)])
        circle([S*0.52, S*0.20, S*0.52 + S*0.26, S*0.20 + S*0.26])
    elif name == "circle-dollar-sign":
        circle([m, m, S-m, S-m])
        line([(S*0.5, S*0.26), (S*0.5, S*0.74)])
        line([(S*0.62, S*0.38), (S*0.42, S*0.38), (S*0.42, S*0.5),
              (S*0.58, S*0.5), (S*0.58, S*0.62), (S*0.38, S*0.62)])
    elif name == "search":
        circle([m, m, S*0.62, S*0.62])
        line([(S*0.57, S*0.57), (S-m, S-m)])
    elif name == "shopping-cart":
        line([(m, m), (S*0.28, m), (S*0.40, S*0.64), (S-m, S*0.64),
              (S-m*1.3, S*0.30), (S*0.30, S*0.30)])
        d.ellipse([S*0.42, S-m - S*0.10, S*0.42 + S*0.10, S-m], fill=color)
        d.ellipse([S*0.72, S-m - S*0.10, S*0.72 + S*0.10, S-m], fill=color)
    elif name == "check-circle-2":
        circle([m, m, S-m, S-m])
        line([(S*0.33, S*0.52), (S*0.45, S*0.64), (S*0.68, S*0.38)])
    elif name == "alert-triangle":
        line([(S*0.5, m), (S-m, S-m), (m, S-m), (S*0.5, m)])
        line([(S*0.5, S*0.42), (S*0.5, S*0.62)])
        d.ellipse([S*0.5 - w, S*0.70, S*0.5 + w, S*0.70 + 2*w], fill=color)
    elif name == "smartphone":
        d.rounded_rectangle([S*0.32, m, S*0.68, S-m], radius=S*0.05, outline=color, width=w)
        line([(S*0.45, S-m*1.3), (S*0.55, S-m*1.3)])
    elif name == "mail":
        d.rounded_rectangle([m, S*0.26, S-m, S*0.74], radius=S*0.03, outline=color, width=w)
        line([(m, S*0.30), (S*0.5, S*0.54), (S-m, S*0.30)])
    elif name == "globe":
        circle([m, m, S-m, S-m])
        d.ellipse([S*0.32, m, S*0.68, S-m], outline=color, width=w)
        line([(m, S*0.5), (S-m, S*0.5)])
    elif name == "clock":
        circle([m, m, S-m, S-m])
        line([(S*0.5, S*0.30), (S*0.5, S*0.5), (S*0.66, S*0.58)])
    elif name == "sparkles":
        cx, cy, r = S*0.42, S*0.42, S*0.22
        line([(cx, cy-r), (cx, cy+r)]); line([(cx-r, cy), (cx+r, cy)])
        line([(cx-r*0.7, cy-r*0.7), (cx+r*0.7, cy+r*0.7)])
        line([(cx-r*0.7, cy+r*0.7), (cx+r*0.7, cy-r*0.7)])
    else:
        d.ellipse([S*0.36, S*0.36, S*0.64, S*0.64], fill=color)

    im = im.resize((px, px), Image.LANCZOS)
    path = os.path.join(tempfile.gettempdir(),
                        f"ozicon_{name}_{color[0]}{color[1]}{color[2]}.png")
    im.save(path)
    _CACHE[key] = path
    return path


def hex_to_rgba(hexstr: str):
    hexstr = hexstr.lstrip("#")
    return (int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16), 255)
