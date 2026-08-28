# The Oz Deck Builder

Genere des PowerPoint chartes The Oz - natifs et editables - a partir d'un plan JSON.
Un moteur deterministe unique, conforme a la charte The Oz V2, utilisable dans Claude
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
├── tests/            Plans de reference + tests de conformite a la charte
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

## Charte V2

Un seul systeme visuel :

- **slides de contenu** : fond blanc, bande orange de 0,5 cm au bord gauche, titre en
  capitales corps 28 suivi d'un trait orange de 3 pt, pied standardise avec pagination ;
- **slides evenementielles** (couverture, chapitre, fin) : fond degrade de la charte,
  logo blanc, chrome blanc ;
- **typographie** Quicksand (Bold/Regular), embarquee dans le `.pptx` ;
- **palette principale** noir / vert sauge / orange / rubis / gris / blanc, et
  **camaieu utilitaire** (moutarde vers automne) reserve aux graphiques.

Il n'y a pas de cle `theme` a fournir dans le plan.

Le masque `engine/oz_deck/assets/oz_template_master.pptx` porte ces invariants et
7 dispositions nommees "OZ - ..." : le deck genere est donc aussi un template
reutilisable dans PowerPoint.

## Layouts (20)

cover, report-cover, section, content, tiles, grid, kpi, roadmap, verbatim, table,
chart (natif), split, capture, recommendations, audit, dashboard, summary,
performance, analysis, closing. Detail et exemples :
`skills/create-branded-deck/references/layouts.md`.

## Consommer la charte hors PowerPoint

Le moteur est la source de verite de la charte, y compris pour un consommateur qui
ne produit pas de PowerPoint (rapport PDF, page web) :

```bash
PYTHONPATH=engine python3 -m oz_deck --export json   # tokens bruts
PYTHONPATH=engine python3 -m oz_deck --export css    # :root { --oz-* }
```

Le CSS est utilisable tel quel par WeasyPrint : valeurs litterales, pas de `var()`
imbrique, corps et espacements en `pt`. Il couvre la palette principale, le camaieu
utilitaire et sa paire de contraste, les roles semantiques, l'echelle DOCUMENT
(H1 24 / H2 14 / corps 10,5), l'espacement 2:1, les bornes d'interlignage et les
planchers de corps.

Les fontes suivent :

```python
from oz_deck import fonts
fonts.files()["regular"]     # chemin stable des Quicksand statiques
print(fonts.css_font_face()) # @font-face pret a coller
```

Quicksand est sous licence SIL Open Font License 1.1 : `OFL.txt` est livre a cote
des fichiers et doit accompagner toute redistribution.

Chaque export porte `charte_version`, et la meme valeur est tamponnee dans les
`.pptx` produits (propriete personnalisee `OzCharteVersion`) : un livrable reste
rattachable a une version de charte precise.

## Tests de conformite

```bash
python3 tests/conformance.py <deck.pptx>
```

Inspecte le `.pptx` produit (formes, couleurs, polices, alignements reels) et verifie
les regles de la charte : fonds, bande orange, trait de titre, pied, palette,
typographie, ferrage, interlignage, planchers de corps, absence d'ombre portee,
confinement des images, ainsi que la validite structurelle OOXML.

## Prerequis

Python >= 3.11. Le moteur ne depend que de `python-pptx` et `Pillow` ; le serveur MCP
ajoute le SDK `mcp`. Aucune police ni LibreOffice au runtime (le rendu final se fait
dans le PowerPoint du destinataire).
