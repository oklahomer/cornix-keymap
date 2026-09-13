# 12. Pin the vendor template by digest

Status: accepted

## Context

`vendor/cornix-default-keymap.vil` is the generator's input (adr/0010) and, at the
same time, this suite's oracle: `VendorPreservationTest` asserts that the generated
document matches that file everywhere outside layers 0-2 and the settings block.

An input that is also the expected value cannot detect its own corruption. Edit the
template and the tests do not fail — they agree with the edit. What would be lost is
exactly what adr/0010 says must not be: the uid the firmware matches on, the array
shapes, layers 3-9, and `USER00`-`USER02`, which on this board are the Bluetooth and
output controls. Losing those can mean losing the ability to reconnect the keyboard.

Nothing else guards the file. It is a pristine factory export; there is no upstream
to diff it against.

## Decision

Record the SHA-256 of the template in the test suite and assert it.

The digest is `f85dd13d58398ea53e29f3fbab88d07b1f86ba09982e7eaac5d36eb314a327ab`.

A deliberate refresh — a firmware update that changes the factory export — updates
the digest in the same commit that replaces the file, and says why in a new ADR.

## Consequences

- Any change to the template fails the suite immediately, whatever made it, and the
  failure names the file rather than appearing as a puzzling preservation failure.
- The oracle is now independent of the input in the one way that matters.
- Refreshing the vendor export costs one extra deliberate step. That is the point.
