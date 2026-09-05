# 5. Numbers and function keys live on the QWERTY row, reached by a layer

Status: accepted

## Context

Reaching the number row means stretching a finger off the home position, and a
numpad means moving the whole hand. Neither is possible with the wrists resting.

The keyboard being replaced had a number row, but it also carried the digits on the
symbol layer, on the QWERTY row: `1`-`5` under `QWERT` and `6`-`0` under `YUIOP`.
The media layer did the same with `F1`-`F10`, and put `F11` and `F12` in the column
below `F10` so that a ten-column row could still cover twelve function keys.

The Cornix has three rows per half and no number row at all.

## Decision

Digits and function keys are reached by holding a layer key, on the QWERTY row.
Losing the physical number row costs nothing, because the layer positions were
already the ones in daily use.

Hold the layer key on the half opposite the digits being typed, so the holding hand
is never the typing hand.

## Consequences

- `F10`, `F11` and `F12` stack vertically in the same column, one under the other.
  The stack is a property of the layout, not an accident of the old board, so the
  renderer's diagrams should be checked for it after any change.
- The top row of the old keymap disappears entirely, along with the duplicate
  Escape that sat in its corner. The remaining Escape is the thumb key.
