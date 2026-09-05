# 7. The inner column moves to the encoder push-buttons

Status: accepted

## Context

The old keyboard had a seventh column on the inside of each half, reached by
stretching an index finger inwards. It carried four keys: two chords on the upper
row and two on the lower.

The Cornix has six columns per half. What it does have is two rotary encoders, each
with a push-button, mounted inboard of the inner column at roughly the height of the
bottom letter row — which is where the old inner column's lower keys were.

In the matrix those push-buttons are `[2][6]` on the left and `[5][6]` on the right.
Note the asymmetry: the right one is on row 5, not row 6.

## Decision

Treat the encoder push-buttons as the replacement for the inner column, one slot per
half, per layer:

| layer | left `[2][6]` | right `[5][6]` |
| --- | --- | --- |
| base | `LALT(KC_SPACE)` | sleep, `LALT(LGUI(KC_POWER))` |
| symbol | `RALT(KC_M)`, mission control | unused |
| media | unused | unused |

Two of the four old inner-column keys switched virtual desktops. They were no longer
in use and were dropped rather than relocated, which is what freed the slots.

## Consequences

- Pressing a knob is not pressing a key. Both survivors are deliberate, occasional
  actions, so the different feel is acceptable — and putting sleep behind a knob
  press makes it harder to trigger by accident than it was in a corner of the old
  top row.
- If a board without the encoder modules is ever used, these two slots vanish. The
  fallback is the empty flat bottom key on each half.
- Every other column-6 slot must stay unused (`-1`) on every layer. The generator
  enforces this and the tests check it.
