# CLAUDE.md - The Oz Deck Builder

Instructions de projet pour Claude Code / l'IDE. Lire en premier.

## Ce que fait le projet

Genere des PowerPoint `.pptx` NATIFS et EDITABLES aux couleurs The Oz a partir d'un
plan JSON, conformement a la charte The Oz V2. Un seul systeme visuel : contenu sur
fond blanc, slides evenementielles sur le degrade de la charte. Expose comme serveur
MCP local.

## Architecture (principe directeur)

Le MOTEUR est la source de verite unique ; tout le reste est un adaptateur fin.

```
engine/oz_deck/      <- MOTEUR deterministe (charte + layouts + rendu). NE PAS dupliquer.
  theme.py           <- tokens de charte V2 (palettes, typo, espacements, geometrie)
  engine.py          <- layouts + build(schema)->pptx
  icons.py           <- icones Lucide (PNG teintes)
  catalog.py         <- catalogue + JSON Schema + validate()
  fontembed.py       <- embarquement de la police dans le .pptx
  docprops.py        <- tampon de version de charte dans le .pptx
  fonts.py / logos.py <- fontes et logos officiels, exposes aux consommateurs
mcp/server.py        <- adaptateur MCP stdio, importe oz_deck
mcp/run.sh           <- lanceur : prepare un venv isole au 1er demarrage
skills/              <- skill qui pilote le MCP
tests/               <- plans de reference + conformance.py (tests de charte)
```

Regle d'or : toute logique de rendu/charte va dans `engine/oz_deck`. Les adaptateurs
ne font que traduire un transport (stdio) en appel `build()` / `validate()`.

## Regles de charte V2 (invariantes)

Tout est tokenise dans `engine/oz_deck/theme.py` : ne JAMAIS ecrire une couleur ou
une cote en dur ailleurs.

- **Palette principale** : Noir `#191919`, Vert sauge `#3E9356` (positif), Orange logo
  `#EC4324` (identitaire), Rubis `#D3122A` (alerte / negatif), Gris `#999999`
  (secondaire), Blanc `#FFFFFF` (fond de tous les contenus).
- **Palette utilitaire (camaieu)**, reservee aux graphiques et schemas, dans cet ordre :
  Moutarde `#D99B26`, Citrouille `#EA7C23`, Orange `#EC4324`, Cuivre `#8F3D2E`,
  Automne `#59261D`. A DEUX series comparees : moutarde + orange (contraste fort).
- **Gris techniques** : `#F3F2F2` (aplats, bandes de tableau), `#E7E7E7` (filets 1 pt).
- **Fonds** : slides d'analyse et de contenu en blanc EXCLUSIVEMENT ; slides
  evenementielles (couverture, chapitre, fin) sur le degrade de la charte
  (`assets/fond_chapitre.jpg`), pose en pleine page.
- **Elements graphiques obligatoires** : bande orange de 0,5 cm calee sur le bord
  gauche de toutes les slides de contenu ; trait orange de 3 pt juste sous le titre.
- **Police** : Quicksand (Google Fonts, OFL), Bold pour les titres et Regular pour le
  corps, declaree dans le theme et sur chaque run. Jamais de serif.
- **Polices EMBARQUEES : desactivees par defaut.** PowerPoint pour le WEB (Teams,
  Office en ligne) refuse d'ouvrir un fichier qui en contient. La cle racine
  `embed_fonts: true` les reactive pour un deck distribue uniquement en client
  lourd. Contrepartie : un destinataire sans Quicksand verra une substitution ;
  leur installer la police (`oz_deck.fonts`) est la vraie parade.
- **Echelle de slide** : titre de slide 28, couverture et chapitre 44, intitule de
  bloc 14, corps 14, texte dense 12, metrique KPI 48, libelle KPI 14, variation 12,
  phase de feuille de route 18, verbatim 28 (interlignage 1,5) et sa source 18,
  en-tete de tableau 14, cellule 12, etiquettes de graphique 12 (camembert 18),
  legende 14, pied 8.
- **Planchers** : aucun titre sous le corps 14, aucun texte sous le corps 12. Seul le
  pied de page descend a 8, parce que la charte l'impose.
- **Espacement** : l'espace AVANT un titre vaut 2x l'espace APRES (H1 20/10, H2 16/8,
  corps 0/6). Interlignage du texte courant strictement entre 1,3 et 1,4 :
  `_running_line()` y ramene tout paragraphe de texte courant, la regle est donc
  structurelle et pas seulement rappelee a chaque appel.
- **Aucun effet d'ombre portee.** `add_shape` attache un `<p:style>` qui herite des
  effets du theme Office : toute autoforme passe donc par `_shape()`, qui coupe
  l'heritage. Ne jamais appeler `add_shape` directement.
- **Ferrage a gauche** partout ; chiffres et metriques a droite (alignement des
  unites) ; jamais de justifie, jamais de bloc centre.
- **Couverture** : titre en capitales corps 44 dont le premier mot / concept cle en
  noir, 2 lignes maximum, puis filet blanc et UN seul niveau de sous-titre.
- **Pied standardise** : filet 1 pt, logo secondaire + "THE OZ - AGENCE SHOPIFY" en
  corps 8 a gauche (libelle centre sur la hauteur du badge), "DOCUMENT INTERNE" +
  pagination ferres a droite. Pagination sur TOUTES les slides.
- **Ferrage des logos** : les PNG officiels ont une marge transparente (8,13 % a
  gauche pour le principal, 1 % pour le secondaire). `_LOGO_INK_LEFT` la compense
  pour que l'encre tombe exactement sur la marge.
- **Logo** : orange sur fond clair, blanc monochrome sur fond degrade/sombre. Le noir
  est banni.
- **Icones** : Lucide, filaires monochromes uniquement (jamais de solid ni de
  couleur). Eventuellement dans un carre 1:1 aux coins de 4 pt (gris, orange, cuivre
  ou noir), l'icone occupant 60 % du carre.
- **Style editorial** : premier mot / concept cle en gras ET en couleur (gere par le
  moteur ; un concept multi-mots se balise `*ainsi*`). Sur la couverture et les
  chapitres, cet accent est le NOIR.
- **Puces** : caractere de puce, jamais un tiret. **Pastilles numerotees** : chiffre
  au corps 14. **Symbole monetaire** plutot que le code a trois lettres.
- **Pas de second niveau de titre** sous le H1 d'une slide de contenu.
- **L'orange ponctue, le rubis alerte.** Ne pas confondre les deux.
- **Composants hors charte** (voir `catalog.IGNORED_FIELDS`) : pastilles de niveau
  ELEVE/MOYEN/FAIBLE, cartouche Client/Periode, barre d'onglets, sur-titre de
  couverture, accroche de page de fin, tuile pleine orange des cartes KPI. Les champs
  correspondants restent acceptes mais ne sont plus rendus.

## Regles de code

- Python 3.11+. Le moteur ne depend QUE de `python-pptx` + `Pillow` (pas de police ni
  LibreOffice au runtime : le rendu final se fait dans le PowerPoint du destinataire).
- Graphiques : natifs (`add_chart`), jamais rendus en image.
- Les gros binaires (images, .pptx) ne transitent pas dans les reponses : handles
  d'assets, chemins locaux ou URLs.
- Images : toujours CONTENUES dans leur zone (ratio preserve) et collees au repere de
  marge exterieur. Les chemins relatifs d'un plan passent par `resolve_images()`.
- Ponctuation : uniquement le trait d'union `-`, jamais `-` cadratin ni `-` demi-cadratin,
  dans TOUT livrable (code, docs, titres, slides).

## Commandes (voir manifest.json)

- `pip install mcp -r engine/requirements.txt`
- `PYTHONPATH=engine python3 engine/cli.py <schema.json> <sortie.pptx>` (rendu local)
- `python3 tests/conformance.py <sortie.pptx>` (TESTS DE CHARTE : verifie les regles
  ci-dessus sur le .pptx produit, plus sa validite structurelle OOXML. A lancer apres
  toute modification de theme.py ou engine.py.)
- `PYTHONPATH=engine python3 -m oz_deck --export json|css` (tokens de charte pour un
  consommateur hors PowerPoint : rapport PDF, page web. `theme.py` est la seule
  source, le generateur ne contient aucune valeur en dur.)

## Layouts disponibles (20)

cover, report-cover, section, content, tiles, grid, kpi, roadmap, verbatim, table,
chart, split, capture, recommendations, audit, dashboard, summary, performance,
analysis, closing.
Voir skills/create-branded-deck/references/layouts.md.

## Logos et assets

Les 4 PNG officiels sont dans engine/oz_deck/assets/ (principal = badge + wordmark
pour cover/closing ; secondaire = badge seul pour le pied). Le degrade des pages
evenementielles est `assets/fond_chapitre.jpg`. Le masque brande
`assets/oz_template_master.pptx` porte les invariants (fond, bande orange, titre +
trait, pied) et 7 dispositions nommees "OZ - ..." : le deck genere est donc aussi un
template reutilisable dans PowerPoint.

## Consommer la charte hors PowerPoint

Le moteur n'est pas seulement un generateur de `.pptx` : c'est la source de verite
de la charte pour tout consommateur.

- `python3 -m oz_deck --export json|css` donne palette, camaieu, roles semantiques,
  echelle DOCUMENT, espacement 2:1, bornes d'interlignage et planchers de corps. Le
  CSS est utilisable tel quel par WeasyPrint.
- `oz_deck.fonts` expose les deux Quicksand statiques a un chemin stable, avec leur
  licence OFL et un `@font-face` pret a coller. La licence DOIT accompagner toute
  redistribution.
- `CHARTE_VERSION` (theme.py) est propagee a l'export ET tamponnee dans le `.pptx`
  (propriete personnalisee `OzCharteVersion`, voir `docprops.py`) : un livrable est
  toujours rattachable a une version de charte precise. La bumper des qu'un token
  change.
- `tests/charte_tokens.json` fige l'export : toute derive d'un token de `Brand` fait
  echouer `conformance.py`. Une modification volontaire se valide en regenerant
  l'instantane ET en bumpant `CHARTE_VERSION`.

Le rendu doit rester REPRODUCTIBLE octet pour octet : aucun horodatage dans le
`.pptx`, sinon toute comparaison de decks de reference devient impossible.

## Points ouverts

- Types de graphiques funnel / waterfall (optionnel).
- Pagination : posee par le moteur (elle depend du rang de la slide). Une slide
  ajoutee a la main dans le template n'aura donc pas de numero.
