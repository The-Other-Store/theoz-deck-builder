#!/usr/bin/env python3
"""CLI local : rendu d'un schema JSON en .pptx (utile pour tests hors MCP)."""
import json
import sys
from oz_deck import build, validate


def main():
    if len(sys.argv) < 3:
        print("usage: python cli.py <schema.json> <sortie.pptx>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        schema = json.load(f)
    errs = validate(schema)
    if errs:
        print("VALIDATION KO :", file=sys.stderr)
        for e in errs:
            print(f"  - {e['path']}: {e['error']}", file=sys.stderr)
        sys.exit(1)
    build(schema, sys.argv[2])
    print("OK ->", sys.argv[2])


if __name__ == "__main__":
    main()
