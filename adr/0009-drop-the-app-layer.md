# 9. The application-launcher layer is removed

Status: accepted

## Context

The old keymap had a fourth layer, entered with a one-shot key, whose only content
was six application launchers on their mnemonic letters: `T` for the terminal, `S`
for Slack, and so on.

The layer never launched anything itself. Each key emitted `Right Option + letter`,
and the mapping software turned that chord into a launch, so that the same shortcut
worked from the laptop keyboard. The layer existed purely as a more comfortable way
to type a chord.

`RAlt` is present on the base layer of this keymap, on the outermost bottom key of
the right half.

## Decision

Drop the layer and its entry key. Launch applications by pressing `Right Option`
and the letter directly, the same way it is done from the laptop keyboard.

## Consequences

- Three layers instead of four, and one fewer thing to remember.
- Nothing is lost: every launcher shortcut still works, because the shortcut was
  never in the firmware to begin with.
- The base-layer key that held the one-shot is now empty, mirroring the empty key on
  the left half.
- Layers 3 to 9 in the generated file are whatever the vendor shipped; this
  repository does not touch them (ADR 10). Bringing a layer back would mean adding
  it to `keymap.py` and assigning an entry key.
