# 6. Special keys go on the thumb arc, and keep their old order

Status: accepted

## Context

Modifiers and other special keys are conventionally on the outer edges, under the
little fingers. Holding one with a little finger while typing distorts the whole
hand: the finger that should press a key is busy, so a neighbouring finger covers
for it, and the hand travels further than it should.

Thumbs, meanwhile, do nothing during letter entry.

Each Cornix half has six keys below the alphabet block: three flat ones under the
outer columns, and three angled ones forming the thumb arc. The keyboard being
replaced had two large thumb keys per half, ordered, from the inside out:

    GUI, Escape/Shift, symbol layer, media layer, ... , Alt

## Decision

Put the special keys on the thumbs, and preserve that inside-out order on the arc
and the flat row:

| | inner → outer |
| --- | --- |
| left | `LGui`, `Esc`/`LShft`, symbol layer &#124; media layer, (unused), `LAlt` |
| right | `RGui`, `Spc`/`LCtrl`, symbol layer &#124; media layer, (unused), `RAlt` |

Combine it with dual-role keys (ADR 4) so three arc keys carry five functions.

## Consequences

- The order transfers muscle memory directly: nothing that used to be inboard of
  something else ends up outboard of it.
- The stock keymap treats the innermost arc key as the thumb's home position and
  puts Space there. This layout instead puts the previous keyboard's home thumb key
  in the middle position, keeping the relative order intact. If the innermost key
  turns out to be the comfortable one in practice, swapping positions 4 and 5 of
  `left_bottom` and `right_bottom` is a two-line change.
- The flat position between the media-layer key and `Alt` is left empty on the base
  layer, because it was empty on the previous keyboard too. It is the obvious place
  for anything new.
