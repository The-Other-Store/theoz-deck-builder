---
name: create-branded-deck
description: >
  Cree un PowerPoint charte The Oz (templates clair ou sombre) a partir d'un brief,
  de donnees ou d'un document. Utiliser des que l'utilisateur veut produire une
  presentation, un deck, des slides, un diagnostic, un rapport commercial ou une
  note aux couleurs The Oz, ou mentionne "PPT charte", "slides The Oz",
  "presentation The Oz", ou fournit un Excel/CSV a transformer en deck.
---

# Create Branded Deck (The Oz)

Produire un `.pptx` natif et editable aux couleurs The Oz via le serveur MCP
`theoz-deck-builder`. Le modele ne manipule JAMAIS de XML ni d'image de slide :
il compose un PLAN JSON leger, le moteur fait le rendu deterministe.

## Principe

- Les graphiques ne sont PAS des images : passer les donnees (categories/series),
  le moteur cree un graphique natif editable, theme The Oz.
- Le logo, les icones et la charte sont resolus cote serveur. Ne fournir que le
  NOM d'une icone (voir `list_icons`).
- Seules les vraies images externes (captures, photos) passent par `register_asset`,
  qui renvoie un handle `asset://...` a mettre dans le champ `image` d'un slide `capture`.

## Procedure

1. **Rassembler le contenu** : lire le brief, l'Excel/CSV ou le document source.
   Extraire les chiffres et les messages. Ne pas inventer de donnees.
2. **Choisir le template** : `dark` (fond noir, premium, defaut) ou `light`
   (fond clair, rapports). Demander a l'utilisateur si ce n'est pas evident.
3. **Decouvrir les layouts** : appeler `list_layouts` (catalogue) et
   `get_deck_schema` (contrat) si besoin de rappel des champs.
4. **Composer le plan JSON** : une liste `slides`, chaque slide = un `layout`
   + ses champs. Structure narrative recommandee : cover -> section -> kpi/content
   -> charts/tables -> tiles/capture -> closing.
5. **Enregistrer les images** eventuelles via `register_asset` et referencer les
   handles.
6. **Valider** avec `validate_deck`. Corriger toute erreur retournee avant de rendre.
7. **Rendre** avec `create_deck` (donner un `filename` parlant). Recuperer le chemin.
8. **QA** : convertir en images et inspecter (idealement via sous-agent) avant de
   livrer. Voir `references/qa.md`.

## Regles de charte a respecter dans le contenu

- Style editorial : commencer les phrases de bloc par le mot/concept cle (le moteur
  le met en gras automatiquement dans les tuiles et blocs `content`).
- Chiffres et metriques : ferrage a droite gere par le moteur (tableaux).
- Alerte dans un tableau : prefixer la valeur par `!` -> texte orange.
- KPI en accent (valeur orange) : `"accent": true`. Delta positif = vert,
  negatif = orange (`"positive": false`).
- L'orange se merite : reserve aux accents, frictions et anomalies. Ne pas en abuser.

## Details des layouts et exemples

Voir `references/layouts.md` pour le detail de chaque layout et la marche a suivre
pour composer un plan (contrat via `get_deck_schema`, validation via `validate_deck`).
