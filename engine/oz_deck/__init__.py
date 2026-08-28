"""oz_deck - Moteur de generation de PowerPoint chartes The Oz (charte V2)."""
from .theme import CHARTE_VERSION
from .engine import build, resolve_images
from .catalog import (validate, LAYOUT_CATALOG, DECK_SCHEMA, THEMES, TONES,
                      IGNORED_FIELDS)

__version__ = "0.7.0"   # charte V2 + contrats pour consommateurs externes
__all__ = ["build", "resolve_images", "validate", "LAYOUT_CATALOG", "DECK_SCHEMA",
           "THEMES", "TONES", "IGNORED_FIELDS", "CHARTE_VERSION"]
