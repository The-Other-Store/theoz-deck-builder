"""oz_deck - Moteur de generation de PowerPoint chartes The Oz (charte V2)."""
from .engine import build, resolve_images
from .catalog import (validate, LAYOUT_CATALOG, DECK_SCHEMA, THEMES, TONES,
                      IGNORED_FIELDS)

__version__ = "0.6.0"   # charte V2 + retours de relecture
__all__ = ["build", "resolve_images", "validate", "LAYOUT_CATALOG", "DECK_SCHEMA",
           "THEMES", "TONES", "IGNORED_FIELDS"]
