# Layouts - detail & exemples

Chaque slide est un objet avec une cle `layout` + ses champs. Le deck a une cle
racine `theme` (`dark` | `light`), surchargable par slide.

## cover
`{ "layout": "cover", "kicker": "JUIN 2026", "title": "...", "subtitle": "..." }`
Couverture : kicker (surtitre), grand titre, sous-titre. kicker/subtitle optionnels.

## section
`{ "layout": "section", "number": "01", "title": "Le diagnostic" }`
Intercalaire de partie. `number` optionnel (affiche en gros orange).

## content
`{ "layout": "content", "title": "...", "blocks": [ {"heading": "Constat", "body": "..."} ] }`
1 a 3 blocs (heading orange + paragraphe, 1er mot en gras auto). Pour du texte structure.

## tiles
`{ "layout": "tiles", "title": "...", "tiles": [ {"heading": "...", "body": "..."} ] }`
2 ou 3 tuiles cote a cote (nombre auto selon la liste). Pour comparer/opposer des idees.

## kpi
```
{ "layout": "kpi", "title": "...",
  "kpis": [ {"icon": "circle-dollar-sign", "label": "CA HT", "value": "374 k",
             "delta": "+15%", "positive": true, "accent": false} ] }
```
2 a 4 cartes chiffrees. `accent:true` -> valeur en orange. `positive:false` -> delta orange.

## table
```
{ "layout": "table", "title": "...", "headers": ["Canal","Visites","CA"],
  "rows": [ ["Direct","300 000","0,6 M"], ["Social","485 000","!5% du CA"] ] }
```
En-tete noir/blanc. 1re colonne ferree a gauche, autres a droite. Prefixe `!` = alerte orange.

## chart
```
{ "layout": "chart", "title": "...", "chart_type": "bar",
  "categories": ["Jan","Fev","Mar"],
  "series": [ {"name": "CA", "values": [10, 20, 15]} ] }
```
Graphique NATIF editable. `chart_type`: `bar` | `line` | `pie`. Palette The Oz auto
(orange = 1re serie/accent). Plusieurs series = legende auto.

## grid
```
{ "layout": "grid", "title": "...", "intro": "...(optionnel)",
  "items": [ {"heading": "...", "body": "..."} ] }
```
Grille de 4 a 6 tuiles courtes (2 rangees, 2 ou 3 colonnes auto). Pour lister
plusieurs marqueurs/leviers sur une seule slide (evite de scinder en 2 pages).

## split
```
{ "layout": "split", "title": "...", "ratio": "half|third|two-thirds", "swap": false,
  "left":  { "chart": { "chart_type": "bar", "categories": [...], "series": [...] } },
  "right": { "blocks": [ {"heading","body"} ] } }
```
Deux colonnes : un VISUEL (graphique ou `image`) + une colonne TEXTE. La colonne
texte accepte `blocks` (paragraphes heading+body) ou `cards` (mini-tuiles empilees).
`ratio` = largeur de la colonne visuelle (defaut half). `swap:true` met le visuel a
droite. C'est LE layout pour reproduire les slides "graphique a gauche, lecture a
droite" sans passer sur deux pages.

## capture
```
{ "layout": "capture", "title": "Audit CRO", "image": "asset://abc123",
  "frictions": [ {"label": "Frais affiches tard", "impact": "ELEVE"} ] }
```
Capture a droite (via handle `register_asset`) + tuiles friction a gauche
(hauteur adaptative). `impact`: `ELEVE` | `MOYEN` | `FAIBLE`. `image` optionnelle.

## recommendations
```
{ "layout": "recommendations", "title": "...", "subtitle": "...(opt)",
  "items": [ { "icon": "shopping-cart", "title": "Optimiser le tunnel",
               "impact": "Eleve", "effort": "Moyen", "priority": "1", "accent": true,
               "actions": ["action 1", "action 2"] } ] }
```
Rangees : icone + titre + colonnes Impact/Effort/Priorite + puces d'actions. Pour un
plan d'actions priorise (reproduit "Recommandations prioritaires" de la charte).
`accent:true` met l'icone et la priorite en orange. 3 a 4 items conseilles.

## audit
```
{ "layout": "audit", "title": "Audit CRO - Page checkout", "subtitle": "...",
  "image": "asset://...", "summary": "...",
  "impact": [ {"label": "Taux actuel", "value": "2,35 %"} ],
  "frictions": [ {"label": "...", "impact": "ELEVE|MOYEN|FAIBLE"} ] }
```
Audit complet : colonne gauche = resume executif + bandeau impact chiffre + frictions
numerotees a badges ; colonne droite = capture. `image` via register_asset (sinon
placeholder). Reproduit la slide "Audit CRO - Page checkout" de la charte.

## closing
`{ "layout": "closing", "headline": "The Oz - conseil e-commerce", "url": "www.the-oz.com" }`

## Icones disponibles (cartes KPI)
trending-up, bar-chart-3, line-chart, pie-chart, percent, users, circle-dollar-sign,
search, shopping-cart, check-circle-2, alert-triangle, smartphone, mail, globe,
clock, sparkles.

## Composer un plan
Appeler `get_deck_schema` pour le contrat JSON complet, puis `validate_deck` avant
`create_deck`. Structure narrative recommandee : cover -> section -> kpi/content ->
chart/table -> tiles/capture -> closing.
