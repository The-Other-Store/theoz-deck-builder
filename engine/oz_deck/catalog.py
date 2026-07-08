"""
catalog.py - Catalogue de layouts, JSON Schema du deck, et validation.

Le catalogue guide le CHOIX (quand utiliser quel layout), le JSON Schema
CONTRAINT la sortie du modele, et validate() renvoie des erreurs structurees
pour l'auto-correction avant rendu.
"""

from __future__ import annotations
from .icons import AVAILABLE as ICONS

LAYOUT_CATALOG = [
    {"layout": "cover", "usage": "Couverture. Champs: kicker?, title, subtitle?"},
    {"layout": "section", "usage": "Intercalaire de partie. Champs: number?, title"},
    {"layout": "content", "usage": "1 a 3 blocs texte (heading orange + body, 1er mot en gras). Champs: title, blocks[{heading, body}]"},
    {"layout": "tiles", "usage": "2 ou 3 tuiles cote a cote. Champs: title, tiles[{heading, body}]"},
    {"layout": "grid", "usage": "Grille de 4 a 6 tuiles courtes (2 rangees). Champs: title, intro?, items[{heading, body}]"},
    {"layout": "kpi", "usage": "2 a 4 cartes indicateurs. Champs: title, kpis[{icon, label, value, delta?, positive?, accent?}]"},
    {"layout": "table", "usage": "Tableau charte. 1re col a gauche, autres a droite. Prefixe '!' = alerte orange. Champs: title, headers[], rows[[]]"},
    {"layout": "chart", "usage": "Graphique natif editable. Champs: title, chart_type(bar|line|pie), categories[], series[{name, values[]}]"},
    {"layout": "split", "usage": "Deux colonnes : visuel (graphique/image) + texte (blocs ou cartes). Champs: title, ratio(half|third|two-thirds)?, swap?, left{chart{...}|image}, right{blocks[]|cards[]}"},
    {"layout": "capture", "usage": "Audit simple: capture a droite + tuiles friction a gauche. Champs: title, image?, frictions[{label, impact(ELEVE|MOYEN|FAIBLE)}]"},
    {"layout": "recommendations", "usage": "Recommandations prioritaires : rangees icone + titre + impact/effort/priorite + actions. Champs: title, subtitle?, items[{icon, title, impact, effort, priority, actions[], accent?}]"},
    {"layout": "audit", "usage": "Audit CRO complet : resume executif + bandeau impact chiffre + frictions a gauche, capture a droite. Champs: title, subtitle?, image?, summary?, impact[{label, value}], frictions[{label, impact}]"},
    {"layout": "closing", "usage": "Slide de fin. Champs: headline?, url?"},
]

THEMES = ["dark", "light"]

# JSON Schema (draft-07) surface a exposer au modele via le MCP.
DECK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "The Oz branded deck",
    "type": "object",
    "required": ["slides"],
    "properties": {
        "theme": {"type": "string", "enum": THEMES, "default": "dark",
                  "description": "Template global. Surchargable par slide."},
        "slides": {"type": "array", "minItems": 1, "items": {"$ref": "#/definitions/slide"}},
    },
    "definitions": {
        "icon": {"type": "string", "enum": ICONS},
        "slide": {
            "type": "object",
            "required": ["layout"],
            "properties": {
                "layout": {"type": "string",
                           "enum": [l["layout"] for l in LAYOUT_CATALOG]},
                "theme": {"type": "string", "enum": THEMES},
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
                {"if": {"properties": {"layout": {"const": "table"}}},
                 "then": {"required": ["title", "headers", "rows"]}},
                {"if": {"properties": {"layout": {"const": "chart"}}},
                 "then": {"required": ["title", "categories", "series"]}},
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
}
_VALID_LAYOUTS = set(_REQUIRED)


def validate(schema: dict) -> list[dict]:
    """Retourne une liste d'erreurs structurees (vide si OK)."""
    errors = []
    if not isinstance(schema, dict):
        return [{"path": "$", "error": "le schema doit etre un objet JSON"}]
    if schema.get("theme") and schema["theme"] not in THEMES:
        errors.append({"path": "theme", "error": f"theme inconnu, attendu {THEMES}"})
    slides = schema.get("slides")
    if not isinstance(slides, list) or not slides:
        return errors + [{"path": "slides", "error": "champ 'slides' manquant ou vide"}]
    for i, sl in enumerate(slides):
        p = f"slides[{i}]"
        layout = sl.get("layout")
        if layout not in _VALID_LAYOUTS:
            errors.append({"path": f"{p}.layout", "error": f"layout invalide {layout!r}, attendu {sorted(_VALID_LAYOUTS)}"})
            continue
        for field in _REQUIRED[layout]:
            if field not in sl:
                errors.append({"path": f"{p}.{field}", "error": f"champ requis manquant pour layout '{layout}'"})
        if layout == "kpi":
            for j, k in enumerate(sl.get("kpis", [])):
                ic = k.get("icon")
                if ic and ic not in ICONS:
                    errors.append({"path": f"{p}.kpis[{j}].icon", "error": f"icone inconnue {ic!r}"})
        if layout == "chart":
            ct = sl.get("chart_type", "bar")
            if ct not in ("bar", "line", "pie"):
                errors.append({"path": f"{p}.chart_type", "error": f"chart_type invalide {ct!r}"})
            for j, ser in enumerate(sl.get("series", [])):
                if "values" not in ser:
                    errors.append({"path": f"{p}.series[{j}].values", "error": "valeurs manquantes"})
    return errors
