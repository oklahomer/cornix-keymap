#!/usr/bin/env python3
"""Render a ``.vil`` as readable diagrams, or diff two of them.

Two modes:

``render.py FILE``
    Print one section per layer: the keys laid out the way the board looks,
    followed by the raw matrix table you can compare against Vial cell by cell.

``render.py FILE --diff OTHER``
    Compare two ``.vil`` documents semantically -- JSON formatting differences
    are ignored -- and exit non-zero if anything differs.  This is how a layout
    edited in the Vial GUI is checked against the committed artifact.
"""

from __future__ import annotations

import argparse
import re
import sys

import cornix

# --------------------------------------------------------------------------
# Labels
# --------------------------------------------------------------------------
CELL = 6

SHORT = {
    cornix.KC_TRNS: "~", cornix.KC_NO: "",
    "KC_TAB": "Tab", "KC_ESCAPE": "Esc", "KC_SPACE": "Spc", "KC_BSPACE": "BkSp",
    "KC_ENTER": "Enter", "KC_DELETE": "Del", "KC_CAPSLOCK": "Caps",
    "KC_LCTRL": "LCtrl", "KC_RCTRL": "RCtrl", "KC_LSHIFT": "LShft", "KC_RSHIFT": "RShft",
    "KC_LALT": "LAlt", "KC_RALT": "RAlt", "KC_LGUI": "LGui", "KC_RGUI": "RGui",
    "KC_MINUS": "-", "KC_EQUAL": "=", "KC_LBRACKET": "[", "KC_RBRACKET": "]",
    "KC_BSLASH": "\\", "KC_SCOLON": ";", "KC_QUOTE": "\"", "KC_GRAVE": "`",
    "KC_COMMA": ",", "KC_DOT": ".", "KC_SLASH": "/",
    "KC_UP": "Up", "KC_DOWN": "Down", "KC_LEFT": "Left", "KC_RIGHT": "Right",
    "KC_MUTE": "Mute", "KC_VOLU": "Vol+", "KC_VOLD": "Vol-",
    "KC_POWER": "Power", "KC_SYSTEM_POWER": "Power",
    "KC_MS_L": "MsLft", "KC_MS_R": "MsRgt", "KC_MS_U": "MsUp", "KC_MS_D": "MsDwn",
    "KC_BTN1": "Lclk", "KC_BTN2": "Rclk", "KC_BTN3": "Mclk",
    "KC_WH_U": "WhUp", "KC_WH_D": "WhDn", "KC_WH_L": "WhLft", "KC_WH_R": "WhRgt",
    "QK_BOOT": "BOOT",
    "LALT(LGUI(KC_POWER))": "SLEEP",
    "LALT(KC_SPACE)": "OptSpc",
    "LSFT_T(KC_ESCAPE)": "Esc/S",
    "LCTL_T(KC_SPACE)": "Spc/C",
}
MOD_SHORT = {"LCTL": "Ctl", "LSFT": "Sft", "LALT": "Opt", "LGUI": "Cmd",
             "RCTL": "RCtl", "RSFT": "RSft", "RALT": "RAlt", "RGUI": "RCmd"}
MOD_LETTER = {"LCTL": "C", "LSFT": "S", "LALT": "A", "LGUI": "G",
              "RCTL": "C", "RSFT": "S", "RALT": "A", "RGUI": "G"}

_RE_LAYER = re.compile(r"^(MO|OSL|TO|TG|TT|DF)\((\d)\)$")
_RE_USER = re.compile(r"^USER(\d{2})$")
_RE_WRAP = re.compile(r"^([A-Z]+(?:_T)?)\((.+)\)$")


def label(value) -> str:
    """A short, human-readable name for one slot."""
    if value == cornix.UNUSED:
        return "-"
    if value in SHORT:
        return SHORT[value]
    layer = _RE_LAYER.match(value)
    if layer:
        prefix = "L" if layer.group(1) == "MO" else layer.group(1)
        return f"{prefix}{layer.group(2)}"
    user = _RE_USER.match(value)
    if user:
        return f"USR{user.group(1)}"
    wrapped = _RE_WRAP.match(value)
    if wrapped:
        wrapper, inner = wrapped.group(1), wrapped.group(2)
        if wrapper.endswith("_T"):
            return f"{label(inner)}/{MOD_LETTER[wrapper[:-2]]}"[:CELL]
        return f"{MOD_SHORT[wrapper]}+{label(inner)}"[:CELL]
    if value.startswith("KC_"):
        return value[3:][:CELL]
    return value[:CELL]


def _cell(value) -> str:
    return label(value).center(CELL)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def _rule(count: int, left: str = ",", mid: str = "+", right: str = ".") -> str:
    return left + mid.join("-" * CELL for _ in range(count)) + right


def render_layer(matrix, index: int, name: str = "") -> str:
    """One layer as a visual diagram plus its raw matrix table."""
    view = cornix.matrix_to_visual(matrix)
    gap = "    "
    lines: list[str] = []

    title = f"Layer {index}" + (f" - {name}" if name else "")
    lines.append(f"### {title}")
    lines.append("")
    lines.append("```")
    top = _rule(6)
    sep = _rule(6, "|", "+", "|")
    bottom = _rule(6, "`", "+", "'")
    lines.append(top + gap + top)
    for row_index in range(3):
        left = "|" + "|".join(_cell(k) for k in view["left_main"][row_index]) + "|"
        right = "|" + "|".join(_cell(k) for k in view["right_main"][row_index]) + "|"
        lines.append(left + gap + right)
        lines.append((sep if row_index < 2 else bottom) + gap + (sep if row_index < 2 else bottom))

    # Encoder pushes sit inboard of the inner column, level with the ZXCV row.
    enc_left = label(view["left_encoder"]) or "(none)"
    enc_right = label(view["right_encoder"]) or "(none)"
    lines.append("")
    lines.append(f"  encoder push   [2,6] {enc_left:<8}   [5,6] {enc_right}")
    lines.append("")

    # Bottom row: three flat keys, then the three-key thumb arc.
    def split_line(cells, edge):
        flat = edge + edge.join(cells[:3]) + edge
        arc = edge + edge.join(cells[3:]) + edge
        return flat + "  " + arc

    def keys_line(keys):
        return split_line([_cell(k) for k in keys], "|")

    def coords_line(row):
        return split_line([f"{row},{c}".center(CELL) for c in range(6)], " ")

    rule = _rule(3) + "  " + _rule(3)
    foot = _rule(3, "`", "+", "'") + "  " + _rule(3, "`", "+", "'")
    left_coords = coords_line(3)
    # The right half is drawn inner-to-outer, so its coordinates count down.
    right_coords = split_line([f"7,{c}".center(CELL) for c in (5, 4, 3, 2, 1, 0)], " ")

    lines.append("  " + rule + gap + rule)
    lines.append("  " + keys_line(view["left_bottom"]) + gap + keys_line(view["right_bottom"]))
    lines.append("  " + foot + gap + foot)
    lines.append("  " + left_coords + gap + right_coords)
    lines.append("```")
    lines.append("")

    lines.append("| row | col0 | col1 | col2 | col3 | col4 | col5 | col6 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row_index, row in enumerate(matrix):
        side = "L" if row_index in cornix.LEFT_ROWS else "R"
        cells = " | ".join("`-`" if v == cornix.UNUSED else f"`{v}`" for v in row)
        lines.append(f"| {row_index} ({side}) | {cells} |")
    lines.append("")
    return "\n".join(lines)


def render(document: dict, names: dict[int, str], layers: list[int]) -> str:
    head = [
        "# Layers",
        "",
        "Generated by `render.py`; edit `keymap.py` and run `make render` instead.",
        "",
        "Both halves are drawn the way they sit on the desk. The matrix tables below",
        "each diagram are in storage order, so `col0` is the outermost column on both",
        "halves and the right half reads reversed compared with the picture.",
        "",
    ]
    encoders = document.get("encoder_layout") or []
    if encoders:
        first = encoders[0]
        head += [
            "Encoder rotation (unchanged from the stock keymap): "
            + ", ".join(
                f"encoder {i}: {label(pair[0])} / {label(pair[1])}"
                for i, pair in enumerate(first)
            ),
            "",
        ]
    body = [render_layer(document["layout"][i], i, names.get(i, "")) for i in layers]
    return "\n".join(head + body)


# --------------------------------------------------------------------------
# Diff
# --------------------------------------------------------------------------
def diff(current: dict, other: dict) -> list[str]:
    """Human-readable differences between two ``.vil`` documents."""
    report: list[str] = []

    for key in sorted(set(current) | set(other)):
        if key in ("layout", "settings", "encoder_layout"):
            continue
        if current.get(key) != other.get(key):
            report.append(f"field {key}: {current.get(key)!r} -> {other.get(key)!r}")

    for layer, row, col, value in cornix.iter_slots(current["layout"]):
        try:
            theirs = other["layout"][layer][row][col]
        except (IndexError, KeyError):
            report.append(f"layer {layer} [{row}][{col}]: missing in the other file")
            continue
        if value != theirs:
            where = cornix.SLOT_NAMES.get((row, col), "")
            suffix = f"  ({where})" if where else ""
            report.append(f"layer {layer} [{row}][{col}]: {value} -> {theirs}{suffix}")

    if current.get("encoder_layout") != other.get("encoder_layout"):
        report.append("encoder_layout differs")

    ours, theirs = current.get("settings", {}), other.get("settings", {})
    for qsid in sorted(set(ours) | set(theirs), key=int):
        if ours.get(qsid) != theirs.get(qsid):
            name = cornix.QMK_SETTING_NAMES.get(qsid, f"qmk_setting {qsid}")
            report.append(f"setting {qsid} ({name}): {ours.get(qsid)} -> {theirs.get(qsid)}")
    return report


def visual_literals(current: dict, other: dict) -> list[str]:
    """For every layer that differs, print the other file's rows as source literals.

    ``keymap.py`` is never rewritten automatically: the diagrams and the intent
    comments in it are the point of the file.  This just saves the retyping.
    """
    out: list[str] = []
    for layer in cornix.OWNED_LAYERS:
        if current["layout"][layer] == other["layout"][layer]:
            continue
        view = cornix.matrix_to_visual(other["layout"][layer])
        out.append(f"# layer {layer}, as written in keymap.py (visual order)")
        out.append("left_main=[")
        for row in view["left_main"]:
            out.append("    " + repr(row) + ",")
        out.append("],")
        out.append(f"left_bottom={view['left_bottom']!r},")
        out.append(f"left_encoder={view['left_encoder']!r},")
        out.append("right_main=[")
        for row in view["right_main"]:
            out.append("    " + repr(row) + ",")
        out.append("],")
        out.append(f"right_bottom={view['right_bottom']!r},")
        out.append(f"right_encoder={view['right_encoder']!r},")
        out.append("")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help=".vil to render or use as the baseline")
    parser.add_argument("--diff", metavar="OTHER", help="compare against another .vil")
    parser.add_argument("--emit", action="store_true",
                        help="with --diff, print paste-ready keymap.py literals")
    parser.add_argument("--all-layers", action="store_true",
                        help="render every layer, not just the ones this repo owns")
    args = parser.parse_args(argv)

    document = cornix.load_vil(args.file)
    cornix.check_shape(document)

    if args.diff:
        other = cornix.load_vil(args.diff)
        report = diff(document, other)
        if not report:
            print(f"no differences between {args.file} and {args.diff}")
            return 0
        print(f"{len(report)} difference(s) between {args.file} and {args.diff}:")
        for line in report:
            print(f"  {line}")
        if args.emit:
            print()
            print("\n".join(visual_literals(document, other)))
        return 1

    try:
        import keymap
        names = {layer.index: layer.name for layer in keymap.LAYERS}
    except Exception:  # rendering must work on any .vil, even without keymap.py
        names = {}
    layers = list(range(cornix.N_LAYERS)) if args.all_layers else list(cornix.OWNED_LAYERS)
    print(render(document, names, layers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
