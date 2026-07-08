"""oz_deck - Moteur de generation de PowerPoint chartes The Oz."""
from .engine import build
from .catalog import validate, LAYOUT_CATALOG, DECK_SCHEMA, THEMES

__version__ = "0.1.0"
__all__ = ["build", "validate", "LAYOUT_CATALOG", "DECK_SCHEMA", "THEMES"]
