# 4. Dual-role keys are firmware mod-taps, tuned to decide on events not time

Status: accepted

## Context

Two thumb keys carry two roles each:

- Escape when tapped, Left Shift when held with another key.
- Space when tapped, Left Control when held with another key.

Putting a modifier under a thumb is what lets the pinkies stay on letters, and
doubling it with a tap keeps the small thumb cluster useful. See ADR 6.

On the previous keyboard this was hand-written C rather than QMK's built-in
`SFT_T()`. The objection to the built-in was not the idea of a dual-role key but how
the decision was made: a hold threshold in milliseconds, with separate options
changing what happens when another key arrives near that threshold. A judgement that
rests on timing misfires when typing speed changes. The hand-written version decided
on an event instead — another key going down means "modifier", full stop — and used
the timer only for the tap case.

Its exact specification was:

1. another key goes down while the key is held: send the modifier;
2. released alone within the tapping term: send the tap keycode;
3. released alone after the tapping term: send nothing.

There is no way to write custom code on this firmware, so the behaviour has to come
out of a stock mod-tap keycode plus settings.

## Decision

Use `LSFT_T(KC_ESCAPE)` and `LCTL_T(KC_SPACE)`, with these settings:

| Vial id | setting | value | why |
| --- | --- | --- | --- |
| 23 | Hold On Other Key Press | on | makes rule 1 an event, not a timer |
| 22 | Permissive Hold | off | one decision rule, not two overlapping ones |
| 26 | Chordal Hold | off | it resolves *same-hand* chords as taps, which would turn thumb-Shift plus a left-hand letter into a lowercase letter |
| 27 | Flow Tap | off | it forces a tap when the previous keystroke was recent, which is exactly the speed-dependent misfire being avoided |
| 7 | Tapping Term | 200 ms | matches the previous keyboard, which ran the QMK default |

## Consequences

- Rules 1 and 2 are reproduced exactly. Rule 3 is close but not identical: a mod-tap
  held alone and released emits a bare modifier press and release, where the C
  version emitted nothing. Nothing in this setup reacts to a bare Shift or Control,
  so the difference is not observable, but it is a real difference.
- Two of the settings ship in the opposite state, and `Chordal Hold` in particular
  breaks the feature outright, so a layout load is not complete until the settings
  have been checked. The README lists them.
- The whole decision hinges on the firmware honouring setting 23. The falsification
  is cheap: turn it off, and holding Space plus another key should start producing a
  space instead of a Control chord. If nothing changes, the firmware is ignoring the
  setting and the behaviour has to move to the mapping software, at the cost of not
  working on other machines.
