#!/usr/bin/env python3
"""Generate ``build/oklahomer.vil`` from ``keymap.py``.

The generator never builds a ``.vil`` from scratch.  It loads the pristine
vendor export as a template and replaces only the layers this repository owns
plus the QMK Settings block.  Everything else -- the uid the firmware matches
on, the protocol numbers, the macro/combo/tap-dance array sizes, the encoder
rotation actions and layers 3-9 -- is carried over untouched, so a rebuild can
never invent a shape the firmware rejects or delete a keycode the vendor put
there.  See adr/0010.
"""

from __future__ import annotations

import argparse
import os
import sys

import cornix
import keymap

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "vendor", "cornix-default-keymap.vil")
OUTPUT = os.path.join(HERE, "build", "oklahomer.vil")


def build(template: dict) -> dict:
    """Return a new ``.vil`` document: the template with our layers merged in."""
    owned = {layer.index: cornix.layer_to_matrix(layer) for layer in keymap.LAYERS}
    unknown = set(owned) - set(cornix.OWNED_LAYERS)
    if unknown:
        raise ValueError(f"keymap.py defines layers outside OWNED_LAYERS: {sorted(unknown)}")

    layout = [
        owned.get(index, template["layout"][index])
        for index in range(cornix.N_LAYERS)
    ]
    result = {**template, "layout": layout, "settings": dict(keymap.QMK_SETTINGS)}
    cornix.check_shape(result)
    _check_vocabulary(result)
    return result


def _check_vocabulary(document: dict) -> None:
    """Refuse to emit a keycode Vial would not understand.

    A string Vial cannot parse does not raise an error on the board: it becomes
    KC_NO, and the key is silently dead.  Failing the build is the only place
    that mistake is cheap to catch.
    """
    for layer, row, col, value in cornix.iter_slots(document["layout"]):
        if value == cornix.UNUSED:
            continue
        cornix.validate_keycode(value, f"layer {layer} [{row}][{col}]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--template", default=TEMPLATE, help="pristine vendor export")
    parser.add_argument("--output", default=OUTPUT, help="generated artifact")
    parser.add_argument(
        "--check", action="store_true",
        help="build in memory and report whether the artifact on disk matches",
    )
    args = parser.parse_args(argv)

    template = cornix.load_vil(args.template)
    cornix.check_shape(template)
    document = build(template)

    if args.check:
        existing = cornix.load_vil(args.output)
        if existing != document:
            print(f"{args.output} is stale; run 'make build'", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date")
        return 0

    cornix.dump_vil(document, args.output)
    owned = ", ".join(f"{layer.index}:{layer.name}" for layer in keymap.LAYERS)
    print(f"wrote {args.output} (layers {owned}; layers 3-9 from the vendor template)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
