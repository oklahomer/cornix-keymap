# 1. Ship a `.vil` on the stock firmware

Status: accepted

## Context

The Cornix LP ships with RMK firmware that speaks the Vial protocol. Vial rewrites
the keymap on the board in real time, over USB or Bluetooth, with no compile and no
reflash. A layout can be exported to a `.vil` file and loaded back later.

The keymap being ported here came from an ErgoDox EZ running QMK, where the keymap
was C source compiled into the firmware image. That workflow does not exist on this
board: the Cornix is not supported by QMK, and its firmware is written in Rust.

Three options were on the table:

1. Stay on the stock firmware and treat the `.vil` as the deliverable.
2. Flash a community ZMK build. ZMK expresses hold-tap behaviour more precisely
   than anything the Vial protocol can carry.
3. Build RMK from source, defining the keymap in `keyboard.toml`.

## Decision

Stay on the stock firmware and ship a `.vil`.

## Consequences

- No toolchain. Applying a change is loading a file, and reverting is loading the
  previous file. Both work wirelessly.
- No custom firmware code. Behaviour that the ErgoDox implemented in C has to be
  expressed with keycodes and firmware settings instead. See ADR 4.
- The keymap depends on what this firmware version's Vial implementation accepts.
  Anything it cannot parse becomes a dead key rather than an error, so the generator
  validates every keycode string before writing the file, and the README lists the
  checks to run on the hardware after loading a new layout.
- Options 2 and 3 stay open. Both would start from the layer definitions in
  `keymap.py`, which are firmware-independent.
