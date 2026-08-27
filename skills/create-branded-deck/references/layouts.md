# Layouts - detail & exemples

Chaque slide est un objet avec une cle `layout` + ses champs. La charte V2 n'a qu'un
systeme visuel : ne mettre AUCUNE cle `theme`.

- Slides de **contenu** : fond blanc, bande orange 0,5 cm au bord gauche, titre en
  capitales corps 28 + trait orange 3 pt dessous, pied de page avec pagination.
  PAS de second niveau de titre sous le H1.
- Slides **evenementielles** (`cover`, `report-cover`, `section`, `closing`) : fond
  degrade de la charte (orange vers rubis), chrome blanc, pagination incluse.

Corps a respecter : corps de slide 14, texte dense 12, metrique KPI 48, libelle 14,
variation 12, phase 18, verbatim 28 et sa source 18, tableau 14/12, graphique 12
(camembert 18) et legende 14. **Aucun titre sous 14, aucun texte sous 12.**
Aucun effet d'ombre portee. Puces et non tirets. Symbole monetaire, pas le code.

Tons semantiques (champ `tone`) : `positive` (vert sauge), `negative` (rubis),
`accent` (orange), `neutral` (noir), `gris`, `cuivre`.

Style editorial : le 1er mot d'un `body` passe en gras et en couleur. Pour un concept
de plusieurs mots, l'entourer d'asterisques : `"*Le taux d'abandon* atteint 12 %..."`.

## cover
```
{ "layout": "cover", "kicker": "Diagnostic e-commerce",
  "title": "Analyse CRO du parcours d'achat", "subtitle": "...",
  "client": "Nom du client", "date": "Novembre 2025" }
```
Couverture : fond orange, logo principal blanc a gauche, titre en capitales corps 44
dont le PREMIER MOT (ou le concept balise `*...*`) passe en noir. Tous les champs sauf
`title` sont optionnels.

## section
```
{ "layout": "section", "title": "Chapitre / sous-partie",
  "subtitle": "est un exemple", "caption": "..." }
```
Intercalaire de chapitre (modele charte p.22) : fond orange, `title` en NOIR,
`subtitle` en BLANC sur la ligne suivante, filet blanc, `caption` en petit dessous.
`number` optionnel (affiche en noir au-dessus).

## content
`{ "layout": "content", "title": "...", "blocks": [ {"heading": "Constat", "body": "..."} ] }`
1 a 3 blocs (heading orange + paragraphe, 1er mot en gras auto). Pour du texte structure.

## tiles
```
{ "layout": "tiles", "title": "...",
  "tiles": [ {"heading": "...", "body": "...", "icon": "users", "tone": "gris"} ] }
```
2 a 4 cartes blanches a contour fin, cote a cote. `icon` + `tone` posent un carre-icone
charte (coins 4 pt, icone monochrome occupant 60 % du carre). Optionnels.

## kpi
```
{ "layout": "kpi", "title": "Performance globale du checkout",
  "kpis": [ {"icon": "trending-up", "value": "+ 24,5%",
             "label": "Taux de conversion post refonte (3 mois)", "tone": "positive"},
            {"icon": "triangle-alert", "value": "12%",
             "label": "Taux d'abandon observe au checkout", "tone": "negative"},
            {"icon": "users", "value": "45 300",
             "label": "Sessions observees depuis 1 semaine", "tone": "neutral"} ] }
```
2 a 4 cartes blanches a contour fin (modele charte p.19) : icone filaire coloree,
metrique en grand, libelle en corps de texte. `tone` donne la couleur de l'icone ET du
chiffre. `delta` optionnel (vert si `positive:true`, rubis sinon).

## table
```
{ "layout": "table", "title": "...", "headers": ["Canal","Visites","CA"],
  "rows": [ ["Direct","300 000","0,6 M"], ["Social","485 000","!5% du CA"] ] }
```
En-tete noir/blanc capitales, bandes alternees. 1re colonne ferree a gauche, autres a
droite (alignement des unites). Prefixe `!` = alerte rubis ; prefixe `+` = vert sauge ;
ligne dont la 1re cellule vaut `TOTAL` = gras. `left_align:true` pour un tableau de texte.

## chart
```
{ "layout": "chart", "title": "...", "chart_type": "bar",
  "categories": ["Jan","Fev","Mar"],
  "series": [ {"name": "CA", "values": [10, 20, 15]} ] }
```
Graphique NATIF editable. `chart_type`: `bar` | `line` | `pie`. Les series prennent
automatiquement le camaieu utilitaire de la charte, dans l'ordre : moutarde,
citrouille, orange, cuivre, automne. Un camembert colore ses parts dans le meme ordre.
Etiquettes de valeurs et legende automatiques (`labels:false` / `legend:false` pour les
couper). Ne jamais specifier de couleur.

## grid
```
{ "layout": "grid", "title": "...", "intro": "...(optionnel)",
  "items": [ {"heading": "...", "body": "..."} ] }
```
Grille de 4 a 6 tuiles courtes (2 rangees, 2 ou 3 colonnes auto). Pour lister
plusieurs marqueurs/leviers sur une seule slide (evite de scinder en 2 pages).

## Images : cadrage

Quel que soit le layout (`capture`, `audit`, `split`), l'image est **contenue** dans sa
zone, ratio d'aspect preserve : bridee par la largeur si elle est panoramique, par la
hauteur si elle est en portrait. Tout format passe (JPEG, PNG, PNG avec transparence).

Elle est **collee au repere de marge exterieur et au haut du contenu**, pas centree :
son bord exterieur tombe exactement sur la marge et son haut s'aligne sur celui de la
colonne texte. Le jeu restant part dans la gouttiere.

Dans `capture` et `audit`, la colonne texte **recupere la largeur que l'image n'utilise
pas** : une capture verticale ne laisse donc plus de poche de blanc au milieu de la
slide. Cela reste plus lisible avec une image large : pour le modele p.18 de la charte,
fournir une image composite (deux ecrans cote a cote) plutot qu'une capture unique.

Si `image` est absent ou introuvable, le moteur pose un placeholder
`[ CAPTURE CLIENT ]` : on peut livrer sans image.

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
{ "layout": "capture", "title": "Analyse de la page panier",
  "intro": "Points de blocage identifies", "image": "asset://abc123",
  "frictions": [ {"label": "Le bouton de validation est sous la ligne de flottaison"},
                 {"label": "Les frais de port ne sont pas indiques clairement"} ] }
```
Modele charte p.18 : constats numerotes par pastilles RUBIS a gauche, capture client a
droite (handle `register_asset`, sinon placeholder). `intro` = intitule de la colonne
(defaut "Points de blocage identifies"). `impact` optionnel par friction
(`ELEVE` -> rubis, `MOYEN` -> gris, `FAIBLE` -> vert sauge).

## roadmap
```
{ "layout": "roadmap", "title": "Feuille de route et reco CRO",
  "phases": [ {"heading": "Phase 1 - immediat",
               "items": ["Corriger le bug du bouton sur Mobile (Safari)",
                         "Supprimer les champs facultatifs sur le formulaire"]},
              {"heading": "Phase 2 - a 30 jours", "items": ["..."]},
              {"heading": "Phase 3 - a 90 jours", "items": ["..."]} ] }
```
Modele charte p.20 : 2 a 4 colonnes de phases separees par un filet vertical fin.
L'intitule et son soulignement prennent le camaieu utilitaire dans l'ordre des phases
(surchargeable par `tone`). C'est LE layout pour un plan d'actions sequence dans le temps
(`recommendations` sert quand il faut qualifier impact / effort / priorite).

## verbatim
```
{ "layout": "verbatim", "title": "Verbatim utilisateur",
  "quote": "*L'etape de paiement* est trop confuse, j'ai cherche pendant 2 minutes...",
  "source": "Utilisateur Mobile, test interface du 10/11" }
```
Modele charte p.21 : citation en grand (corps 22, interlignage aere), concept cle en
gras et en cuivre, source en gris. Une seule citation par slide.

## recommendations
```
{ "layout": "recommendations", "title": "...", "subtitle": "...(opt)",
  "items": [ { "icon": "shopping-cart", "title": "Optimiser le tunnel",
               "impact": "Eleve", "effort": "Moyen", "priority": "1", "accent": true,
               "actions": ["action 1", "action 2"] } ] }
```
Rangees : icone + titre + colonnes Impact/Effort/Priorite + puces d'actions. Pour un
plan d'actions priorise (reproduit "Recommandations prioritaires" de la charte).
`tone` colore le carre-icone (`accent` -> orange, `negative` -> rubis, defaut noir). 3 a 4 items conseilles.
Options (page 15 "04") : `number` (numero de section prefixe au titre) et `objective`
= `{label?, body, icon?}` (ligne "Objectif global" en bas).

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
Option (page 19) : `annotations` = `[{n, x, y}]` pose des pastilles numerotees rubis
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
(heading orange + 1er mot du body en gras) + callout `attention` encadre rubis en bas
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
gauche, graphique natif a droite, callout d'attention encadre rubis en bas. `chart` et
`attention` optionnels. `tone` sur un finding colore son carre-icone.

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

## Plans de reference
- `tests/charte_v2_modeles.json` - reproduit les modeles de slides de la charte V2
  (couverture, chapitre, contenu, capture, KPI, feuille de route, verbatim, graphique,
  page de fin). A comparer au PDF de charte.
- `tests/ecommerce_analysis.json` - analyse e-commerce complete.
- `tests/diagnostic_recreation.json` - note de diagnostic.
