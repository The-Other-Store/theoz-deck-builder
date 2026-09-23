"""
catalog.py - Catalogue de layouts, JSON Schema du deck, et validation.

Le catalogue guide le CHOIX (quand utiliser quel layout), le JSON Schema
CONTRAINT la sortie du modele, et validate() renvoie des erreurs structurees
pour l'auto-correction avant rendu.

Charte V2 : un seul systeme visuel (contenu blanc / evenementiel orange). La cle
racine "theme" n'a plus d'effet ; elle reste toleree pour les plans anterieurs.
"""

from __future__ import annotations
from .icons import AVAILABLE as ICONS

LAYOUT_CATALOG = [
    {"layout": "cover", "usage": "Couverture (fond degrade, titre capitales corps 44 dont le 1er mot en noir, filet blanc puis UN seul sous-titre corps 15). Titre sur 2 lignes maximum. Pas de logo (il est au pied de page) ni de sur-titre. Champs: title, subtitle?"},
    {"layout": "report-cover", "usage": "Couverture de rapport : comme cover + tagline en bas. Champs: title, subtitle?, tagline?"},
    {"layout": "section", "usage": "Intercalaire de chapitre (fond degrade). `title` en NOIR, `subtitle` en BLANC sur la ligne suivante, corps 44. Champs: number?, title, subtitle?, caption?"},
    {"layout": "content", "usage": "1 a 3 blocs texte (intitule orange corps 14 + corps 14 au style editorial : 1er mot/concept en gras et en couleur). Champs: title, blocks[{heading, body}]"},
    {"layout": "tiles", "usage": "2 a 4 tuiles cote a cote (cartes blanches a contour fin, sans ombre). Champs: title, tiles[{heading, body, icon?, tone?}]"},
    {"layout": "grid", "usage": "Grille de 4 a 6 tuiles courtes (2 ou 3 colonnes). Champs: title, intro?, items[{heading, body, icon?, tone?}]"},
    {"layout": "kpi", "usage": "2 a 4 cartes indicateurs : icone filaire + metrique corps 48 + libelle corps 14 + variation optionnelle corps 12. tone/positive donnent la couleur : vert sauge (positif), rubis (negatif), orange (accent), noir (neutre). Utiliser le symbole EUR sous sa forme monetaire. Champs: title, kpis[{icon, label, value, tone?, positive?, accent?, delta?}]"},
    {"layout": "roadmap", "usage": "Feuille de route / phases : colonnes separees par un filet, intitule corps 18 dans le camaieu utilitaire, items en puces corps 14. Champs: title, phases[{heading, items[], tone?}]"},
    {"layout": "verbatim", "usage": "Verbatim utilisateur : citation corps 28 interlignage 1,5 (concept cle en gras et en cuivre), source corps 18 en gris. Champs: title, quote, source?"},
    {"layout": "table", "usage": "Tableau charte CENTRE verticalement (en-tete noir corps 14, cellules corps 12, bandes alternees). 1re col a gauche, autres a droite. Prefixe '!' = alerte rubis ; '+' = vert sauge ; 1re cellule TOTAL = gras. Champs: title, headers[], rows[[]], left_align?"},
    {"layout": "chart", "usage": "Graphique natif editable. Series au camaieu utilitaire ; a DEUX series, contraste fort automatique (moutarde + orange). Etiquettes corps 12, camembert corps 18 centre dans la part, legende corps 14. Champs: title, chart_type(bar|line|pie), categories[], series[{name, values[]}], labels?, legend?"},
    {"layout": "split", "usage": "Deux colonnes : visuel (graphique/image) + texte. Preferer le TEXTE A GAUCHE et le visuel a droite (swap: true). `numbered: true` prefixe les blocs de pastilles numerotees. Champs: title, ratio(half|third|two-thirds)?, swap?, numbered?, left{chart{...}|image}, right{blocks[]|cards[]}"},
    {"layout": "capture", "usage": "Analyse de capture (modele charte p.18) : constats en PUCES NUMEROTEES (pastille rubis, chiffre corps 14) a gauche, capture client a droite. Champs: title, intro?, image?, frictions[{label}]"},
    {"layout": "recommendations", "usage": "Recommandations prioritaires : rangees carre-icone + titre corps 14 + impact/effort/priorite corps 12 + actions en puces, + ligne 'objectif global' optionnelle. Champs: number?, title, items[{icon, title, impact, effort, priority, actions[], tone?}], objective{label?, body, icon?}?"},
    {"layout": "audit", "usage": "Audit CRO complet : resume executif + bandeau impact chiffre + frictions en puces numerotees a gauche, capture annotee a droite. Champs: title, image?, summary?, impact[{label, value, tone?}], frictions[{label}], annotations[{n, x, y}]?"},
    {"layout": "dashboard", "usage": "Tableau de bord dense : sections a bandeau noir (intitule corps 14, icone blanche) + tables charte corps 12. Champs: title, sections[{heading, icon?, headers[], rows[[]]}]"},
    {"layout": "summary", "usage": "Synthese executive editoriale : blocs corps 14 (1er mot en gras et en couleur) + callout d'attention encadre rubis (titre corps 14, items corps 12). Champs: number?, title, blocks[{heading, body}], attention{title?, items[]}?"},
    {"layout": "performance", "usage": "Indicateurs cles : rangee de cartes KPI compactes + tableau. Pas de tuile pleine : c'est la metrique qui se colorise. Champs: number?, title, kpis[{icon, label, value, tone?, positive?, accent?, delta?}], headers[]?, rows[[]]?"},
    {"layout": "analysis", "usage": "Analyse detaillee : constats a carre-icone a gauche, graphique a droite, callout d'attention en bas. Champs: number?, title, findings[{icon, label, body, tone?}], chart{...}?, attention{title?, items[]}?"},
    {"layout": "closing", "usage": "Slide de fin (fond degrade, logo principal blanc et filet ferres a gauche, URL soulignee). Pas d'accroche. Champs: url?"},
]

# Champs acceptes mais PLUS RENDUS depuis la relecture de charte. Ils ne font pas
# echouer la validation (les plans anterieurs restent valides) mais n'apparaissent
# plus : la relecture les a juges hors charte.
IGNORED_FIELDS = {
    "subtitle": "slides de contenu : pas de second niveau de titre sous le H1",
    "kicker": "couvertures : pas de sur-titre",
    "client": "couvertures : un seul niveau de sous-titre",
    "date": "couvertures : un seul niveau de sous-titre",
    "headline": "page de fin : pas d'accroche au-dessus de l'URL",
    "meta": "tableau de bord : cartouche Client/Periode hors charte",
    "tabs": "tableau de bord : barre d'onglets sans apport",
    "impact": "frictions : les pastilles de niveau n'existent pas dans la charte",
}

# Charte V2 : un seul systeme visuel. Conserve pour compatibilite d'API.
THEMES = ["oz"]
_LEGACY_THEMES = {"oz", "dark", "light"}

# Tons semantiques acceptes partout ou un champ `tone` existe.
TONES = ["positive", "negative", "accent", "neutral", "gris", "cuivre"]

# JSON Schema (draft-07) surface a exposer au modele via le MCP.
DECK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "The Oz branded deck (charte V2)",
    "type": "object",
    "required": ["slides"],
    "properties": {
        "theme": {"type": "string", "enum": sorted(_LEGACY_THEMES), "default": "oz",
                  "description": "Obsolete : la charte V2 n'a qu'un systeme visuel "
                                 "(contenu blanc / evenementiel orange). Tolere pour "
                                 "les plans anterieurs."},
        "embed_fonts": {"type": "boolean", "default": False,
                        "description": "Embarquer Quicksand dans le .pptx. FAUX par "
                                       "defaut : PowerPoint pour le WEB (Teams, Office "
                                       "en ligne) refuse d'ouvrir un fichier contenant "
                                       "des polices embarquees. Ne passer a true que "
                                       "pour un deck distribue uniquement en client "
                                       "lourd, ou la fidelite typographique prime sur "
                                       "l'ouvrabilite."},
        "slides": {"type": "array", "minItems": 1, "items": {"$ref": "#/definitions/slide"}},
    },
    "definitions": {
        "icon": {"type": "string", "enum": ICONS},
        "tone": {"type": "string", "enum": TONES},
        "slide": {
            "type": "object",
            "required": ["layout"],
            "properties": {
                "layout": {"type": "string",
                           "enum": [l["layout"] for l in LAYOUT_CATALOG]},
            },
            "allOf": [
                {"if": {"properties": {"layout": {"const": "cover"}}},
                 "then": {"required": ["title"]}},
                {"if": {"properties": {"layout": {"const": "section"}}},
                 "then": {"required": ["title"]}},
                {"if": {"properties": {"layout": {"const": "content"}}},
                 "then": {"required": ["title", "blocks"]}},
                {"if": {"properties": {"layout": {"const": "tiles"}}},
                 "then": {"required": ["title", "tiles"]}},
                {"if": {"properties": {"layout": {"const": "kpi"}}},
                 "then": {"required": ["title", "kpis"]}},
                {"if": {"properties": {"layout": {"const": "roadmap"}}},
                 "then": {"required": ["title", "phases"]}},
                {"if": {"properties": {"layout": {"const": "verbatim"}}},
                 "then": {"required": ["title", "quote"]}},
                {"if": {"properties": {"layout": {"const": "table"}}},
                 "then": {"required": ["title", "headers", "rows"]}},
                {"if": {"properties": {"layout": {"const": "chart"}}},
                 "then": {"required": ["title", "categories", "series"]}},
                {"if": {"properties": {"layout": {"const": "dashboard"}}},
                 "then": {"required": ["title", "sections"]}},
                {"if": {"properties": {"layout": {"const": "summary"}}},
                 "then": {"required": ["title", "blocks"]}},
                {"if": {"properties": {"layout": {"const": "report-cover"}}},
                 "then": {"required": ["title"]}},
                {"if": {"properties": {"layout": {"const": "performance"}}},
                 "then": {"required": ["title", "kpis"]}},
                {"if": {"properties": {"layout": {"const": "analysis"}}},
                 "then": {"required": ["title", "findings"]}},
            ],
        },
    },
}

_REQUIRED = {
    "cover": ["title"], "section": ["title"], "content": ["title", "blocks"],
    "tiles": ["title", "tiles"], "grid": ["title", "items"], "kpi": ["title", "kpis"],
    "table": ["title", "headers", "rows"], "chart": ["title", "categories", "series"],
    "split": ["title", "left", "right"], "capture": ["title"],
    "recommendations": ["title", "items"], "audit": ["title"], "closing": [],
    "dashboard": ["title", "sections"], "summary": ["title", "blocks"],
    "report-cover": ["title"], "performance": ["title", "kpis"],
    "analysis": ["title", "findings"], "roadmap": ["title", "phases"],
    "verbatim": ["title", "quote"],
}
_VALID_LAYOUTS = set(_REQUIRED)


def _check_icons(errors, path, items, key="icon"):
    for j, it in enumerate(items or []):
        ic = it.get(key)
        if ic and ic not in ICONS:
            errors.append({"path": f"{path}[{j}].{key}", "error": f"icone inconnue {ic!r}"})


def validate(schema: dict) -> list[dict]:
    """Retourne une liste d'erreurs structurees (vide si OK)."""
    errors = []
    if not isinstance(schema, dict):
        return [{"path": "$", "error": "le schema doit etre un objet JSON"}]
    if "embed_fonts" in schema and not isinstance(schema["embed_fonts"], bool):
        errors.append({"path": "embed_fonts",
                       "error": "doit etre un booleen (true/false)"})
    if schema.get("theme") and schema["theme"] not in _LEGACY_THEMES:
        errors.append({"path": "theme", "error": "cle 'theme' obsolete (charte V2 : un seul "
                                                 f"systeme visuel) ; valeurs tolerees {sorted(_LEGACY_THEMES)}"})
    slides = schema.get("slides")
    if not isinstance(slides, list) or not slides:
        return errors + [{"path": "slides", "error": "champ 'slides' manquant ou vide"}]
    for i, sl in enumerate(slides):
        p = f"slides[{i}]"
        layout = sl.get("layout")
        if layout not in _VALID_LAYOUTS:
            errors.append({"path": f"{p}.layout",
                           "error": f"layout invalide {layout!r}, attendu {sorted(_VALID_LAYOUTS)}"})
            continue
        for field in _REQUIRED[layout]:
            if field not in sl:
                errors.append({"path": f"{p}.{field}",
                               "error": f"champ requis manquant pour layout '{layout}'"})
        if layout in ("kpi", "performance"):
            _check_icons(errors, f"{p}.kpis", sl.get("kpis"))
        if layout in ("tiles",):
            _check_icons(errors, f"{p}.tiles", sl.get("tiles"))
        if layout in ("grid",):
            _check_icons(errors, f"{p}.items", sl.get("items"))
        if layout == "recommendations":
            _check_icons(errors, f"{p}.items", sl.get("items"))
        if layout == "analysis":
            _check_icons(errors, f"{p}.findings", sl.get("findings"))
        if layout == "roadmap" and "phases" in sl:
            phases = sl.get("phases")
            if not isinstance(phases, list) or not phases:
                errors.append({"path": f"{p}.phases", "error": "au moins une phase requise"})
            else:
                for j, ph in enumerate(phases):
                    if not ph.get("heading"):
                        errors.append({"path": f"{p}.phases[{j}].heading",
                                       "error": "intitule de phase manquant"})
        if layout == "chart":
            ct = sl.get("chart_type", "bar")
            if ct not in ("bar", "line", "pie"):
                errors.append({"path": f"{p}.chart_type", "error": f"chart_type invalide {ct!r}"})
            for j, ser in enumerate(sl.get("series", [])):
                if "values" not in ser:
                    errors.append({"path": f"{p}.series[{j}].values", "error": "valeurs manquantes"})
        if layout == "dashboard":
            secs = sl.get("sections")
            if not isinstance(secs, list) or not secs:
                errors.append({"path": f"{p}.sections", "error": "au moins une section requise"})
            else:
                for j, sec in enumerate(secs):
                    if not sec.get("headers") or not isinstance(sec.get("rows"), list):
                        errors.append({"path": f"{p}.sections[{j}]",
                                       "error": "section : 'headers' et 'rows' requis"})
    return errors
