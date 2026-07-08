#!/usr/bin/env python3
"""
server.py - Serveur MCP "The Oz Deck Builder" (transport stdio, usage local).

Expose le moteur oz_deck a un client MCP (Cowork / Claude Code / Claude Desktop).

Outils :
  - list_layouts        : catalogue des layouts + themes (guide de CHOIX)
  - get_deck_schema     : JSON Schema du deck (contrat qui CONTRAINT la sortie)
  - list_icons          : icones disponibles
  - validate_deck       : erreurs structurees pour auto-correction avant rendu
  - register_asset      : enregistre une image locale et renvoie un handle asset://
  - create_deck         : rend le schema en .pptx natif charte, renvoie le chemin

Config par variables d'environnement :
  OZ_OUTPUT_DIR   dossier de sortie des .pptx (defaut: ./out)
  OZ_ASSET_DIR    dossier des assets images (defaut: OZ_OUTPUT_DIR/assets)
"""

from __future__ import annotations
import os
import sys
import json
import shutil
import uuid
from pathlib import Path

# Rend le package oz_deck importable (../engine)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))

from oz_deck import build, validate, LAYOUT_CATALOG, DECK_SCHEMA, THEMES  # noqa: E402
from oz_deck.icons import AVAILABLE as ICONS  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.stderr.write("Dependance manquante : pip install 'mcp[cli]'\n")
    raise

OUTPUT_DIR = Path(os.environ.get("OZ_OUTPUT_DIR", "./out")).resolve()
ASSET_DIR = Path(os.environ.get("OZ_ASSET_DIR", str(OUTPUT_DIR / "assets"))).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR.mkdir(parents=True, exist_ok=True)

# Registre des assets : asset://<id> -> chemin fichier local
_ASSETS: dict[str, str] = {}

mcp = FastMCP("theoz-deck-builder")


def _resolve_assets(schema: dict) -> dict:
    """Remplace les handles asset://<id> par les chemins locaux dans le schema."""
    for sl in schema.get("slides", []):
        img = sl.get("image")
        if isinstance(img, str) and img.startswith("asset://"):
            key = img
            if key in _ASSETS:
                sl["image"] = _ASSETS[key]
    return schema


@mcp.tool()
def list_layouts() -> dict:
    """Catalogue des layouts disponibles (quand utiliser quoi) et themes."""
    return {"themes": THEMES, "layouts": LAYOUT_CATALOG}


@mcp.tool()
def get_deck_schema() -> dict:
    """JSON Schema complet d'un deck. A utiliser pour composer un plan valide."""
    return DECK_SCHEMA


@mcp.tool()
def list_icons() -> list[str]:
    """Icones (facon Lucide) utilisables dans les cartes KPI."""
    return ICONS


@mcp.tool()
def validate_deck(schema: dict) -> dict:
    """Valide un plan de deck. Renvoie {ok, errors[]} pour auto-correction."""
    errs = validate(schema)
    return {"ok": len(errs) == 0, "errors": errs}


@mcp.tool()
def register_asset(source_path: str) -> dict:
    """
    Enregistre une image locale (capture, photo) et renvoie un handle asset://<id>
    a referencer dans le champ 'image' d'un slide 'capture'. En prod (AWS),
    cet outil renverra une URL S3 presignee au lieu d'un chemin local.
    """
    src = Path(source_path).expanduser()
    if not src.exists():
        return {"error": f"fichier introuvable : {source_path}"}
    aid = f"asset://{uuid.uuid4().hex[:12]}"
    dest = ASSET_DIR / (aid.split('//')[1] + src.suffix)
    shutil.copy(src, dest)
    _ASSETS[aid] = str(dest)
    return {"asset_id": aid}


@mcp.tool()
def create_deck(schema: dict, filename: str = "deck.pptx") -> dict:
    """
    Rend un plan de deck en PowerPoint natif charte The Oz.
    Valide d'abord ; en cas d'erreur, renvoie les erreurs sans rendre.
    Retourne le chemin du .pptx genere.
    """
    errs = validate(schema)
    if errs:
        return {"ok": False, "errors": errs}
    if not filename.lower().endswith(".pptx"):
        filename += ".pptx"
    out = OUTPUT_DIR / filename
    _resolve_assets(schema)
    build(schema, str(out))
    return {"ok": True, "path": str(out), "slides": len(schema.get("slides", []))}


if __name__ == "__main__":
    mcp.run()
