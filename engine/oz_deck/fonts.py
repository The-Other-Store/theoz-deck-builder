"""
fonts.py - Acces aux fontes de la charte, pour les consommateurs hors PowerPoint.

Le moteur embarque deja Quicksand dans le .pptx (voir fontembed.py). Un
consommateur qui rend un AUTRE format - un rapport PDF via WeasyPrint, une page
web - a besoin des memes fichiers, au meme endroit, sans les recopier.

Ce module expose donc les deux fontes STATIQUES et leur licence a un chemin
stable, resolu a l'execution :

    from oz_deck import fonts
    fonts.files()["regular"]   # .../assets/fonts/Quicksand-Regular.ttf
    print(fonts.css_font_face())

Licence : SIL Open Font License 1.1 (OFL). Le texte de licence est livre a cote
des fichiers (`OFL.txt`) et DOIT accompagner toute redistribution.

Les statiques sont generees hors runtime depuis la fonte variable par
`dev/fonts/build_fonts.py`.
"""

from __future__ import annotations
import os

FONT_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")

# Graisse -> nom de fichier. La charte n'utilise que ces deux graisses :
# Bold pour les titres, Regular pour le corps.
FILES = {
    "regular": "Quicksand-Regular.ttf",
    "bold": "Quicksand-Bold.ttf",
}
LICENCE_FILE = "OFL.txt"
LICENCE = "SIL Open Font License 1.1"
FAMILY = "Quicksand"
WEIGHTS = {"regular": 400, "bold": 700}


def files() -> dict[str, str]:
    """Chemins ABSOLUS des fontes et de leur licence, resolus a l'execution."""
    out = {k: os.path.join(FONT_DIR, v) for k, v in FILES.items()}
    out["licence"] = os.path.join(FONT_DIR, LICENCE_FILE)
    return out


def available() -> bool:
    """Vrai si les deux graisses ET la licence sont presentes."""
    return all(os.path.exists(p) for p in files().values())


def css_font_face(base_url: str | None = None) -> str:
    """Bloc `@font-face` pret a coller devant les tokens CSS de la charte.

    `base_url` prefixe les `src:` ; sans lui, les chemins absolus du paquet sont
    utilises, ce que WeasyPrint accepte directement (il lit le systeme de
    fichiers). Pour un rendu web, passer l'URL publique du dossier de fontes.
    """
    resolved = files()
    blocks = [f"/* {FAMILY} - {LICENCE}. Redistribuer {LICENCE_FILE} avec les fontes. */"]
    for weight, number in WEIGHTS.items():
        src = (f"{base_url.rstrip('/')}/{FILES[weight]}" if base_url
               else resolved[weight])
        blocks.append(
            "@font-face {\n"
            f"  font-family: '{FAMILY}';\n"
            f"  src: url('{src}') format('truetype');\n"
            f"  font-weight: {number};\n"
            "  font-style: normal;\n"
            "}"
        )
    return "\n".join(blocks) + "\n"
