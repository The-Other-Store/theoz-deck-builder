# CLAUDE.md - The Oz Deck Builder

Instructions de projet pour Claude Code / l'IDE. Lire en premier.

## Ce que fait le projet

Genere des PowerPoint `.pptx` NATIFS et EDITABLES aux couleurs The Oz a partir d'un
plan JSON. Deux templates : `dark` (premium) et `light` (rapports). Expose comme
serveur MCP local.

## Architecture (principe directeur)

Le MOTEUR est la source de verite unique ; tout le reste est un adaptateur fin.

```
engine/oz_deck/      <- MOTEUR deterministe (charte + layouts + rendu). NE PAS dupliquer.
  theme.py           <- tokens de charte + themes dark/light
  engine.py          <- layouts + build(schema)->pptx
  icons.py           <- icones facon Lucide (PNG)
  catalog.py         <- catalogue + JSON Schema + validate()
mcp/server.py        <- adaptateur MCP stdio, importe oz_deck
mcp/run.sh           <- lanceur : prepare un venv isole au 1er demarrage
skills/              <- skill qui pilote le MCP
```

Regle d'or : toute logique de rendu/charte va dans `engine/oz_deck`. Les adaptateurs
ne font que traduire un transport (stdio) en appel `build()` / `validate()`.

## Regles de charte (invariantes)

- Palette 60/30/10 : Noir `#191919`, Vert validation `#346F53`, Orange accent `#EC4324`.
  Neutres : `#F3F2F2`, `#222222`, `#999999`, `#E7E7E7`, blanc.
- Police : Arial (substitution systeme d'Helvetica). Jamais de serif.
- Ferrage a gauche ; chiffres/metriques a droite ; jamais de justifie ni de centre
  (hors titres/couverture).
- Titre haut-gauche avec barre verticale orange. Pied de page "THE OZ - AGENCE SHOPIFY"
  + "DOCUMENT INTERNE" + pagination.
- Logo : orange sur fond clair, blanc sur fond sombre. Jamais noir.
- Icones : Lucide, outline monochrome ; orange reserve aux frictions/anomalies.
- Style editorial : premier mot/concept cle en gras (gere par le moteur).

## Regles de code

- Python 3.11+. Le moteur ne depend QUE de `python-pptx` + `Pillow` (pas de police ni
  LibreOffice au runtime : le rendu final se fait dans le PowerPoint du destinataire).
- Graphiques : natifs (`add_chart`), jamais rendus en image.
- Les gros binaires (images, .pptx) ne transitent pas dans les reponses : handles
  d'assets, chemins locaux ou URLs.
- Ponctuation : uniquement le trait d'union `-`, jamais `-` cadratin ni `-` demi-cadratin,
  dans TOUT livrable (code, docs, titres, slides).

## Commandes (voir manifest.json)

- `pip install mcp -r engine/requirements.txt`
- `PYTHONPATH=engine python3 engine/cli.py <schema.json> <sortie.pptx>` (rendu local)

## Layouts disponibles

cover, section, content, tiles, grid, kpi, table, chart, split, capture,
recommendations, audit, closing. Voir skills/create-branded-deck/references/layouts.md.

## Logos

Les 4 PNG officiels sont dans engine/oz_deck/assets/ (principal = badge + wordmark
pour cover/closing ; secondaire = badge seul pour le pied). Variante blanc sur fond
sombre, orange sur fond clair (regle charte), gere par `_logo`.

## Points ouverts

- Vraies icones Lucide (meme API `icons.icon_png` ; actuellement tracees maison).
- Types de graphiques funnel / waterfall (optionnel).
- Graphique `pie` : `_chart_in` accede aux axes sans condition -> a corriger pour
  supporter les camemberts (annonces dans le catalogue).
