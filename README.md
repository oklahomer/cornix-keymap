# cornix-keymap

My keymap for the [Cornix LP](https://www.ozokeyboards.com/products/cornix-split-low-profile-split-ergonomic-keyboard),
ported from an ErgoDox EZ that ran QMK for years.

The board ships with RMK firmware that speaks the [Vial](https://get.vial.today/)
protocol, so the keymap is data rather than a firmware build: `build/oklahomer.vil`
is loaded straight into the keyboard over USB or Bluetooth. That file is generated —
the source of truth is [`keymap.py`](keymap.py), which holds the layers as literals
with a diagram of each one above it.

Why the layout looks the way it does is in [`adr/`](adr/README.md), one decision per
file.

## The keyboard

48 keys plus two encoders. Each half is a 3x6 column-staggered block, three flat
keys below the outer columns, a three-key thumb arc, and an encoder whose shaft
doubles as a push-button.

The firmware reports an 8x7 matrix. Rows 0-3 are the left half and rows 4-7 the
right half:

```
LEFT                                                RIGHT
row0   0,0  0,1  0,2  0,3  0,4  0,5                 4,5  4,4  4,3  4,2  4,1  4,0
row1   1,0  1,1  1,2  1,3  1,4  1,5                 5,5  5,4  5,3  5,2  5,1  5,0
row2   2,0  2,1  2,2  2,3  2,4  2,5  (2,6)   (5,6)  6,5  6,4  6,3  6,2  6,1  6,0
row3   3,0  3,1  3,2      3,3 3,4 3,5         7,5 7,4 7,3      7,2  7,1  7,0
                          `- thumb arc -'     `- thumb arc -'
```

Two things about that picture are easy to get wrong, and both are worth checking
before trusting any edit:

**Column 0 is the outermost column on _both_ halves.** The right half is stored in
reverse visual order, so `[4][0]` is the right little finger and `[4][5]` is the
right index finger. The stock keymap proves it: reverse its `layout[0][7]` and you
get `Space, MO(4), MO(2), Left, Down, Right` — an arrow cluster that only makes
sense reversed — with `Up` at `[6][1]` sitting directly above `Down` at `[7][1]`.

**The encoder push-buttons are `[2][6]` and `[5][6]`.** Not `[6][6]`; the right one
is a row higher than the symmetry suggests. Every other column-6 slot is unused and
must stay `-1`.

## The layers

| # | Name | Held with | Contents |
| --- | --- | --- | --- |
| 0 | BASE | — | letters, the two dual-role thumb keys, modifiers |
| 1 | SYMB | `[3][3]` / `[7][3]` | digits on the QWERTY row, punctuation on the home row |
| 2 | MDIA | `[3][2]` / `[7][2]` | `F1`-`F12`, volume, mouse keys, bootloader |

Rendered diagrams and the full matrix tables: [`docs/layers.md`](docs/layers.md).

Layers 3 to 9 are whatever the vendor shipped. This repository does not touch them.

## Building

Standard-library Python 3. No dependencies, no virtualenv.

```
make build     # keymap.py           -> build/oklahomer.vil
make render    # build/oklahomer.vil -> docs/layers.md
make test      # the test suite
make check     # rebuild everything and fail if the committed files are stale
make all       # build + render + test
```

`make build` refuses to write a keycode that Vial is not expected to parse. That
check matters more than it looks: an unparseable keycode does not raise an error on
the board, it becomes a dead key.

`make check` is also installed as a pre-commit hook, so a commit that changes
`keymap.py` without regenerating `build/` and `docs/` is rejected. Set it up again
after a fresh clone with:

```
printf '#!/bin/sh\nexec make check\n' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

## Applying it to the keyboard

Use [vial.rocks](https://vial.rocks/) in Chrome, or the desktop app from
get.vial.today. Connect over USB the first time.

1. **Back up first.** `File > Save current layout`. Keep it; it is the only way
   back if something goes wrong.
2. `File > Load saved layout` and pick `build/oklahomer.vil`. It is written to the
   board immediately — there is no flashing step.
3. Export again and run `make import FILE=<the export>`. It must report no
   differences. That is the acceptance test.
4. Set the tap-hold values in the **QMK Settings** tab (next section). A layout load
   does not necessarily carry them.

To roll back, load `vendor/cornix-default-keymap.vil`, which is the untouched
factory export.

Firmware updates reset the keymap, so keep the artifact — reloading it is the whole
recovery procedure.

## QMK Settings

Four of these decide whether the dual-role thumb keys work at all. Two of them ship
in the state that breaks them, so check the tab after every firmware update.

| id | Setting | Stock | Here | Why |
| --- | --- | --- | --- | --- |
| 7 | Tapping Term | 250 | **200** | matches the keyboard this was ported from |
| 22 | Permissive Hold | 1 | **0** | one hold-decision rule, not two overlapping ones |
| 23 | Hold On Other Key Press | 0 | **1** | decide on another key going down, not on a timer |
| 26 | Chordal Hold | 1 | **0** | it resolves same-hand chords as taps, which turns thumb-Shift plus a left-hand letter into a lowercase letter |
| 27 | Flow Tap | 120 | **0** | it forces a tap when the previous keystroke was recent — the speed-dependent misfire this design exists to avoid |
| 2 | Combo timeout | 50 | 50 | unchanged |
| 6 | One-shot timeout | 1000 | 1000 | unchanged |
| 18 | Tap Code Delay | 20 | 20 | unchanged |
| 19 | Tap Hold Caps Delay | 20 | 20 | unchanged |

Reasoning in [ADR 4](adr/0004-reproduce-dual-role-keys-with-firmware-mod-tap.md).

## The board is not the source of truth

`keymap.py` is. An edit made in the Vial GUI lands on the keyboard and nowhere else,
so it is treated as a proposal:

```
make import FILE=~/Downloads/whatever.vil
```

It diffs the export against the committed artifact, names the slots that changed,
prints the affected rows as `keymap.py` literals, and exits non-zero. Apply the
change to the source by hand — that keeps the diagram and the reason for the change
attached to it — then `make all` and commit.

## Checking it on the hardware

Worth running once after the first load, and after any change to the right half.

**Geometry.** In Vial's Matrix Tester, confirm right `Y` is `[4][5]`, right
`BackSpace` is `[4][0]`, right `Enter` is `[5][0]`, the innermost right thumb key is
`[7][5]`, and the encoder pushes are `[2][6]` and `[5][6]`. If any of these differ,
stop: the column mapping is wrong and nothing below will make sense.

**Typing.** A reversed right half produces specific wrong answers, which is what
makes these three worth typing:

| Type | Expect | Reversed gives |
| --- | --- | --- |
| `qwertyuiop` | `qwertyuiop` | `qwertpoiuy` |
| `asdfghjkl;` | `asdfghjkl;` | `asdfg;lkjh` |
| `zxcvbnm,./` | `zxcvbnm,./` | `zxcvb/.,mn` |

Then, on SYMB: hold the right layer key and type the left QWERTY row for `12345`;
hold the left one and type the right row for `67890` (reversed: `09876`); `-=[]`
under `JKL;` (reversed: `][=-`). On MDIA: `F1`-`F5` and `F6`-`F10` on the QWERTY
row, `F11` and `F12` stacked below `F10`.

**Dual-role keys.** Hold the left thumb Escape and tap `a`: it must produce `A`, not
`a`. Tap it alone: Escape. Hold the right thumb Space and tap `a`: Control+A. Then
type a couple of paragraphs at full speed and check for stray capitals — that is
what catches Flow Tap or Chordal Hold still being on.

To prove setting 23 is actually being honoured rather than coincidentally matching,
turn it off and repeat the Space test. If the behaviour does not change, the
firmware is ignoring it.

**Modifiers.** With an event viewer open, the two thumb Command keys must report
*left* and *right* Command separately, the two outer bottom keys *left* and *right*
Option, and the left home-row pinky *left Control* rather than Caps Lock.

**Careful with two keys.** `[5][6]` on the base layer sleeps the machine. `[3][0]`
on MDIA enters the bootloader; recovering from that means double-tapping the reset
button and reflashing.

## Repository layout

```
keymap.py       the keymap: layer literals and diagrams, no logic
cornix.py       matrix geometry, the right-half reversal, keycode vocabulary, .vil I/O
gen_vil.py      keymap.py + vendor template -> build/oklahomer.vil
render.py       any .vil -> diagrams, or a semantic diff between two of them
build/          generated artifact, committed
docs/           generated diagrams, committed
vendor/         pristine factory export: generator template and rollback point
adr/            why the layout is the way it is
tests/          run with `make test`
```
