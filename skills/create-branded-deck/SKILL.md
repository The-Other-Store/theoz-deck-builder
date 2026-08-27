---
name: create-branded-deck
description: >
  Cree un PowerPoint charte The Oz (charte V2) a partir d'un brief, de donnees ou
  d'un document. Utiliser des que l'utilisateur veut produire une presentation, un
  deck, des slides, un diagnostic, un rapport commercial ou une note aux couleurs
  The Oz, ou mentionne "PPT charte", "slides The Oz", "presentation The Oz", ou
  fournit un Excel/CSV a transformer en deck.
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
  qui renvoie un handle `asset://...` a mettre dans le champ `image` d'un slide
  `capture`, `audit` ou `split`. Voir la section "Images" (flux en deux temps).

## Procedure

1. **Rassembler le contenu** : lire le brief, l'Excel/CSV ou le document source.
   Extraire les chiffres et les messages. Ne pas inventer de donnees.
2. **Ne pas choisir de template** : la charte V2 n'a qu'un systeme visuel. Les
   slides de contenu sont sur fond blanc, les slides evenementielles (`cover`,
   `report-cover`, `section`, `closing`) sur le fond degrade de la charte. Ne pas
   mettre de cle `theme` dans le plan.
3. **Decouvrir les layouts** : appeler `list_layouts` (catalogue) et
   `get_deck_schema` (contrat) si besoin de rappel des champs.
4. **Composer le plan JSON** : une liste `slides`, chaque slide = un `layout`
   + ses champs. Structure narrative recommandee : cover -> section -> kpi/content
   -> charts/tables -> tiles/capture -> closing.
5. **Enregistrer les images** eventuelles via `register_asset` (flux obligatoire
   en deux temps, voir la section "Images" ci-dessous). Etape a ignorer s'il n'y a
   aucune capture/photo.
6. **Valider** avec `validate_deck`. Corriger toute erreur retournee avant de rendre.
7. **Rendre** avec `create_deck` (donner un `filename` parlant). Recuperer le chemin.
8. **QA** : convertir en images et inspecter (idealement via sous-agent) avant de
   livrer. Voir `references/qa.md`.

## Regles de charte a respecter dans le contenu

- **Style editorial** : commencer chaque phrase de bloc par le mot ou le concept cle.
  Le moteur le passe en gras ET en couleur automatiquement. Pour un concept de
  PLUSIEURS mots, l'entourer d'asterisques en tete de chaine :
  `"*L'etape de paiement* est trop confuse, ..."`.
- **Titre de couverture** : le premier mot (ou le concept balise `*...*`) passe en
  noir sur le fond orange. Placer donc le mot le plus fort en tete.
- **Chiffres et metriques** : ferrage a droite gere par le moteur (tableaux).
- **Tons semantiques** (champ `tone`, ou `positive` pour un delta) :
  - `positive` -> vert sauge `#3E9356` : progression, objectif atteint, KPI au vert ;
  - `negative` -> rubis `#D3122A` : alerte, echec, metrique negative ;
  - `accent` -> orange `#EC4324` : ponctuation identitaire, a garder rare ;
  - `neutral` -> noir `#191919` : volumes et donnees de reference.
- **Tableaux** : prefixer une valeur par `!` -> rubis (alerte) ; par `+` -> vert
  sauge ; une ligne dont la 1re cellule vaut `TOTAL` passe en gras.
- **Graphiques** : les series prennent automatiquement le camaieu utilitaire
  (moutarde, citrouille, orange, cuivre, automne). Ne pas specifier de couleur.
- **L'orange se merite** : c'est la couleur identitaire, elle ponctue. L'alerte,
  c'est le rubis.
- **Monnaie** : toujours le symbole monetaire, jamais le code a trois lettres.
- **Ne pas emettre** les champs listes dans `champs_sans_effet` (retour de
  `list_layouts`) : `subtitle` sur une slide de contenu, `kicker` / `client` /
  `date` sur une couverture, `headline` sur la page de fin, `meta` / `tabs` sur un
  tableau de bord, `impact` sur une friction. Ils sont acceptes mais plus rendus.
- **Titre de couverture ou de chapitre** : 2 lignes maximum.
- **`split`** : preferer le texte a GAUCHE et le visuel a droite (`swap: true`), et
  `numbered: true` quand les blocs commentent des zones de la capture.

## Images (captures, photos)

Ajouter une image est un flux OBLIGATOIRE en deux temps. Ne JAMAIS mettre un chemin
de fichier, une URL, ou du base64 directement dans un champ `image` : le moteur
n'accepte QUE des handles `asset://...`.

1. **Enregistrer** le fichier local (PNG/JPG qui existe sur le disque) :
   `register_asset("/chemin/absolu/capture.png")` -> retourne `{"asset_id": "asset://a1b2c3..."}`.
2. **Referencer** ce handle exact dans le champ `image` du slide. L'emplacement du
   champ depend du layout :
   - `capture` et `audit` : champ `image` au niveau du slide (top-level).
   - `split` : champ `image` DANS `left` (c.-a-d. `left.image`), en alternative a
     `left.chart`. Un slide `split` a soit un graphique, soit une image a gauche, pas les deux.

Exemple complet (capture) :
```
{ "layout": "capture", "title": "Audit CRO - Checkout",
  "image": "asset://a1b2c3d4e5f6",
  "frictions": [ {"label": "Frais affiches trop tard", "impact": "ELEVE"} ] }
```

Exemple (split avec image a gauche) :
```
{ "layout": "split", "title": "Parcours mobile",
  "left":  { "image": "asset://a1b2c3d4e5f6" },
  "right": { "blocks": [ {"heading": "Constat", "body": "..."} ] } }
```

Notes :
- Si `image` est absent (ou le fichier introuvable), le moteur dessine un placeholder
  `[ CAPTURE CLIENT ]` : c'est voulu, on peut livrer sans image.
- L'image est contenue dans sa zone et centree, ratio preserve : tout format passe.
  Une capture verticale n'occupe qu'une bande centrale ; pour remplir la largeur,
  fournir une image composite (deux ecrans cote a cote).
- Un seul handle par image. Pour reutiliser la meme capture sur deux slides, reutiliser
  le meme `asset://...`.
- En mode distant (API AWS), `register_asset` renverra une URL S3 presignee : le flux
  cote plan JSON reste identique (toujours un handle dans `image`).

## Details des layouts et exemples

Voir `references/layouts.md` pour le detail des 20 layouts et des exemples de plan.
Plans de reference dans le dossier `tests/` du plugin :
- `charte_v2_modeles.json` : reproduit les modeles de slides de la charte V2 ;
- `ecommerce_analysis.json`, `diagnostic_recreation.json` : cas reels.
