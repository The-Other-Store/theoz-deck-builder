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
Options (page 15 "04") : `number` (numero de section prefixe au titre) et `objective`
= `{label?, body, icon?}` (ligne "Objectif global" encadree orange en bas).

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
Option (page 19) : `annotations` = `[{n, x, y}]` pose des pastilles numerotees orange
sur la capture (`x`, `y` = fractions 0-1 de la zone capture).

## closing
`{ "layout": "closing", "headline": "The Oz - conseil e-commerce", "url": "www.the-oz.com" }`

## dashboard
```
{ "layout": "dashboard", "title": "Tableau de bord", "subtitle": "Indicateurs cles",
  "meta": [ {"label": "Client", "value": "..."}, {"label": "Periode", "value": "..."} ],
  "sections": [
    { "heading": "Acquisition & trafic", "icon": "trending-up",
      "headers": ["Canal", "Visites", "% total", "Conversion", "CA genere"],
      "rows": [ ["Recherche organique", "128 544", "32,1%", "3,31%", "0,29 M"],
                ["TOTAL", "399 883", "100%", "3,16%", "0,93 M"] ] }
  ],
  "tabs": ["Tableau de bord", "Acquisition", "Conversion"] }
```
Tableau de bord analytique facon tableur (Excel/Sheets, page 17 de la charte). Chaque
section = bandeau sombre a icone + table dense (ferrage a droite, bandes alternees).
Prefixe `!` sur une valeur = alerte orange ; ligne dont la 1re cellule vaut `TOTAL` =
gras. `meta` = cartouche Client/Periode en haut a droite. `tabs` = barre d'onglets bas
(1er actif orange). 1 a 2 sections tiennent confortablement ; les hauteurs s'adaptent.

## summary
```
{ "layout": "summary", "number": "01", "title": "Vue d'ensemble",
  "subtitle": "Synthese executive",
  "blocks": [ {"heading": "Performance en hausse", "body": "..."} ],
  "attention": { "title": "Points d'attention prioritaires",
                 "items": ["...", "..."] } }
```
Page de synthese editoriale (rapport, page 15). Titre de section numerote + blocs
(heading orange + 1er mot du body en gras) + callout `attention` encadre orange en bas
(optionnel). `number` et `attention` sont optionnels. 2 a 4 blocs conseilles.

## report-cover
```
{ "layout": "report-cover", "kicker": "DIAGNOSTIC E-COMMERCE",
  "title": "Performance globale & recommandations", "subtitle": "...(opt)",
  "client": "Client x The Oz", "date": "Octobre 2025",
  "tagline": "Expertise, performance, croissance" }
```
Couverture de rapport editoriale (page 15) : titre a gauche, filet orange, client
(orange), date, logo + tagline en bas. Variante "rapport" de `cover`. Sans pied de page.

## performance
```
{ "layout": "performance", "number": "02", "title": "Performance globale",
  "subtitle": "Indicateurs cles",
  "kpis": [ {"icon": "percent", "label": "Taux de conversion", "value": "2,35%",
             "delta": "+0,32 pt", "positive": true, "accent": true} ],
  "headers": ["Indicateur", "Sept.", "Oct.", "Evolution"],
  "rows": [ ["Visites", "312 544", "358 762", "+14,8%"] ] }
```
Composite "02 Performance globale" (page 15) : rangee de cartes KPI + tableau dessous.
Une carte `accent:true` est rendue en FOND ORANGE plein (texte blanc). `headers`/`rows`
optionnels (KPI seuls possibles). Alerte `!` et ligne `TOTAL` gerees comme un tableau.

## analysis
```
{ "layout": "analysis", "number": "03", "title": "Analyse detaillee",
  "subtitle": "Donnees cles",
  "findings": [ {"icon": "search", "label": "Constat", "body": "..."},
                {"icon": "triangle-alert", "label": "Impact", "body": "...", "accent": true},
                {"icon": "circle-check-big", "label": "Recommandation", "body": "..."} ],
  "chart": { "chart_type": "bar", "categories": ["Mai","Juin"], "series": [{"name":"CA","values":[520,560]}] },
  "attention": { "title": "Points d'attention", "items": ["...", "..."] } }
```
Composite "03 Analyse detaillee" (page 15) : constats a icones (label orange + texte) a
gauche, graphique natif a droite, callout d'attention encadre orange en bas. `chart` et
`attention` optionnels. `accent:true` sur un finding met l'icone en orange.

## Icones disponibles (cartes KPI, recommandations)
Vraies icones Lucide (lucide.dev), contour monochrome. Liste exacte via l'outil
`list_icons`. Catalogue actuel :

- Analytics : trending-up, trending-down, chart-column, chart-line, chart-pie,
  chart-bar, activity, gauge, target, percent
- Commerce : shopping-cart, shopping-bag, package, truck, tag, credit-card, wallet,
  receipt, store, gift, circle-dollar-sign
- Clients : users, user-check, heart, star, thumbs-up, thumbs-down, message-circle
- Communication : mail, megaphone, bell, send, share-2
- Tech / web : smartphone, monitor, globe, wifi, search, funnel, zap, settings,
  database, code
- Statut / UX : circle-check-big, circle-x, triangle-alert, info, clock, calendar,
  lock, shield, eye
- Narratif : rocket, flag, map-pin, layers, lightbulb, refresh-cw, sparkles,
  arrow-up-right, arrow-right

Alias herites acceptes (anciens noms) : bar-chart-3, line-chart, pie-chart,
check-circle-2, alert-triangle, filter.

