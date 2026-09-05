# 8. Left and right modifiers stay separate physical keys

Status: accepted

## Context

When a keyboard has two of the same modifier, one of them can keep its original
behaviour while the other is given a related but different job. That is how a single
board grows extra shortcuts without redefining any existing one.

That pattern is in heavy use on this machine, through the mapping software:

- Left Command alone switches the input source to English; Right Command alone
  switches it to Japanese.
- Right Command plus a letter or digit is a private prefix for a dozen shortcuts
  (function keys, tab switching, window switching, paste-without-formatting, several
  IDE actions), none of which collide with a system default.
- Right Option plus a letter launches applications.

All of it depends on the two sides being distinguishable. Software that only sees
"Command" cannot tell them apart.

## Decision

Keep `LGui` and `RGui` as separate keys, one on each thumb arc, and keep `LAlt` and
`RAlt` on the outermost flat bottom key of their own half. Never collapse a pair
onto one side, and never map one side's keycode onto the other side's key.

## Consequences

- Two of the six thumb-arc keys are spent on Command. That is expensive on a small
  board, and it is the reason the neighbouring key carries two roles (ADR 4).
- `Enter` also keeps its position and its finger — right little finger, home row,
  outermost column — because pressing it by mistake has consequences.
- Verifying this needs an event viewer, not a text editor: the two keys look
  identical until you can see which HID code each one sends.
