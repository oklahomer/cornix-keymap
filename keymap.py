"""The keymap itself.  This file is the source of truth.

Everything here is a literal.  There is no logic: ``gen_vil.py`` turns these
layers into ``build/oklahomer.vil`` and ``render.py`` turns any ``.vil`` back
into the diagrams below, so the picture and the data can never drift apart.

How to read a layer
-------------------
Both halves are written **visually, left to right**, exactly as the keys sit on
the desk.  On the right half that means inner-to-outer; the matrix stores that
row reversed, and ``cornix.to_storage_right`` is the only code that knows it.

``left_bottom`` and ``right_bottom`` are six keycodes each: the three flat keys
under the outer columns, then the three angled thumb-arc keys.

``~`` in the diagrams is ``KC_TRNS`` (falls through to the layer below) and a
blank cell is ``KC_NO``.
"""

from cornix import KC_NO as XX
from cornix import KC_TRNS as __
from cornix import Layer

# Layer indices.  The names match the ErgoDox keymap this was ported from.
BASE, SYMB, MDIA = 0, 1, 2


BASE_LAYER = Layer(
    index=BASE,
    name="BASE",
    doc=r"""
,-----+-----+-----+-----+-----+-----.                 ,-----+-----+-----+-----+-----+-----.
| Tab |  Q  |  W  |  E  |  R  |  T  |                 |  Y  |  U  |  I  |  O  |  P  |BkSp |
|-----+-----+-----+-----+-----+-----|                 |-----+-----+-----+-----+-----+-----|
|LCtrl|  A  |  S  |  D  |  F  |  G  |                 |  H  |  J  |  K  |  L  |  ;  |Enter|
|-----+-----+-----+-----+-----+-----+-----.     ,-----+-----+-----+-----+-----+-----+-----|
|LShft|  Z  |  X  |  C  |  V  |  B  |Opt+ |     |SLEEP|  N  |  M  |  ,  |  .  |  /  |RShft|
`-----+-----+-----+-----+-----+-----|Space|     |     |-----+-----+-----+-----+-----+-----'
                                    `-----'     `-----'
                                     [2,6]       [5,6]      <- encoder push-buttons
   ,-----+-----+-----. ,-----+-----+-----.   ,-----+-----+-----. ,-----+-----+-----.
   |LAlt |     | L2  | | L1  |Esc /|LGui |   |RGui |Spc /| L1  | | L2  |     |RAlt |
   |     |     |     | |     |LShft|     |   |     |LCtrl|     | |     |     |     |
   `-----+-----+-----' `-----+-----+-----'   `-----+-----+-----' `-----+-----+-----'
     3,0   3,1   3,2     3,3   3,4   3,5       7,5   7,4   7,3     7,2   7,1   7,0

Esc/LShft and Spc/LCtrl are mod-tap keys: tapped they send Escape and Space,
held while another key goes down they act as Left Shift and Left Control.  See
adr/0004 for why that behaviour lives in the firmware, and README.md for the
four QMK Settings values it depends on.
""",
    left_main=[
        ["KC_TAB",    "KC_Q", "KC_W", "KC_E", "KC_R", "KC_T"],
        ["KC_LCTRL",  "KC_A", "KC_S", "KC_D", "KC_F", "KC_G"],
        ["KC_LSHIFT", "KC_Z", "KC_X", "KC_C", "KC_V", "KC_B"],
    ],
    #             3,0        3,1  3,2      3,3      3,4                  3,5
    left_bottom=["KC_LALT",  XX,  "MO(2)", "MO(1)", "LSFT_T(KC_ESCAPE)", "KC_LGUI"],
    left_encoder="LALT(KC_SPACE)",
    right_main=[
        ["KC_Y", "KC_U", "KC_I",     "KC_O",   "KC_P",      "KC_BSPACE"],
        ["KC_H", "KC_J", "KC_K",     "KC_L",   "KC_SCOLON", "KC_ENTER"],
        ["KC_N", "KC_M", "KC_COMMA", "KC_DOT", "KC_SLASH",  "KC_RSHIFT"],
    ],
    #              7,5         7,4                  7,3      7,2      7,1  7,0
    right_bottom=["KC_RGUI",  "LCTL_T(KC_SPACE)",  "MO(1)", "MO(2)",  XX,  "KC_RALT"],
    right_encoder="KC_SLEP",
)


SYMB_LAYER = Layer(
    index=SYMB,
    name="SYMB",
    doc=r"""
,-----+-----+-----+-----+-----+-----.                 ,-----+-----+-----+-----+-----+-----.
|  ~  |  1  |  2  |  3  |  4  |  5  |                 |  6  |  7  |  8  |  9  |  0  |  ~  |
|-----+-----+-----+-----+-----+-----|                 |-----+-----+-----+-----+-----+-----|
|  ~  | Tab |  `  |  \  |  "  |BkSp |                 |     |  -  |  =  |  [  |  ]  |  ~  |
|-----+-----+-----+-----+-----+-----+-----.     ,-----+-----+-----+-----+-----+-----+-----|
|  ~  |     |     |Ctl+[|     |     |RAl+M|     |     |     |     |  ~  |  ~  |  ~  |  ~  |
`-----+-----+-----+-----+-----+-----|     |     |     |-----+-----+-----+-----+-----+-----'
                                    `-----'     `-----'
   ,-----+-----+-----. ,-----+-----+-----.   ,-----+-----+-----. ,-----+-----+-----.
   |  ~  |     |     | |     |  ~  |  ~  |   |  ~  |  ~  |     | |  ~  |  ~  |  ~  |
   `-----+-----+-----' `-----+-----+-----'   `-----+-----+-----' `-----+-----+-----'

Digits sit on the QWERTY row, which is the whole reason this board can lose a
number row without losing anything (adr/0005).  Hold the layer key on the half
opposite the digits you are typing.  RAl+M is Mission Control, delivered as a
Right Option chord for the mapping software to catch (adr/0003).
""",
    left_main=[
        [__, "KC_1",   "KC_2",     "KC_3",       "KC_4",     "KC_5"],
        [__, "KC_TAB", "KC_GRAVE", "KC_BSLASH",  "KC_QUOTE", "KC_BSPACE"],
        [__, XX,       XX,         "LCTL(KC_LBRACKET)", XX,  XX],
    ],
    left_bottom=[__, XX, XX, XX, __, __],
    left_encoder="RALT(KC_M)",
    right_main=[
        ["KC_6", "KC_7",     "KC_8",     "KC_9",         "KC_0",           __],
        [XX,     "KC_MINUS", "KC_EQUAL", "KC_LBRACKET",  "KC_RBRACKET",    __],
        [XX,     XX,         __,         __,             __,               __],
    ],
    right_bottom=[__, __, __, __, __, __],
    right_encoder=XX,
)


MDIA_LAYER = Layer(
    index=MDIA,
    name="MDIA",
    doc=r"""
,-----+-----+-----+-----+-----+-----.                 ,-----+-----+-----+-----+-----+-----.
|USR00|  F1 |  F2 |  F3 |  F4 |  F5 |                 |  F6 |  F7 |  F8 |  F9 | F10 |     |
|-----+-----+-----+-----+-----+-----|                 |-----+-----+-----+-----+-----+-----|
|USR01|Vol- |Vol+ |Mute |     |BkSp |                 |MsLft|MsDwn|MsUp |MsRgt| F11 |     |
|-----+-----+-----+-----+-----+-----+-----.     ,-----+-----+-----+-----+-----+-----+-----|
|USR02|     |     |     |     |     |     |     |     |     |Lclk |Rclk |     | F12 |     |
`-----+-----+-----+-----+-----+-----|     |     |     |-----+-----+-----+-----+-----+-----'
                                    `-----'     `-----'
   ,-----+-----+-----. ,-----+-----+-----.   ,-----+-----+-----. ,-----+-----+-----.
   |BOOT |     |     | |     |  ~  |  ~  |   |  ~  |  ~  |     | |     |     |     |
   `-----+-----+-----' `-----+-----+-----'   `-----+-----+-----' `-----+-----+-----'

F10, F11 and F12 stack vertically in the same column so that the whole F-row is
reachable without leaving the home position (adr/0005).  USR00-02 are the
firmware's own custom keycodes, kept from the stock keymap (adr/0010).  BOOT is
the bootloader entry used when updating firmware; it needs the layer key held,
so it cannot be hit by accident.
""",
    left_main=[
        ["USER00", "KC_F1",   "KC_F2",   "KC_F3",   "KC_F4", "KC_F5"],
        ["USER01", "KC_VOLD", "KC_VOLU", "KC_MUTE", XX,      "KC_BSPACE"],
        ["USER02", XX,        XX,        XX,        XX,      XX],
    ],
    left_bottom=["QK_BOOT", XX, XX, XX, __, __],
    left_encoder=XX,
    right_main=[
        ["KC_F6",   "KC_F7",    "KC_F8",    "KC_F9",    "KC_F10", XX],
        ["KC_MS_L", "KC_MS_D",  "KC_MS_U",  "KC_MS_R",  "KC_F11", XX],
        [XX,        "KC_BTN1",  "KC_BTN2",  XX,         "KC_F12", XX],
    ],
    right_bottom=[__, __, XX, XX, XX, XX],
    right_encoder=XX,
)


LAYERS = (BASE_LAYER, SYMB_LAYER, MDIA_LAYER)


# --------------------------------------------------------------------------
# QMK Settings written alongside the layout
# --------------------------------------------------------------------------
# Ids are Vial's qmk_settings numbers; see README.md for what each one does and
# adr/0004 for why these four values in particular.
QMK_SETTINGS = {
    "2": 50,     # combo timeout, stock value
    "6": 1000,   # one-shot timeout, stock value
    "7": 200,    # tapping term: match the ErgoDox, which ran the QMK default
    "18": 20,    # tap code delay, stock value
    "19": 20,    # tap hold caps delay, stock value
    "22": 0,     # permissive hold OFF: pick exactly one hold-decision rule
    "23": 1,     # hold on other key press ON: decide on the event, not a timer
    "26": 0,     # chordal hold OFF: same-hand chords must still produce a hold
    "27": 0,     # flow tap OFF: never suppress a hold just because typing is fast
}


# --------------------------------------------------------------------------
# Port ledger
# --------------------------------------------------------------------------
# Every keycode the ErgoDox keymap used, and what became of it.  ``tests`` walks
# this table and fails if a claim stops being true, so a key cannot quietly go
# missing during a refactor.
#
#   ("kept",     reason)      -- appears verbatim in LAYERS
#   ("wrapped",  new_keycode) -- survives, but wrapped; new_keycode must appear
#   ("replaced", new_keycode) -- the intent survives under a different keycode
#   ("dropped",  reason)      -- deliberately gone
KEPT = "kept"
WRAPPED = "wrapped"
REPLACED = "replaced"
DROPPED = "dropped"

ERGODOX_DISPOSITION: dict[str, tuple[str, str]] = {
    # -- alphabet, digits and punctuation ---------------------------------
    **{f"KC_{c}": (KEPT, "alpha block is 1:1") for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    **{f"KC_{d}": (KEPT, "digits live on the SYMB QWERTY row") for d in "1234567890"},
    **{f"KC_F{n}": (KEPT, "F-keys live on the MDIA QWERTY row") for n in range(1, 13)},
    "KC_TAB": (KEPT, ""),
    "KC_BSPACE": (KEPT, ""),
    "KC_ENTER": (KEPT, "right pinky, home row: position and finger unchanged"),
    "KC_SCOLON": (KEPT, ""),
    "KC_COMMA": (KEPT, ""),
    "KC_DOT": (KEPT, ""),
    "KC_SLASH": (KEPT, ""),
    "KC_GRAVE": (KEPT, ""),
    "KC_BSLASH": (KEPT, ""),
    "KC_QUOTE": (KEPT, ""),
    "KC_MINUS": (KEPT, ""),
    "KC_EQUAL": (KEPT, ""),
    "KC_LBRACKET": (KEPT, ""),
    "KC_RBRACKET": (KEPT, ""),
    "KC_TRNS": (KEPT, ""),
    "KC_NO": (KEPT, ""),
    # -- modifiers ---------------------------------------------------------
    "KC_LCTRL": (KEPT, "left pinky home row, not Caps Lock"),
    "KC_LSHIFT": (KEPT, ""),
    "KC_RSHIFT": (KEPT, ""),
    "KC_LALT": (KEPT, "bottom row, outermost"),
    "KC_RALT": (KEPT, "bottom row, outermost; the launcher chords need it"),
    "KC_LGUI": (KEPT, "left thumb"),
    "KC_RGUI": (KEPT, "right thumb, still a distinct key from LGUI"),
    # -- dual-role keys ----------------------------------------------------
    "KC_ESCAPE": (WRAPPED, "LSFT_T(KC_ESCAPE)"),
    "KC_SPACE": (WRAPPED, "LCTL_T(KC_SPACE)"),
    # -- layer keys --------------------------------------------------------
    "MO(1)": (KEPT, "on both thumb arcs"),
    "MO(2)": (KEPT, "on both flat bottom rows"),
    "MO(0)": (DROPPED, "belonged to the APP layer, which is gone"),
    "OSL(3)": (DROPPED, "APP layer removed; press Right Option + letter instead"),
    # -- chords ------------------------------------------------------------
    "LALT(KC_SPACE)": (KEPT, "moved to the left encoder push"),
    "LALT(LGUI(KC_POWER))": (REPLACED, "KC_SLEP"),
    "LCTL(KC_LBRACKET)": (KEPT, "must emit LEFT control"),
    "RALT(KC_M)": (KEPT, "mission control, moved to the left encoder push on SYMB"),
    "LCTL(KC_1)": (DROPPED, "desktop switching, no longer used"),
    "LCTL(KC_2)": (DROPPED, "desktop switching, no longer used"),
    "RALT(KC_T)": (DROPPED, "APP layer removed; Right Option + T does the same"),
    "RALT(KC_S)": (DROPPED, "APP layer removed; Right Option + S does the same"),
    "RALT(KC_G)": (DROPPED, "APP layer removed; Right Option + G does the same"),
    "RALT(KC_C)": (DROPPED, "APP layer removed; Right Option + C does the same"),
    "RALT(KC_I)": (DROPPED, "APP layer removed; Right Option + I does the same"),
    "RALT(KC_L)": (DROPPED, "APP layer removed; Right Option + L does the same"),
    # -- media, mouse, firmware -------------------------------------------
    "KC_VOLD": (KEPT, ""),
    "KC_VOLU": (KEPT, ""),
    "KC_MUTE": (KEPT, ""),
    "KC_MS_L": (KEPT, ""),
    "KC_MS_R": (KEPT, ""),
    "KC_MS_U": (KEPT, ""),
    "KC_MS_D": (KEPT, ""),
    "KC_BTN1": (KEPT, ""),
    "KC_BTN2": (KEPT, ""),
    "QK_BOOT": (KEPT, "MDIA bottom-left, same slot as before"),
}
