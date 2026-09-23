# QA d'un deck

Apres `create_deck`, verifier le rendu avant livraison. Deux niveaux : les tests
automatiques de conformite (a lancer systematiquement), puis l'oeil humain.

## 1. Tests de conformite a la charte (automatique)

```bash
python3 tests/conformance.py chemin/vers/deck.pptx
```

Inspecte le .pptx reellement produit (formes, couleurs, polices, alignements) et
verifie les regles de la charte V2 :

- format 16:9 paysage ;
- fonds : contenu blanc / evenementiel orange uni ;
- bande orange de 0,5 cm au bord gauche de chaque slide de contenu ;
- trait orange de 3 pt sous le titre, titres en capitales ;
- pied standardise (filet 1 pt + logo + mention corps 8) et pagination ;
- palette : aucune couleur hors charte (principale + camaieu utilitaire) ;
- typographie Quicksand partout, police embarquee dans le fichier ;
- ferrage a gauche : ni texte justifie ni bloc centre ;
- interlignage du texte courant entre 1,3 et 1,4 ;
- espacement des titres : espace avant = 2 x espace apres ;
- graphiques natifs au camaieu utilitaire ;
- logo jamais noir ;
- aucun texte ne franchit le filet de pied (debordement mesure avec les vraies
  fontes Quicksand) ;
- images contenues dans la zone utile et ratio d'aspect preserve (une capture
  portrait est bridee par la HAUTEUR, sinon elle sort de la diapositive) ;
- ponctuation : pas de cadratin ni de demi-cadratin ;
- **ouvrable en PowerPoint web** : aucune police embarquee. Teams et Office en
  ligne refusent d'ouvrir un fichier qui en contient ;
- aucune ombre portee sur les formes ;
- titres de slide au corps 28 ;
- aucun texte sous le corps 12 (hors pied de page a 8) ;
- **structure OOXML valide** : ordre des elements conforme au schema
  ECMA-376 et attributs requis presents. Un ordre invalide donne un fichier
  que PowerPoint propose de "reparer" alors que le zip et le XML restent
  bien formes : c'est le piege classique du XML fabrique a la main (masque,
  theme, embarquement de fontes).

Code de sortie non nul si une regle est violee. Corriger le plan JSON (ou le moteur
si c'est une regression de rendu) puis re-rendre.

## 2. Relecture visuelle

Le controle automatique ne voit pas les chevauchements ni les respirations bancales.
Si LibreOffice est disponible :

```bash
soffice --headless --convert-to pdf deck.pptx
pdftoppm -jpeg -r 110 deck.pdf slide
```

Sinon, ouvrir le `.pptx` dans PowerPoint (`open deck.pptx` sur macOS) : c'est de
toute facon le rendu de reference, puisque la police est embarquee et les graphiques
sont natifs.

Points a controler : chevauchements, pied de page percute par le contenu, colonnes
mal alignees, cartes qui se touchent, capture ecrasee, libelle de KPI tronque.

S'arreter apres un cycle de correction, sauf defaut majeur (debordement,
chevauchement, contenu manquant).

Note : la charte impose Quicksand (Bold pour les titres, Regular pour le corps). Le
moteur embarque les deux fontes dans le `.pptx`, le rendu est donc fidele chez un
destinataire qui ne les a pas installees. Aucune serif n'est toleree.
