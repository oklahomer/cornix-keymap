# cornix-keymap

`keymap.py` is the source of truth. `build/oklahomer.vil` and `docs/layers.md` are
generated from it — never edit them by hand; run `make all`. `make check` only
reports staleness; it will not regenerate for you.

Most of this repository's invariants are already enforced by code, not by this file:
`cornix.layer_to_matrix` performs the right-half reversal, `check_shape` fixes the
encoder and dead slots, every row and both encoders are validated on the way in and
the whole document again before it is written, and `gen_vil.build` requires exactly
one definition per owned layer. Trust those and read the failure.
What follows is only what no check can decide for you.

## Verification boundary

`make check` verifies that this repository is internally consistent. It verifies
nothing about the keyboard: not RMK, not Vial, not Bluetooth, not HID behaviour, and
not whether the QMK settings block reached the board.

After any change to a layout, an encoder, a modifier, or `QMK_SETTINGS`:

1. Ask the user to load `build/oklahomer.vil` onto the board.
2. Ask them to export it again from Vial and run `make import FILE=<export>`.
3. Point them at the hardware checks in README.md.

Report hardware verification as pending until the user comes back with a result.
Passing tests are not evidence that the keyboard works.

## Writing a layer

Write both halves **visually, left to right, as the keys sit on the desk**. On the
right half that is inner-to-outer. The matrix stores that row reversed, and
`cornix.to_storage_right` is the only code that knows it — so putting a keycode in
the wrong visual position produces a perfectly valid `.vil` that is the wrong
keymap. No test can catch that; check the rendered diagram in `docs/layers.md`
against the physical board.

## Layout decisions live in adr/

The shape and vocabulary checks accept many changes that contradict an accepted
decision: moving the function-key stack (adr/0005), moving a thumb key (adr/0006),
or collapsing left and right modifiers into one (adr/0008) all pass.

Before changing where something lives, read the ADR that put it there. If the
request reverses an accepted decision, do not just edit the literal — add a new ADR
saying what it supersedes and update `adr/README.md`.

## Commands

`make all` (build + render + test) · `make check` (consistency) · `make import FILE=…`
