# Installation utilisateur - The Oz Deck Builder

Guide de l'utilisateur final : installer le plugin dans Claude (Cowork / Claude
Code / Claude Desktop) et produire des PowerPoint chartes The Oz.

## 1. Comment ca marche

Le moteur tourne sur ta machine via un serveur MCP local. L'IA compose un plan JSON
leger ; le moteur rend un `.pptx` natif et editable (ecrit dans `out/`).

## 2. Prerequis

- **Python >= 3.11** dans le `PATH` (`python3 --version`).
- Acces reseau a PyPI **au premier demarrage** (pour installer les dependances du
  moteur). Ensuite, plus besoin de reseau pour le rendu.

Aucune installation manuelle de dependances n'est requise : le plugin embarque un
lanceur (`mcp/run.sh`) qui prepare tout seul un environnement Python isole. Voir
section 3.

## 3. Installer le plugin (marketplace)

Le repo `The-Other-Store/theoz-deck-builder` est un marketplace Claude Code. Dans
Claude Code / Cowork :

```
/plugin marketplace add The-Other-Store/theoz-deck-builder
/plugin install theoz-deck-builder@theoz
```

Au premier demarrage du serveur MCP, le lanceur `mcp/run.sh` :

1. cree un environnement virtuel Python **local au plugin** (`.venv/`, sans droits
   admin, sans `sudo`) ;
2. y installe les dependances (`mcp`, `python-pptx`, `Pillow`) ;
3. lance le serveur `theoz-deck-builder`.

Les fois suivantes, il reutilise ce `.venv` (demarrage immediat).

### Poste aux droits limites / reseau restreint

Le lanceur degrade proprement :

- Si le venv ne peut pas etre construit (pas de Python 3.11+, module `venv`
  absent, PyPI injoignable), il se rabat sur un `python3` systeme qui aurait deja
  `mcp`, `python-pptx` et `Pillow`.
- A defaut, il affiche une consigne : `pip install --user mcp python-pptx Pillow`
  dans l'interpreteur Python utilise par ton client.

> Windows : le lanceur est un script bash ; l'executer via Git Bash.

## 4. Verifier l'installation

Le serveur expose 6 outils. Une fois le plugin charge, ils doivent apparaitre :

| Outil            | Role                                                        |
|------------------|-------------------------------------------------------------|
| `list_layouts`   | Catalogue des layouts et des themes disponibles.            |
| `get_deck_schema`| Contrat JSON attendu par le moteur.                         |
| `list_icons`     | Noms d'icones utilisables (facon Lucide).                   |
| `validate_deck`  | Valide un plan JSON, renvoie les erreurs.                   |
| `register_asset` | Enregistre une image externe, renvoie un handle `asset://`. |
| `create_deck`    | Rend le `.pptx` et renvoie son chemin.                      |

Test hors client (rendu direct via le CLI, sans MCP) - creer un plan minimal puis :

```bash
cat > /tmp/plan.json <<'JSON'
{"theme":"dark","slides":[
  {"layout":"cover","kicker":"DEMO","title":"Mon deck","subtitle":"The Oz"},
  {"layout":"closing","url":"the-oz.com"}
]}
JSON
PYTHONPATH=engine python3 engine/cli.py /tmp/plan.json out/demo.pptx
```

Un `.pptx` doit apparaitre dans `out/`.

## 5. Produire un deck

En conversation, la skill `create-branded-deck` guide toute la composition. En
resume :

1. Decrire le besoin (brief, chiffres, ou fichier Excel/CSV).
2. Choisir le template : `dark` (fond noir, premium, defaut) ou `light`
   (fond clair, rapports).
3. Laisser Claude composer un plan JSON leger (une liste `slides`, chaque slide =
   un `layout` + ses champs), le valider (`validate_deck`), puis le rendre
   (`create_deck`).
4. Recuperer le `.pptx` dans `out/`, editable nativement dans PowerPoint.

Points cles de charte (geres par le moteur) : graphiques natifs et non des images,
logo/icones/couleurs resolus automatiquement, orange reserve aux accents et
anomalies. Detail des layouts : `skills/create-branded-deck/references/layouts.md`.

## 6. Images externes

Pour inclure une capture ou une photo : `register_asset` renvoie un handle
`asset://...` a placer dans le champ `image` d'un slide `capture`. Ne jamais coller
d'image de slide entiere : le moteur compose la mise en page.

## 7. Depannage

- **Les outils MCP n'apparaissent pas** : verifier que le serveur `theoz-deck-builder`
  est autorise, et que `python3` du client trouve `mcp`, `python-pptx`, `Pillow`.
- **`ModuleNotFoundError: oz_deck`** : `PYTHONPATH` doit pointer sur `engine/`
  (fait par `.mcp.json` ; en manuel, prefixer les commandes par `PYTHONPATH=engine`).
- **`ModuleNotFoundError: mcp`** : `pip install mcp` dans le bon interpreteur.
- **Python trop ancien** : le moteur requiert 3.11+ ; installer une version recente.
- **Erreurs de validation** : `validate_deck` renvoie `path` + `error` par champ ;
  corriger le plan avant de rendre.
