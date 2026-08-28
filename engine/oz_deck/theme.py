"""
theme.py - Tokens de la charte The Oz V2 (CHARTE_TOZ_DOCUMENTS_V2).

La charte V2 definit UN SEUL systeme visuel, plus deux templates :
  - slides d'analyse & contenu : fond uni exclusivement BLANC ;
  - slides evenementielles (couverture, chapitre, fin) : fond uni ORANGE.

Ce fichier est la source de verite unique : palettes, echelle typographique,
espacements (regle 2:1) et geometrie. Le moteur (engine.py) et le generateur de
masque (dev/master/build_template.py) n'y ajoutent aucune couleur.
"""

from __future__ import annotations
from dataclasses import dataclass
from pptx.dml.color import RGBColor

# Version de la CHARTE appliquee par le moteur. Distincte de la version du paquet
# (`oz_deck.__version__`) : le moteur peut evoluer sans que la charte bouge, et
# inversement. Propagee a trois endroits, pour qu'un livrable soit toujours
# rattachable a une charte precise :
#   - l'export de tokens (`python -m oz_deck.theme --export ...`) ;
#   - la reponse de l'API distante (champ `charte_version`) ;
#   - les proprietes personnalisees du .pptx (`OzCharteVersion`, voir docprops.py).
# 2.x = charte V2 (CHARTE_TOZ_DOCUMENTS_V2) ; le mineur suit les revisions de
# relecture appliquees a cette charte.
CHARTE_VERSION = "2.2.0"


def rgb(hexstr: str) -> RGBColor:
    hexstr = hexstr.lstrip("#")
    return RGBColor(int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16))


def luminance(color: RGBColor) -> float:
    """Luminance relative approchee (0 = noir, 1 = blanc)."""
    r, g, b = color[0] / 255, color[1] / 255, color[2] / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


class Brand:
    # --- Palette principale (charte p.6) ---
    NOIR    = rgb("191919")   # textes principaux, titres de tableaux, fonds de titre
    VERT    = rgb("3E9356")   # vert sauge : chiffres positifs, dynamisme
    ORANGE  = rgb("EC4324")   # couleur identitaire : accents + fonds evenementiels
    RUBIS   = rgb("D3122A")   # impact : alerte, metriques negatives ou en echec
    GRIS    = rgb("999999")   # informations secondaires (legendes, sous-titres discrets)
    BLANC   = rgb("FFFFFF")   # fond de toutes les slides de contenu

    # --- Palette utilitaire, camaieu (charte p.7) : schemas et graphiques ---
    MOUTARDE   = rgb("D99B26")   # 1er niveau : valeurs de reference
    CITROUILLE = rgb("EA7C23")   # 2e niveau : progression, valeur intermediaire
    CUIVRE     = rgb("8F3D2E")   # relief, sous-categorie
    AUTOMNE    = rgb("59261D")   # teinte la plus sombre : fonds de graphique, point final

    # Ordre du camaieu pour les series de graphiques (charte p.8).
    CHART_PALETTE = [MOUTARDE, CITROUILLE, ORANGE, CUIVRE, AUTOMNE]
    # A 2 series comparees : contraste fort plutot que deux tons voisins (retour).
    CHART_PAIR = [MOUTARDE, ORANGE]

    # --- Gris techniques (fonctionnels, hors palette nommee) ---
    GRIS_TECH = rgb("F3F2F2")   # aplats techniques : bandes de tableau, carte grise
    FILET     = rgb("E7E7E7")   # filets fins 1 pt (pied de page, separateurs)

    # --- Typographie (charte p.9 a p.11) ---
    FONT = "Quicksand"          # Bold pour les titres, Regular pour le corps
    # Echelle document de reference : H1 24 / H2 14 / corps 10,5.
    DOC_H1, DOC_H2, DOC_BODY = 24.0, 14.0, 10.5
    # Echelle slide 16:9. Calee sur les modeles de la charte puis sur les retours
    # de relecture (RETOURS_CHARTE_showcase) qui fixent chaque corps.
    TITLE      = 28.0    # H1 : titre de slide, capitales, bold
    HEADING    = 14.0    # H2 : intitule de bloc, bold, orange
    BODY       = 14.0    # corps de slide
    SMALL      = 12.0    # texte dense (cartes, cellules) = plancher
    MICRO      = 12.0    # labels, legendes = plancher
    FOOTER     = 8.0     # pied de page (charte : corps 8)
    COVER      = 44.0    # titre de couverture
    COVER_SUB  = 15.0    # sous-titre de couverture (retour : corps 15)
    SECTION    = 44.0    # titre de chapitre
    KPI_VALUE  = 48.0    # metrique de carte KPI
    KPI_LABEL  = 14.0    # libelle de carte KPI
    DELTA      = 12.0    # variation (optionnelle) d'une carte KPI
    PHASE      = 18.0    # intitule de phase (feuille de route)
    TABLE_HEAD = 14.0    # en-tete de tableau
    TABLE_CELL = 12.0    # cellule de tableau
    CHART_LABEL = 12.0   # etiquettes de valeurs d'un graphique
    CHART_LEGEND = 14.0  # legende d'un graphique
    PIE_LABEL  = 18.0    # etiquettes d'un camembert (centrees dans la part)
    QUOTE      = 28.0    # verbatim
    QUOTE_SOURCE = 18.0  # source d'un verbatim
    QUOTE_LINE = 1.5     # interlignage du verbatim

    # Planchers imposes par la relecture : aucun titre sous 14, aucun texte sous 12.
    # (Le pied de page reste a 8 : c'est la charte qui l'impose.)
    MIN_HEADING = 14.0
    MIN_TEXT = 12.0

    # Espacement : l'espace AVANT un titre vaut 2x l'espace APRES (charte p.11).
    SP_H1 = (20.0, 10.0)
    SP_H2 = (16.0, 8.0)
    SP_BODY = (0.0, 6.0)
    # Interlignage strictement entre 1,3 et 1,4 pour le texte courant.
    LINE_MIN = 1.3
    LINE_MAX = 1.4
    LINE = 1.35
    LINE_TIGHT = 1.2     # blocs denses (cartes, cellules)

    # --- Geometrie 16:9 (pouces) ---
    SW = 13.333
    SH = 7.5
    BAND_W = 0.1969          # bande orange bord gauche = 0,5 cm (obligatoire)
    MARGIN = 0.78            # ferrage du contenu (apres la bande)
    MARGIN_R = 0.78
    FOOTER_MARGIN = 0.45     # le pied deborde legerement du bloc de contenu
    TITLE_TOP = 0.52
    TITLE_H = 0.46
    RULE_Y = 1.06            # trait orange 3 pt sous le titre
    RULE_W = 0.60
    RULE_PT = 3.0
    CONTENT_TOP = 1.60       # premiere ligne de contenu
    GUTTER = 0.55            # gouttiere entre colonne texte et colonne visuelle
    MEASURE_MAX = 7.2        # largeur de justification max d'une colonne de texte
    FOOTER_LINE_Y = 6.86     # filet 1 pt
    FOOTER_TEXT_Y = 7.00
    FOOTER_LOGO = 0.24       # hauteur du badge (logo secondaire)
    ICON_RADIUS_PT = 4.0     # coins arrondis du carre-icone (charte p.14)
    ICON_FILL_RATIO = 0.6    # l'icone occupe 60 % du carre (marge 20 % par cote)

    # Fond des slides evenementielles : image de degrade fournie par la charte
    # (orange #EE8506 -> rubis #E11225). Remplace l'aplat orange uni.
    EVENT_BG_IMAGE = "fond_chapitre.jpg"

    FOOTER_LEFT = "THE OZ - AGENCE SHOPIFY"
    FOOTER_RIGHT = "DOCUMENT INTERNE"


@dataclass(frozen=True)
class Surface:
    """Socle visuel d'une slide : fond + couleurs de chrome qui en decoulent.

    Deux surfaces seulement, imposees par la charte : CONTENU (fond blanc) et
    EVENEMENT (fond orange, slides de couverture / chapitre / fin).
    """
    name: str
    on_orange: bool
    bg: RGBColor
    text: RGBColor          # texte principal
    text_muted: RGBColor    # texte discret
    accent: RGBColor        # accent editorial (1er mot, intitules de bloc)
    rule: RGBColor          # filets et traits
    logo_variant: str       # "orange" (fond clair) ou "blanc" (fond sombre/orange)
    icon_hex: str


CONTENT = Surface(
    name="content",
    on_orange=False,
    bg=Brand.BLANC,
    text=Brand.NOIR,
    text_muted=Brand.GRIS,
    accent=Brand.ORANGE,
    rule=Brand.FILET,
    logo_variant="orange",
    icon_hex="191919",
)

EVENT = Surface(
    name="event",
    on_orange=True,
    bg=Brand.ORANGE,
    text=Brand.BLANC,
    text_muted=Brand.BLANC,
    accent=Brand.NOIR,       # sur fond orange, l'accent est le noir (charte : couverture)
    rule=Brand.BLANC,
    logo_variant="blanc",
    icon_hex="FFFFFF",
)


# --- Tons semantiques (chiffres, icones, badges) ---
TONES = {
    "positive": Brand.VERT,      # progression, objectif atteint
    "positif": Brand.VERT,
    "green": Brand.VERT,
    "vert": Brand.VERT,
    "negative": Brand.RUBIS,     # alerte, echec, metrique negative
    "negatif": Brand.RUBIS,
    "alert": Brand.RUBIS,
    "rubis": Brand.RUBIS,
    "accent": Brand.ORANGE,      # ponctuation identitaire
    "orange": Brand.ORANGE,
    "neutral": Brand.NOIR,
    "neutre": Brand.NOIR,
    "dark": Brand.NOIR,
    "noir": Brand.NOIR,
    "gris": Brand.GRIS,
    "grey": Brand.GRIS,
    "cuivre": Brand.CUIVRE,
    "copper": Brand.CUIVRE,
}


def tone(name: str | None, default: RGBColor = Brand.NOIR) -> RGBColor:
    return TONES.get((name or "").strip().lower(), default)


def glyph_hex_on(fill: RGBColor) -> str:
    """Charte p.14 : l'icone est monochrome, du blanc au noir selon l'arriere-plan."""
    return "FFFFFF" if luminance(fill) < 0.55 else "191919"


# --- Compatibilite : la charte V2 n'a plus qu'un systeme visuel. -------------
# Les plans existants qui portent encore "theme": "dark" | "light" restent
# valides et rendent la charte V2.
THEMES = {"oz": CONTENT, "light": CONTENT, "dark": CONTENT}


def get_theme(name: str | None = None) -> Surface:
    """Surface de contenu (fond blanc). Conserve pour compatibilite d'appel."""
    return CONTENT


# ===========================================================================
# Export des tokens de charte
# ===========================================================================
#
# Un consommateur NON-PowerPoint (rapport PDF de la flotte, page web, note) doit
# pouvoir appliquer la charte V2 sans jamais redeclarer une couleur ni un corps.
# Ce module est la seule source : le generateur ci-dessous ne contient AUCUNE
# valeur en dur, il ne fait que lire `Brand` et `CHARTE_VERSION`.
#
#     python -m oz_deck.theme --export json    # tokens bruts
#     python -m oz_deck.theme --export css     # :root { --oz-* }
#
# L'export est versionne : il embarque `charte_version`, ce qui permet de
# detecter une divergence entre un PDF produit par un consommateur et un .pptx
# produit par le moteur (meme version tamponnee, cf. docprops.py).

from . import fonts as _fonts
from . import logos as _logos


def _hex(color: RGBColor) -> str:
    return "#" + str(color)


# Nom expose -> attribut de `Brand`. Les valeurs ne sont JAMAIS ecrites ici.
_PALETTE_PRINCIPALE = {
    "noir": "NOIR", "vert-sauge": "VERT", "orange": "ORANGE",
    "rubis": "RUBIS", "gris": "GRIS", "blanc": "BLANC",
}
_PALETTE_UTILITAIRE = {
    "moutarde": "MOUTARDE", "citrouille": "CITROUILLE", "orange": "ORANGE",
    "cuivre": "CUIVRE", "automne": "AUTOMNE",
}
_GRIS_TECHNIQUES = {"gris-technique": "GRIS_TECH", "filet": "FILET"}
_ROLES = {
    "positif": "VERT",      # progression, objectif atteint
    "negatif": "RUBIS",     # alerte, echec, metrique negative
    "accent": "ORANGE",     # ponctuation identitaire
    "neutre": "NOIR",       # volumes, donnees de reference
    "secondaire": "GRIS",   # legendes, sous-titres discrets
    "fond": "BLANC",        # fond de toutes les slides de contenu
}


def export_tokens() -> dict:
    """Tokens de charte, prets a etre consommes hors PowerPoint."""
    g = lambda name: getattr(Brand, name)  # noqa: E731

    return {
        "charte_version": CHARTE_VERSION,
        "police": {
            "famille": g("FONT"),
            "graisses": _fonts.WEIGHTS,
            "serif_interdite": True,
            # Fichiers livres avec le paquet. Chemins RELATIFS au dossier de
            # fontes, volontairement : un chemin absolu dependrait de la machine
            # et rendrait l'export non comparable. Resolution a l'execution :
            # `oz_deck.fonts.files()`.
            "fichiers": dict(_fonts.FILES),
            "dossier": "assets/fonts",
            "licence": _fonts.LICENCE,
            "licence_fichier": _fonts.LICENCE_FILE,
        },
        "logos": {
            # Chemins RELATIFS au dossier d'assets, comme pour les fontes : un
            # chemin absolu dependrait de la machine. Resolution a l'execution :
            # `oz_deck.logos.path(type, variante)` ou `logos.files()`.
            "fichiers": {k: dict(v) for k, v in _logos.FILES.items()},
            "dossier": "assets",
            "ratio_largeur_hauteur": dict(_logos.RATIO),
            # Marge transparente a gauche de chaque PNG, a compenser pour un
            # ferrage a gauche exact.
            "marge_transparente_gauche": dict(_logos.INK_LEFT),
            "zone_de_protection": _logos.PROTECTION_RATIO,
            "variante_fond_clair": _logos.for_background(dark=False),
            "variante_fond_sombre": _logos.for_background(dark=True),
            "noir_banni": True,
        },
        "couleurs": {
            "principale": {k: _hex(g(v)) for k, v in _PALETTE_PRINCIPALE.items()},
            "utilitaire": {k: _hex(g(v)) for k, v in _PALETTE_UTILITAIRE.items()},
            # Ordre du camaieu pour les series d'un graphique (charte p.8).
            "utilitaire_ordre": [_hex(c) for c in g("CHART_PALETTE")],
            # A DEUX series comparees : contraste fort plutot que deux tons voisins.
            "paire_contraste": [_hex(c) for c in g("CHART_PAIR")],
            "technique": {k: _hex(g(v)) for k, v in _GRIS_TECHNIQUES.items()},
            "roles": {k: _hex(g(v)) for k, v in _ROLES.items()},
        },
        "typographie": {
            # Echelle DOCUMENT (rapport A4, note, page web). Distincte de
            # l'echelle slide, qui n'a de sens qu'en 16:9.
            "document": {
                "h1": g("DOC_H1"), "h2": g("DOC_H2"), "corps": g("DOC_BODY"),
            },
            "planchers": {"titre": g("MIN_HEADING"), "texte": g("MIN_TEXT")},
        },
        "espacement": {
            # L'espace AVANT un titre vaut 2x l'espace APRES (charte p.11).
            "ratio_avant_apres": g("SP_H1")[0] / g("SP_H1")[1],
            "h1": {"avant": g("SP_H1")[0], "apres": g("SP_H1")[1]},
            "h2": {"avant": g("SP_H2")[0], "apres": g("SP_H2")[1]},
            "corps": {"avant": g("SP_BODY")[0], "apres": g("SP_BODY")[1]},
            "unite": "pt",
        },
        "interlignage": {
            # Strictement borne pour le texte courant (charte p.11).
            "texte_courant_min": g("LINE_MIN"),
            "texte_courant_max": g("LINE_MAX"),
            "defaut": g("LINE"),
            "dense": g("LINE_TIGHT"),
        },
        "editorial": {
            # Premier mot ou concept cle en gras ET en couleur.
            "accent_premier_mot": True,
            "balise_concept": "*concat*",
            "ferrage": "gauche",
            "justifie_interdit": True,
            "centre_interdit": True,
            "chiffres_ferres_a_droite": True,
        },
    }


def _flatten(node, prefix="oz"):
    """Aplatit l'arbre de tokens en paires `--oz-a-b-c` -> valeur."""
    out = []
    if isinstance(node, dict):
        for key, val in node.items():
            out += _flatten(val, f"{prefix}-{key}")
    elif isinstance(node, list):
        out.append((prefix, ", ".join(str(v) for v in node)))
    elif isinstance(node, bool):
        out.append((prefix, "true" if node else "false"))
    else:
        out.append((prefix, str(node)))
    return out


def export_css() -> str:
    """Variables CSS de la charte, utilisables telles quelles par WeasyPrint.

    Pas de `var()` imbrique, pas de calcul, pas de preprocesseur : chaque
    variable porte une valeur litterale. Les corps et espacements sont exprimes
    en `pt`, unite native de WeasyPrint pour la mise en page papier.
    """
    tokens = export_tokens()
    lines = [
        "/* Charte The Oz - tokens generes par `python -m oz_deck.theme --export css`.",
        f"   Charte version {tokens['charte_version']}. NE PAS EDITER A LA MAIN :",
        "   la source unique est engine/oz_deck/theme.py. */",
        ":root {",
    ]
    pt_prefixes = ("oz-typographie-", "oz-espacement-")
    for name, value in _flatten(tokens):
        if value in ("true", "false"):
            continue          # drapeaux de politique : utiles en JSON, pas en CSS
        name = name.replace("_", "-")
        if name.startswith(pt_prefixes) and _is_number(value) and "ratio" not in name:
            value = f"{value}pt"
        lines.append(f"  --{name}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _main(argv=None) -> int:
    import argparse
    import json as _json

    ap = argparse.ArgumentParser(
        prog="python -m oz_deck.theme",
        description="Exporte les tokens de la charte The Oz (source unique : theme.py).")
    ap.add_argument("--export", choices=("json", "css"), required=True,
                    help="format de sortie")
    args = ap.parse_args(argv)
    if args.export == "json":
        print(_json.dumps(export_tokens(), ensure_ascii=False, indent=2))
    else:
        print(export_css(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
