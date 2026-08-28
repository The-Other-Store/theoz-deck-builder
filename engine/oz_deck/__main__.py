"""Point d'entree du paquet : `python -m oz_deck --export json|css`.

Equivalent a `python -m oz_deck.theme`, mais sans le RuntimeWarning que runpy
emet quand le module vise a deja ete importe par le `__init__` du paquet.
"""
from .theme import _main

raise SystemExit(_main())
