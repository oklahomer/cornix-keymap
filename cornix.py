"""Geometry, vocabulary and .vil I/O for the Cornix LP keyboard.

This module knows three things and nothing else:

1. The physical shape of the board and how it maps onto the 8x7 matrix that
   the firmware and Vial exchange.
2. Which keycode strings are legal.
3. How to read and write a ``.vil`` file.

Every function here is pure: nothing is mutated in place, callers always get a
fresh object back.  ``keymap.py`` holds the keymap itself and contains no logic.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable, NamedTuple, Sequence

# --------------------------------------------------------------------------
# Matrix geometry
# --------------------------------------------------------------------------
# The Cornix reports an 8 x 7 matrix.  Rows 0-3 are the left half, rows 4-7 the
# right half.  Column 6 exists only on rows 2 and 5 -- those two slots are the
# encoder push-buttons.  Every other column 6 slot must stay -1 (unused) or the
# firmware rejects the layout.
#
#   LEFT                                                RIGHT
#   row0   0,0  0,1  0,2  0,3  0,4  0,5                 4,5  4,4  4,3  4,2  4,1  4,0
#   row1   1,0  1,1  1,2  1,3  1,4  1,5                 5,5  5,4  5,3  5,2  5,1  5,0
#   row2   2,0  2,1  2,2  2,3  2,4  2,5  (2,6)   (5,6)  6,5  6,4  6,3  6,2  6,1  6,0
#   row3   3,0  3,1  3,2      3,3 3,4 3,5         7,5 7,4 7,3      7,2  7,1  7,0
#                             `- thumb arc -'     `- thumb arc -'
#
# Column 0 is the *outermost* (pinky side) column on BOTH halves, which means
# the right half is stored in reverse visual order.  `to_storage_right` is the
# only place in this repository that knows that.

ROWS = 8
COLS = 7
N_LAYERS = 10
MAIN_COLS = 6

LEFT_ROWS = (0, 1, 2, 3)
RIGHT_ROWS = (4, 5, 6, 7)

ENCODER_PUSH = {"left": (2, 6), "right": (5, 6)}
DEAD_SLOTS = frozenset((row, 6) for row in (0, 1, 3, 4, 6, 7))
UNUSED = -1

# Layers this repository owns.  Layers 3-9 are left exactly as the vendor
# shipped them, which is how the stock custom keycodes survive a rebuild.
OWNED_LAYERS = (0, 1, 2)

KC_NO = "KC_NO"
KC_TRNS = "KC_TRNS"

# Human labels for slots, used by the diff output.
SLOT_NAMES = {
    (2, 6): "left encoder push",
    (5, 6): "right encoder push",
    (3, 0): "left bottom, outermost",
    (3, 1): "left bottom, pinky",
    (3, 2): "left bottom, ring",
    (3, 3): "left thumb arc, outer",
    (3, 4): "left thumb arc, middle",
    (3, 5): "left thumb arc, inner",
    (7, 0): "right bottom, outermost",
    (7, 1): "right bottom, pinky",
    (7, 2): "right bottom, ring",
    (7, 3): "right thumb arc, outer",
    (7, 4): "right thumb arc, middle",
    (7, 5): "right thumb arc, inner",
}


# --------------------------------------------------------------------------
# QMK Settings (Vial "qmk_settings"), keyed by the numeric ids Vial uses
# --------------------------------------------------------------------------
QMK_SETTING_NAMES = {
    "2": "Combo timeout (ms)",
    "6": "One-shot timeout (ms)",
    "7": "Tapping Term (ms)",
    "18": "Tap Code Delay (ms)",
    "19": "Tap Hold Caps Delay (ms)",
    "22": "Permissive Hold",
    "23": "Hold On Other Key Press",
    "26": "Chordal Hold",
    "27": "Flow Tap (ms)",
}


# --------------------------------------------------------------------------
# Keycode vocabulary
# --------------------------------------------------------------------------
# Vial on this firmware speaks the *legacy* QMK aliases (KC_LSHIFT, not
# KC_LSFT).  A string Vial cannot parse silently becomes KC_NO on the board, so
# the generator refuses to emit anything outside this vocabulary.
#
# The names come from Vial's own keycode table (vial-gui, keycodes_v6), and the
# spellings are the ones Vial itself writes on export, so that a layout exported
# from the GUI compares equal to the generated artifact.  Two rules follow from
# how Vial serialises a keycode, and both are enforced below:
#
# - A chord with more than one modifier has a single combined name.  Vial writes
#   Ctrl+Gui+Q as LCG(KC_Q), never as LCTL(LGUI(KC_Q)), so modifier wrappers do
#   not nest here either.
# - A keycode with no name at all is written as a bare hex string.  Nothing in
#   this keymap needs that, but see adr/0007 for the one that nearly did.

_ALPHA = {f"KC_{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
_DIGIT = {f"KC_{d}" for d in "1234567890"}
_FKEY = {f"KC_F{n}" for n in range(1, 25)}
_NAMED = {
    KC_NO, KC_TRNS,
    "KC_TAB", "KC_ESCAPE", "KC_SPACE", "KC_BSPACE", "KC_ENTER", "KC_DELETE",
    "KC_CAPSLOCK", "KC_APPLICATION", "KC_INSERT", "KC_HOME", "KC_END", "KC_PGUP", "KC_PGDOWN",
    "KC_LCTRL", "KC_LSHIFT", "KC_LALT", "KC_LGUI",
    "KC_RCTRL", "KC_RSHIFT", "KC_RALT", "KC_RGUI",
    "KC_MINUS", "KC_EQUAL", "KC_LBRACKET", "KC_RBRACKET", "KC_BSLASH",
    "KC_SCOLON", "KC_QUOTE", "KC_GRAVE", "KC_COMMA", "KC_DOT", "KC_SLASH",
    "KC_UP", "KC_DOWN", "KC_LEFT", "KC_RIGHT",
    "KC_MUTE", "KC_VOLU", "KC_VOLD",
    "KC_PWR", "KC_SLEP", "KC_WAKE", "KC_EJCT",
    "KC_MS_L", "KC_MS_R", "KC_MS_U", "KC_MS_D",
    "KC_BTN1", "KC_BTN2", "KC_BTN3", "KC_WH_U", "KC_WH_D", "KC_WH_L", "KC_WH_R",
    "QK_BOOT",
}
BASIC_KEYCODES = frozenset(_ALPHA | _DIGIT | _FKEY | _NAMED)

SIMPLE_MODIFIERS = ("LCTL", "LSFT", "LALT", "LGUI", "RCTL", "RSFT", "RALT", "RGUI")
# One name per modifier *combination*: LCG is Ctrl+Gui, LAG is Alt+Gui, MEH is
# Ctrl+Shift+Alt, HYPR adds Gui.  Vial always writes the combined name.
COMBINED_MODIFIERS = ("C_S", "HYPR", "LAG", "LCA", "LCAG", "LCG", "LSA", "MEH", "RCG", "SGUI")
MODIFIER_WRAPPERS = SIMPLE_MODIFIERS + COMBINED_MODIFIERS
MODTAP_WRAPPERS = tuple(f"{m}_T" for m in MODIFIER_WRAPPERS) + ("ALL_T", "RCAG_T", "RSA_T")

_RE_LAYER = re.compile(r"^(MO|OSL|TO|TG|TT|DF)\((\d)\)$")
_RE_USER = re.compile(r"^USER(\d{2})$")
_RE_WRAP = re.compile(r"^([A-Z]+(?:_T)?)\((.+)\)$")

# ErgoDox (modern QMK) name -> the legacy alias this firmware expects.
MODERN_TO_LEGACY = {
    "KC_ESC": "KC_ESCAPE", "KC_LSFT": "KC_LSHIFT", "KC_RSFT": "KC_RSHIFT",
    "KC_LCTL": "KC_LCTRL", "KC_RCTL": "KC_RCTRL", "KC_BSPC": "KC_BSPACE",
    "KC_ENT": "KC_ENTER", "KC_SCLN": "KC_SCOLON", "KC_BSLS": "KC_BSLASH",
    "KC_QUOT": "KC_QUOTE", "KC_GRV": "KC_GRAVE", "KC_LBRC": "KC_LBRACKET",
    "KC_RBRC": "KC_RBRACKET", "KC_MINS": "KC_MINUS", "KC_EQL": "KC_EQUAL",
    "KC_COMM": "KC_COMMA", "KC_SLSH": "KC_SLASH", "KC_DEL": "KC_DELETE",
    "KC_CAPS": "KC_CAPSLOCK", "KC_SPC": "KC_SPACE",
}


#: Which modifiers each wrapper name stands for.
MODIFIER_ATOMS = {
    "LCTL": ("KC_LCTRL",), "LSFT": ("KC_LSHIFT",), "LALT": ("KC_LALT",), "LGUI": ("KC_LGUI",),
    "RCTL": ("KC_RCTRL",), "RSFT": ("KC_RSHIFT",), "RALT": ("KC_RALT",), "RGUI": ("KC_RGUI",),
    "C_S": ("KC_LCTRL", "KC_LSHIFT"),
    "LCA": ("KC_LCTRL", "KC_LALT"),
    "LCG": ("KC_LCTRL", "KC_LGUI"),
    "LSA": ("KC_LSHIFT", "KC_LALT"),
    "LAG": ("KC_LALT", "KC_LGUI"),
    "SGUI": ("KC_LSHIFT", "KC_LGUI"),
    "LCAG": ("KC_LCTRL", "KC_LALT", "KC_LGUI"),
    "MEH": ("KC_LCTRL", "KC_LSHIFT", "KC_LALT"),
    "HYPR": ("KC_LCTRL", "KC_LSHIFT", "KC_LALT", "KC_LGUI"),
    "RCG": ("KC_RCTRL", "KC_RGUI"),
}


class KeycodeError(ValueError):
    """Raised when a keycode string is outside the accepted vocabulary."""


def to_legacy(keycode: str) -> str:
    """Translate a modern QMK alias to the legacy alias this firmware uses."""
    return MODERN_TO_LEGACY.get(keycode, keycode)


def is_valid_keycode(keycode: str) -> bool:
    """True when Vial on this firmware is expected to parse ``keycode``."""
    if keycode in BASIC_KEYCODES or _RE_LAYER.match(keycode) or _RE_USER.match(keycode):
        return True
    wrapped = _RE_WRAP.match(keycode)
    if not wrapped:
        return False
    wrapper, inner = wrapped.group(1), wrapped.group(2)
    if wrapper in MODTAP_WRAPPERS:
        # A mod-tap holds a plain key, never another wrapper.
        return inner in BASIC_KEYCODES
    if wrapper in MODIFIER_WRAPPERS:
        # Deliberately not recursive: a two-modifier chord has its own name in
        # Vial (LCG, LAG, MEH...), and writing it as nested wrappers would make
        # the artifact differ from what Vial exports for the same key.
        return inner in BASIC_KEYCODES
    return False


def validate_keycode(keycode: str, where: str) -> str:
    """Return ``keycode`` unchanged, or raise with the offending location."""
    if not is_valid_keycode(keycode):
        raise KeycodeError(f"{where}: unknown keycode {keycode!r}")
    return keycode


def atoms(keycode: str) -> frozenset[str]:
    """Every basic keycode reachable inside ``keycode``.

    ``LCG(KC_Q)`` yields ``{KC_LCTRL, KC_LGUI, KC_Q}`` and ``LSFT_T(KC_ESCAPE)``
    yields ``{KC_LSHIFT, KC_ESCAPE}``, so a coverage test can ask "did this
    ErgoDox key survive anywhere" without caring how it is now wrapped.
    """
    if keycode in BASIC_KEYCODES:
        return frozenset({keycode})
    if _RE_LAYER.match(keycode) or _RE_USER.match(keycode):
        return frozenset({keycode})
    wrapped = _RE_WRAP.match(keycode)
    if not wrapped:
        return frozenset()
    wrapper, inner = wrapped.group(1), wrapped.group(2)
    base = wrapper[:-2] if wrapper.endswith("_T") else wrapper
    return frozenset(MODIFIER_ATOMS.get(base, ())) | atoms(inner)


# --------------------------------------------------------------------------
# Layer definition
# --------------------------------------------------------------------------
class Layer(NamedTuple):
    """One layer, written the way the keyboard looks.

    ``left_main`` / ``right_main`` are three rows of six keycodes, and
    ``left_bottom`` / ``right_bottom`` are six keycodes: the three flat keys
    then the three thumb-arc keys.  **Both halves are written visually, left to
    right.**  On the right half that means inner-to-outer, and
    ``to_storage_right`` reverses it on the way into the matrix.
    """

    index: int
    name: str
    doc: str
    left_main: Sequence[Sequence[str]]
    left_bottom: Sequence[str]
    left_encoder: str
    right_main: Sequence[Sequence[str]]
    right_bottom: Sequence[str]
    right_encoder: str


def to_storage_right(visual_row: Sequence[str]) -> list[str]:
    """Turn a visually-ordered right-half row into matrix column order."""
    return list(reversed(list(visual_row)))


def _check_row(row: Sequence[str], where: str) -> list[str]:
    if len(row) != MAIN_COLS:
        raise ValueError(f"{where}: expected {MAIN_COLS} keycodes, got {len(row)}")
    return [validate_keycode(kc, f"{where}[{i}]") for i, kc in enumerate(row)]


def layer_to_matrix(layer: Layer) -> list[list[Any]]:
    """Render one :class:`Layer` as the 8x7 matrix the ``.vil`` stores."""
    tag = f"layer {layer.index} ({layer.name})"
    left = [_check_row(r, f"{tag} left_main[{i}]") for i, r in enumerate(layer.left_main)]
    right = [_check_row(r, f"{tag} right_main[{i}]") for i, r in enumerate(layer.right_main)]
    if len(left) != 3 or len(right) != 3:
        raise ValueError(f"{tag}: each half needs exactly 3 main rows")
    left_bottom = _check_row(layer.left_bottom, f"{tag} left_bottom")
    right_bottom = _check_row(layer.right_bottom, f"{tag} right_bottom")
    left_enc = validate_keycode(layer.left_encoder, f"{tag} left_encoder")
    right_enc = validate_keycode(layer.right_encoder, f"{tag} right_encoder")

    return [
        left[0] + [UNUSED],
        left[1] + [UNUSED],
        left[2] + [left_enc],
        left_bottom + [UNUSED],
        to_storage_right(right[0]) + [UNUSED],
        to_storage_right(right[1]) + [right_enc],
        to_storage_right(right[2]) + [UNUSED],
        to_storage_right(right_bottom) + [UNUSED],
    ]


def matrix_to_visual(matrix: Sequence[Sequence[Any]]) -> dict[str, Any]:
    """Inverse of :func:`layer_to_matrix`, for round-trip checks and rendering."""
    return {
        "left_main": [list(matrix[r][:MAIN_COLS]) for r in (0, 1, 2)],
        "left_bottom": list(matrix[3][:MAIN_COLS]),
        "left_encoder": matrix[2][6],
        "right_main": [to_storage_right(matrix[r][:MAIN_COLS]) for r in (4, 5, 6)],
        "right_bottom": to_storage_right(matrix[7][:MAIN_COLS]),
        "right_encoder": matrix[5][6],
    }


# --------------------------------------------------------------------------
# .vil I/O
# --------------------------------------------------------------------------
def load_vil(path: str) -> dict[str, Any]:
    """Read a ``.vil`` file."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def dump_vil(data: dict[str, Any], path: str, indent: int | None = 1) -> None:
    """Write a ``.vil`` file.

    ``indent=1`` keeps the artifact line-diffable in git.  Vial itself writes
    minified JSON; if a future firmware ever refuses the pretty-printed form,
    pass ``indent=None``.
    """
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=indent)
        handle.write("\n")


def check_shape(data: dict[str, Any]) -> None:
    """Fail loudly if a ``.vil`` does not have the shape this board expects."""
    layout = data.get("layout")
    if not isinstance(layout, list) or len(layout) != N_LAYERS:
        raise ValueError(f"layout must hold {N_LAYERS} layers, got {len(layout or [])}")
    for index, layer in enumerate(layout):
        if len(layer) != ROWS:
            raise ValueError(f"layer {index}: expected {ROWS} rows, got {len(layer)}")
        for row_index, row in enumerate(layer):
            if len(row) != COLS:
                raise ValueError(
                    f"layer {index} row {row_index}: expected {COLS} columns, got {len(row)}"
                )
            for col_index, slot in enumerate(row):
                if (row_index, col_index) in DEAD_SLOTS and slot != UNUSED:
                    raise ValueError(
                        f"layer {index} [{row_index}][{col_index}] is not wired; "
                        f"expected {UNUSED}, got {slot!r}"
                    )


def iter_slots(layout: Sequence[Sequence[Sequence[Any]]]) -> Iterable[tuple[int, int, int, Any]]:
    """Yield ``(layer, row, col, value)`` for every slot in a layout."""
    for layer_index, layer in enumerate(layout):
        for row_index, row in enumerate(layer):
            for col_index, value in enumerate(row):
                yield layer_index, row_index, col_index, value
