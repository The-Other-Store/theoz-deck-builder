# QA visuelle d'un deck

Apres `create_deck`, verifier le rendu avant livraison.

```bash
# 1. Convertir en images (LibreOffice + poppler)
soffice --headless --convert-to pdf deck.pptx
pdftoppm -jpeg -r 110 deck.pdf slide

# 2. Inspecter les images (idealement via un sous-agent aux yeux neufs)
```

Points a controler : debordement de texte hors des cadres, chevauchements, pied de
page qui percute le contenu, contraste (texte clair sur fond clair a proscrire),
marges >= 0,5 cm, alignement des colonnes, tuiles qui se touchent.

Corriger dans le plan JSON puis re-rendre. S'arreter apres un cycle de correction
sauf defaut majeur visible (debordement, chevauchement, contenu manquant).

Note : la police ecrite est Arial (substitution charte d'Helvetica) pour un rendu
fiable ; le vrai Helvetica peut etre active si deploye sur le parc.
