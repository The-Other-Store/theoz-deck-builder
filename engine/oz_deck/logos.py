"""
logos.py - Acces aux logos officiels, pour les consommateurs hors PowerPoint.

Symetrique de `fonts.py`. Sans ce module, un consommateur n'a d'autre choix que
de coder en dur `assets/logo_principal_orange.png` : le jour ou un fichier est
renomme, son rendu casse silencieusement.

    from oz_deck import logos
    logos.path("secondaire", logos.for_background(dark=False))
    logos.files()["principal-blanc"]

Regles de charte portees ici, pas dans l'appelant :

  - Le logo est EXCLUSIVEMENT orange (#EC4324) ou blanc monochrome.
    **Le noir est banni.** Aucun fichier noir n'existe, et il ne faut pas en
    fabriquer un par recoloration.
  - Sur fond clair : version ORANGE. Sur fond sombre ou sur le degrade des pages
    evenementielles : version BLANCHE. `for_background()` tranche.
  - Logo PRINCIPAL (badge + wordmark) : couvertures de rapport et slides phares.
    Logo SECONDAIRE (badge seul) : en-tetes, pieds de page, zones de donnees
    denses.
  - Zone de protection : ne rien adosser a une distance inferieure a la hauteur
    totale du badge circulaire (`PROTECTION_RATIO`).

Les PNG officiels comportent une marge TRANSPARENTE a gauche. Pour un ferrage a
gauche exact, il faut la compenser : c'est `INK_LEFT`, sinon le logo parait
rentre par rapport au texte et aux filets.
"""

from __future__ import annotations
import os

LOGO_DIR = os.path.join(os.path.dirname(__file__), "assets")

# type de logo -> variante -> nom de fichier. Aucune variante noire : bannie.
FILES = {
    "principal": {"orange": "logo_principal_orange.png",
                  "blanc": "logo_principal_blanc.png"},
    "secondaire": {"orange": "logo_secondaire_orange.png",
                   "blanc": "logo_secondaire_blanc.png"},
}

# Rapport largeur / hauteur de chaque PNG officiel.
RATIO = {"principal": 1.0, "secondaire": 1500 / 1364}

# Fraction de marge TRANSPARENTE a gauche, a compenser pour un ferrage exact.
INK_LEFT = {"principal": 0.0813, "secondaire": 0.0100}

# Zone de protection : multiple de la hauteur du logo a laisser libre autour.
PROTECTION_RATIO = 1.0

VARIANTS = ("orange", "blanc")
KINDS = tuple(FILES)


def for_background(dark: bool) -> str:
    """Variante imposee par la charte pour un fond donne.

    `dark=True` couvre le fond sombre ET le degrade orange des pages
    evenementielles : dans les deux cas, le logo est blanc.
    """
    return "blanc" if dark else "orange"


def path(kind: str = "secondaire", variant: str = "orange") -> str:
    """Chemin ABSOLU d'un logo, resolu a l'execution."""
    if kind not in FILES:
        raise ValueError(f"type de logo inconnu : {kind!r} (attendu {KINDS})")
    if variant not in FILES[kind]:
        raise ValueError(f"variante inconnue : {variant!r} (attendu {VARIANTS} ; "
                         "le noir est banni par la charte)")
    return os.path.join(LOGO_DIR, FILES[kind][variant])


def files() -> dict[str, str]:
    """Chemins ABSOLUS de tous les logos, clefs `<type>-<variante>`."""
    return {f"{kind}-{variant}": os.path.join(LOGO_DIR, name)
            for kind, variants in FILES.items()
            for variant, name in variants.items()}


def available() -> bool:
    """Vrai si les quatre PNG officiels sont presents."""
    return all(os.path.exists(p) for p in files().values())


def width_for_height(kind: str, height: float) -> float:
    """Largeur a donner a un logo pour une hauteur voulue (meme unite)."""
    return height * RATIO.get(kind, 1.0)


def ink_offset(kind: str, width: float) -> float:
    """Decalage a RETRANCHER a l'abscisse pour que l'encre tombe sur la marge."""
    return INK_LEFT.get(kind, 0.0) * width
