# 3. Firmware settings and mapping-software settings have separate jobs

Status: accepted

## Context

Two layers of software can remap keys on this machine: the keyboard firmware, and
Karabiner-Elements running on macOS. Their capabilities overlap, so without a rule
it stops being obvious where any given behaviour comes from, or which one wins.

They differ in reach:

| | built-in laptop keyboard | this keyboard | another computer |
| --- | --- | --- | --- |
| mapping software | applies | applies | does not apply |
| firmware | does not apply | applies | applies |

## Decision

- Behaviour that should be identical on the laptop keyboard and this one is
  configured in the mapping software.
- Behaviour that belongs to this keyboard alone, or that must keep working on a
  machine where the mapping software is not installed, is configured in the firmware.

## Consequences

- The dual-role Escape and Space keys are a property of this keyboard, and must
  survive being plugged into someone else's machine, so they live in the firmware.
  See ADR 4.
- Application launching is the other way round. The layer that used to launch
  applications only ever emitted `Right Option + letter` chords, and the mapping
  software turned those into launches, so the same chords work from the laptop
  keyboard. The firmware side of that arrangement was removable; see ADR 9.
- The left pinky home-row key is `KC_LCTRL`, not `KC_CAPSLOCK`. The mapping software
  rewrites Caps Lock to Control on this machine, so both spellings feel identical
  here, but only the firmware spelling survives on a machine without it.
- `LCTL(KC_LBRACKET)` on the symbol layer and the Control half of the Space mod-tap
  must both emit *left* Control, because a mapping-software rule keys off it.
