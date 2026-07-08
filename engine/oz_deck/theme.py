"""
theme.py - Tokens de charte The Oz + systeme de themes (clair / sombre).

Les couleurs de marque (orange accent, vert validation) sont invariantes.
Seul le "socle" (fond, texte, tuiles, logo) change entre les deux templates.
Reference : CHARTE_TOZ_DOCUMENTS.pdf.
"""

from __future__ import annotations
from dataclasses import dataclass
from pptx.dml.color import RGBColor


def rgb(hexstr: str) -> RGBColor:
    hexstr = hexstr.lstrip("#")
    return RGBColor(int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16))


# --- Couleurs de marque invariantes (palette 60 / 30 / 10) ---
class Brand:
    NOIR       = rgb("191919")   # dominante
    VERT       = rgb("346F53")   # validation
    ORANGE     = rgb("EC4324")   # accent
    BLANC      = rgb("FFFFFF")
    GRIS_CLAIR = rgb("F3F2F2")
    GRIS_TUILE = rgb("222222")
    GRIS_TXT   = rgb("999999")
    FILET      = rgb("E7E7E7")
    LINK       = rgb("6EA8C0")   # lien (slide de fin, facon charte)

    FONT = "Arial"               # substitution systeme d'Helvetica (charte)

    # Geometrie 16:9 (pouces)
    SW = 13.333
    SH = 7.5
    MARGIN = 0.7
    TITLE_TOP = 0.55
    FOOTER_TOP = 6.95
    FOOTER_LEFT = "THE OZ - AGENCE SHOPIFY"
    FOOTER_RIGHT = "DOCUMENT INTERNE"


@dataclass(frozen=True)
class Theme:
    """Socle visuel resolu pour un template donne."""
    name: str
    on_dark: bool
    bg: RGBColor                 # fond uni des slides de contenu
    bg_grad_a: RGBColor          # degrade cover/section/closing (debut)
    bg_grad_b: RGBColor          # degrade (fin)
    text: RGBColor               # texte principal
    text_muted: RGBColor         # labels / texte discret
    tile: RGBColor               # fond des tuiles / cartes
    tile_icon_bg: RGBColor       # fond du carre-icone
    icon_hex: str                # couleur de l'icone (monochrome)
    table_body_alt: RGBColor     # bande alternee des tableaux
    table_body_base: RGBColor    # bande de base des tableaux
    table_body_text: RGBColor
    badge_moyen: RGBColor        # badge impact "moyen"


DARK = Theme(
    name="dark",
    on_dark=True,
    bg=Brand.NOIR,
    bg_grad_a=Brand.NOIR,
    bg_grad_b=rgb("3A1E18"),
    text=Brand.BLANC,
    text_muted=Brand.GRIS_TXT,
    tile=rgb("262626"),
    tile_icon_bg=rgb("141414"),
    icon_hex="FFFFFF",
    table_body_alt=Brand.GRIS_CLAIR,
    table_body_base=Brand.BLANC,
    table_body_text=Brand.NOIR,
    badge_moyen=rgb("555555"),
)

LIGHT = Theme(
    name="light",
    on_dark=False,
    bg=Brand.GRIS_CLAIR,
    bg_grad_a=Brand.GRIS_CLAIR,
    bg_grad_b=Brand.BLANC,
    text=Brand.NOIR,
    text_muted=rgb("6B6B6B"),
    tile=Brand.BLANC,
    tile_icon_bg=Brand.GRIS_CLAIR,
    icon_hex="191919",
    table_body_alt=Brand.GRIS_CLAIR,
    table_body_base=Brand.BLANC,
    table_body_text=Brand.NOIR,
    badge_moyen=rgb("8A8A8A"),
)

THEMES = {"dark": DARK, "light": LIGHT}


def get_theme(name: str | None) -> Theme:
    return THEMES.get((name or "dark").lower(), DARK)
