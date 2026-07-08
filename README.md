# The Oz Deck Builder

Genere des PowerPoint chartes The Oz - natifs et editables - a partir d'un plan JSON.
Un moteur deterministe unique, deux templates (clair & sombre), utilisable dans Claude
Code / Cowork via un serveur MCP.

## Pourquoi

Creer des PPT chartes dans un assistant nativement est lourd (beaucoup de tokens) et
donne une charte instable. Ici, l'IA ne produit qu'un plan JSON leger ; un moteur
Python fait le rendu, ce qui garantit : editabilite native, charte unifiee, cout en
tokens minimal.

## Structure

```
theoz-deck-builder/
├── engine/oz_deck/   Moteur (charte, layouts, rendu, validation)
├── engine/cli.py     Rendu local : schema JSON -> .pptx
├── mcp/server.py     Serveur MCP local (stdio)
├── mcp/run.sh        Lanceur : prepare un venv isole au 1er demarrage
├── skills/           Skill "create-branded-deck"
├── docs/             Guide d'installation utilisateur
├── manifest.json     Taches (install, serveur MCP)
└── CLAUDE.md         Regles de charte et de code
```

## Installation (plugin Claude Code / Cowork)

```
/plugin marketplace add The-Other-Store/theoz-deck-builder
/plugin install theoz-deck-builder@theoz
```

Le serveur MCP `theoz-deck-builder` (defini dans `.mcp.json`, lance via `mcp/run.sh`
qui prepare un venv isole et installe les dependances au premier demarrage) expose les
outils `list_layouts`, `get_deck_schema`, `list_icons`, `validate_deck`,
`register_asset`, `create_deck`. La skill `create-branded-deck` guide la composition.
Detail : `docs/INSTALL_USER.md`.

## Rendu local (developpement)

```bash
pip install mcp -r engine/requirements.txt
# rendre un plan JSON en .pptx :
PYTHONPATH=engine python3 engine/cli.py mon_plan.json out/mon_deck.pptx
```

Plan minimal :

```json
{
  "theme": "dark",
  "slides": [
    {"layout": "cover", "kicker": "DEMO", "title": "Mon deck", "subtitle": "The Oz"},
    {"layout": "closing", "url": "the-oz.com"}
  ]
}
```

Le contrat complet est renvoye par l'outil `get_deck_schema` ; les layouts et leurs
champs sont detailles dans `skills/create-branded-deck/references/layouts.md`.

## Templates

- `dark` : fond noir, premium (presentations, diagnostics).
- `light` : fond clair, logo orange (rapports, notes).

Selection via la cle racine `"theme"` du plan, surchargeable par slide.

## Layouts

cover, section, content, tiles, grid, kpi, table, chart (natif), split, capture,
recommendations, audit, closing. Detail et exemples :
`skills/create-branded-deck/references/layouts.md`.

## Prerequis

Python >= 3.11. Le moteur ne depend que de `python-pptx` et `Pillow` ; le serveur MCP
ajoute le SDK `mcp`. Aucune police ni LibreOffice au runtime (le rendu final se fait
dans le PowerPoint du destinataire).
