# Installation utilisateur - The Oz Deck Builder

Guide de l'utilisateur final : installer le plugin et produire des PowerPoint
chartes The Oz. Aucune connaissance AWS requise. Pour le deploiement de l'API
distante, voir `INSTALL_ENTERPRISE.md`.

Le plugin s'installe depuis la marketplace **`The-Other-Store/theoz-deck-builder`**.

## 1. Deux facons d'utiliser

- **Local (MCP)** : le moteur tourne sur ta machine via un serveur MCP. C'est le
  mode par defaut. Les `.pptx` sont ecrits dans `out/`.
- **Distant (API)** : le moteur tourne sur AWS ; tu passes par le connecteur mis en
  place par l'entreprise. Rien a installer cote moteur (voir `REMOTE_USAGE.md`).

Ce guide couvre l'installation **locale (MCP)**.

## 2. Prerequis

- **Python >= 3.11** dans le `PATH` (`python3 --version`).
- Acces reseau a PyPI **au premier demarrage** seulement, pour installer les
  dependances du moteur. Ensuite, plus besoin de reseau pour le rendu.

Aucune installation manuelle de dependances : le plugin embarque un lanceur
(`mcp/run.sh`) qui prepare tout seul un environnement Python isole (section 5).

## 3. Installer depuis Claude Desktop

C'est la voie la plus simple, et la seule si tu n'utilises pas la ligne de commande.

### 3.1 Ajouter la marketplace

1. Ouvrir les **Paramètres** de l'application.
2. Dans la colonne de gauche, section **Personnaliser**, cliquer sur **Plugins**.
3. En haut a droite, ouvrir le menu **+ Ajouter**, puis **Ajouter une place de
   marché**.
4. Une mise en garde s'affiche : les plugins de marketplace ne sont pas controles
   par Anthropic. C'est attendu - `theoz-deck-builder` est le depot de l'agence.
5. Dans le champ **URL**, saisir :

   ```
   The-Other-Store/theoz-deck-builder
   ```

   Le champ accepte un `owner/repo` GitHub ou une URL de depot Git complete.
6. Cliquer sur **Synchro**.

Le plugin **Theoz deck builder** apparait alors sous « Depuis les marketplaces que
vous avez ajoutées », dans l'onglet **Les vôtres**.

### 3.2 Verifier ce qui est reellement installe

Toujours dans **Plugins**, menu **+ Ajouter** > **Gérer les marketplaces**. La
fiche `theoz-deck-builder` affiche l'URL du depot et surtout :

```
Commit synchronisé : <sha>
```

**C'est la seule information fiable sur la version dont tu disposes.** Compare-la
au dernier commit du depot : s'ils different, ta copie est en retard (section 4).

> La date affichee a droite du plugin dans la liste est celle de la POSE INITIALE,
> pas celle de la derniere mise a jour. Elle ne bouge jamais. Ne pas s'y fier.

### 3.3 Activer, desactiver, retirer

Le menu **⋮** a droite du plugin propose **Désactiver**, **Rechercher des mises à
jour** et **Supprimer**.

Supprimer la marketplace (via **Gérer les marketplaces** > **⋮** > **Supprimer**)
**desinstalle aussi ses plugins**.

## 4. Mettre a jour

La synchronisation automatique existe (**Gérer les marketplaces** > **⋮** >
**Synchroniser automatiquement**) mais elle n'est pas immediate : une copie peut
rester plusieurs versions en retard alors que l'option est active.

Pour forcer la mise a jour :

1. **Plugins** > **+ Ajouter** > **Gérer les marketplaces**.
2. Sur la fiche `theoz-deck-builder`, menu **⋮** > **Rechercher des mises à jour**.
3. Verifier que **Commit synchronisé** a change.
4. **Redemarrer l'application** : les serveurs MCP se montent au lancement.

Si le plugin lui-meme ne suit pas, son menu **⋮** dans la liste propose aussi
**Rechercher des mises à jour**.

## 5. Installer depuis Claude Code (ligne de commande)

```
/plugin marketplace add The-Other-Store/theoz-deck-builder
/plugin install theoz-deck-builder@theoz
```

Mise a jour :

```
/plugin marketplace update theoz
/plugin update theoz-deck-builder@theoz
```

Deux pieges :

- **Le rafraichissement de la marketplace n'est pas optionnel.** Sans lui, Claude
  compare la version installee a une copie locale qui peut dater de plusieurs
  semaines, et ne propose donc AUCUNE mise a jour.
- **La forme courte echoue.** `claude plugin update theoz-deck-builder` renvoie
  « Plugin not found » : il faut l'identifiant qualifie `plugin@marketplace`.

Etat reel en ligne de commande :

```bash
claude plugin list | grep -A2 theoz-deck-builder
```

## 6. Ce qui se passe au premier demarrage

Le lanceur `mcp/run.sh` :

1. cree un environnement virtuel Python **local au plugin** (`.venv/`, sans droits
   admin, sans `sudo`) ;
2. y installe les dependances (`mcp`, `python-pptx`, `Pillow`) ;
3. lance le serveur `theoz-deck-builder`.

Les fois suivantes, il reutilise ce `.venv` : demarrage immediat.

### Poste aux droits limites ou reseau restreint

Le lanceur degrade proprement :

- si le venv ne peut pas etre construit (pas de Python 3.11+, module `venv` absent,
  PyPI injoignable), il se rabat sur un `python3` systeme qui aurait deja `mcp`,
  `python-pptx` et `Pillow` ;
- a defaut, il affiche la consigne `pip install --user mcp python-pptx Pillow`.

> Windows : le lanceur est un script bash ; l'executer via Git Bash, ou passer par
> le mode distant.

## 7. Verifier l'installation

Le serveur expose 6 outils :

| Outil            | Role                                                        |
|------------------|-------------------------------------------------------------|
| `list_layouts`   | Catalogue des layouts + rappel de charte.                   |
| `get_deck_schema`| Contrat JSON attendu par le moteur.                         |
| `list_icons`     | Noms d'icones utilisables (Lucide).                         |
| `validate_deck`  | Valide un plan JSON, renvoie les erreurs.                   |
| `register_asset` | Enregistre une image externe, renvoie un handle `asset://`. |
| `create_deck`    | Rend le `.pptx` et renvoie son chemin.                      |

> Le serveur MCP est un serveur **stdio local** : il se monte a la demande et
> s'eteint apres usage. Il n'apparait donc PAS dans une liste de connecteurs
> permanents, contrairement aux connecteurs hebergés. Son absence de cette liste
> n'est pas un symptome.

Test en une phrase : demander `list_layouts`. La reponse doit contenir **20
layouts**, dont `roadmap` et `verbatim`. Moins, et c'est une version ancienne.

Test hors client (rendu direct, sans MCP) :

```bash
PYTHONPATH=engine python3 engine/cli.py tests/charte_v2_modeles.json out/modeles.pptx
```

## 8. Produire un deck

La skill `create-branded-deck` guide toute la composition. En resume :

1. Decrire le besoin (brief, chiffres, ou fichier Excel/CSV).
2. Rien a choisir cote template : la charte V2 n'a qu'un systeme visuel (contenu
   sur fond blanc, slides evenementielles sur le degrade de la charte).
3. Laisser Claude composer un plan JSON leger, le valider (`validate_deck`), puis
   le rendre (`create_deck`).
4. Recuperer le `.pptx`, editable nativement dans PowerPoint.

Pour inclure une capture ou une photo : `register_asset` renvoie un handle
`asset://...` a placer dans le champ `image` d'un slide `capture`, `audit` ou
`split`. Ne jamais coller une image de slide entiere : le moteur compose la mise
en page.

## 9. Depannage

- **Aucune mise a jour proposee** : la marketplace n'a pas ete resynchronisee.
  Voir section 4 (Desktop) ou 5 (ligne de commande). C'est la cause n°1.
- **Les outils MCP n'apparaissent pas** : redemarrer l'application (les serveurs se
  montent au lancement), et verifier que `python3` trouve `mcp`, `python-pptx` et
  `Pillow`.
- **Le deck ne s'ouvre pas dans Teams ou PowerPoint en ligne** : ne pas mettre
  `"embed_fonts": true` dans le plan. PowerPoint web refuse d'ouvrir un fichier
  contenant des polices embarquees. Le defaut (faux) ouvre partout.
- **Le texte n'est pas en Quicksand chez le destinataire** : consequence directe du
  point precedent. La police n'etant pas embarquee, une machine qui ne l'a pas
  installee substitue. Installer Quicksand sur les postes concernes ; les fichiers
  et leur licence OFL sont dans `engine/oz_deck/assets/fonts/`.
- **`ModuleNotFoundError: oz_deck`** : `PYTHONPATH` doit pointer sur `engine/`
  (fait par `.mcp.json` ; en manuel, prefixer par `PYTHONPATH=engine`).
- **Erreurs de validation** : `validate_deck` renvoie `path` + `error` par champ ;
  corriger le plan avant de rendre.
