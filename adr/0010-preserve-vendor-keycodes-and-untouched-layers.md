# 10. Generate from the vendor export, and keep what it contains

Status: accepted

## Context

A `.vil` file carries more than a keymap: a uid the firmware matches on, protocol
version numbers, fixed-size arrays for macros, combos and tap dances, the encoder
rotation actions, and ten layers whether or not they are used.

The stock keymap also uses three firmware-specific custom keycodes, shown as
`USER00`, `USER01` and `USER02`. Their names live in the firmware and are visible in
the Vial GUI, not in the file. On a wireless split keyboard these are the controls
for things like Bluetooth channels and output switching — losing them can mean
losing the ability to reconnect the board.

Writing a `.vil` from scratch risks getting any of this subtly wrong, in a format
that fails silently.

## Decision

`gen_vil.py` loads `vendor/cornix-default-keymap.vil` — a pristine export, never
edited — and replaces only layers 0 to 2 and the settings block. Everything else is
carried through unchanged, including layers 3 to 9.

The three custom keycodes are re-homed onto the media layer, in the left outermost
column, where the ported keymap had nothing.

## Consequences

- The generated file cannot drift out of shape, and a firmware feature that this
  repository does not know about survives a rebuild. A test asserts that every
  top-level field other than `layout` and `settings`, and every layer outside 0-2,
  is byte-identical to the template.
- The same file is the rollback point. Loading it in Vial restores the keyboard to
  how it arrived.
- The custom keycodes are opaque here by design. Confirm what they do in the GUI,
  with the keyboard on USB, before relying on them.
- Encoder rotation is left as the vendor set it: volume on one side, scroll wheel on
  the other. Neither existed on the old keyboard, so neither can feel wrong.
