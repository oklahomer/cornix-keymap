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
| base | `LALT(KC_SPACE)` | lock screen, `LCG(KC_Q)` |
| symbol | `RALT(KC_M)`, mission control | unused |
| media | unused | unused |

Two of the four old inner-column keys switched virtual desktops. They were no longer
in use and were dropped rather than relocated, which is what freed the slots.

### The right encoder locks the screen; it does not sleep

The old keyboard slept the machine from this key: Option+Command+Power, sent as two
modifiers plus HID usage `0x66`, "Keyboard Power". Locking the screen is what is
actually wanted from a key next to the hands, so this is a deliberate change of
function rather than a transliteration. On macOS that is Ctrl+Cmd+Q.

Getting there was not obvious, and the detour is worth recording:

- `KC_SLEP` (System Sleep, `0xA6`) does nothing on this keyboard. It is a *System
  Control* usage, sent on its own HID report, and that report is evidently not
  reaching the host on this firmware and transport. Do not reach for it again.
- The old chord cannot be written by name either. Vial's keycode table has no entry
  for `0x66` — it skips from `0x65` to `0x67`. It *can* still be expressed: Vial
  writes a value it cannot name as a bare hex string and reads it back through an
  expression evaluator, so `"0xc66"` (`(LALT | LGUI) << 8 | 0x66`) round-trips
  through the GUI intact. That escape hatch exists for any future keycode with no
  name; nothing in this keymap needs it now.

The key is written `LCG(KC_Q)`, not `LCTL(LGUI(KC_Q))`. Both resolve to `0x914`, but
Vial gives every modifier *combination* a single name and writes that one on export,
so the nested spelling would come back changed and register as drift. The generator
rejects nested modifier wrappers for that reason.

## Consequences

- Pressing a knob is not pressing a key. The right push is a deliberate, occasional
  action, so the different feel is acceptable there — and putting the lock screen
  behind a knob press makes it harder to trigger by accident than the sleep chord it
  replaces was in a corner of the old top row. The left push turned out not to be
  occasional: Option+Space is in daily use, and the knob's press force is too high
  for a key reached that often. The same chord is therefore also on SYMB `[1][0]`.
  The encoder keeps it, so this is a duplicate rather than a move, and the table
  above still holds.
- If a board without the encoder modules is ever used, these two slots vanish. The
  fallback is the empty flat bottom key on each half.
- Every other column-6 slot must stay unused (`-1`) on every layer. The generator
  enforces this and the tests check it.
