#!/usr/bin/env python3
"""CLI local : rendu d'un schema JSON en .pptx (utile pour tests hors MCP).

Les chemins d'images RELATIFS du plan sont resolus depuis le dossier du plan :
`python3 engine/cli.py tests/mon_plan.json out.pptx` marche donc depuis n'importe
quel repertoire.
"""
import json
import os
import sys
from oz_deck import build, resolve_images, validate


def main():
    if len(sys.argv) < 3:
        print("usage: python cli.py <schema.json> <sortie.pptx>", file=sys.stderr)
        sys.exit(2)
    plan = sys.argv[1]
    with open(plan, encoding="utf-8") as f:
        schema = json.load(f)
    errs = validate(schema)
    if errs:
        print("VALIDATION KO :", file=sys.stderr)
        for e in errs:
            print(f"  - {e['path']}: {e['error']}", file=sys.stderr)
        sys.exit(1)
    resolve_images(schema, os.path.dirname(os.path.abspath(plan)))
    build(schema, sys.argv[2])
    print("OK ->", sys.argv[2])


if __name__ == "__main__":
    main()
