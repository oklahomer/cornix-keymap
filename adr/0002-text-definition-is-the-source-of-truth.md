# 2. A text definition is the source of truth, not the board

Status: accepted

## Context

A `.vil` file is a JSON blob of keycode strings indexed by matrix position. It is
what the keyboard consumes, but it is close to unreadable: nothing in it says which
key is under your left index finger, the right half is stored in reverse column
order, and a diff of two versions is a wall of quoted strings.

The keymap it replaced was C source with an ASCII diagram of every layer in the
comments. The diagram was the part that made the file reviewable a year later.

There is also a second author: the Vial GUI. Any edit made there lands on the board
immediately, and nothing about it flows back into version control.

## Decision

`keymap.py` holds the layers as literals with an ASCII diagram above each one, and
is the only file a human edits. `gen_vil.py` generates `build/oklahomer.vil` from it
and `render.py` regenerates `docs/layers.md` from the artifact. Both generated files
are committed, the way a compiled firmware image used to be committed next to its
source.

The board is never the source of truth. An edit made in the GUI is a proposal:
`make import FILE=<export>` diffs it against the artifact, prints every keycode row
and both encoder fields of each changed owned layer — 0 to 2 — as source literals,
and exits non-zero. The change is then applied to
`keymap.py` by hand so that the diagram and the reasoning stay attached to it.

## Consequences

- `make check` compares the committed files against what the source produces, without
  rewriting either, and fails if they are stale — which catches the case where someone
  edits the source and forgets to rebuild.
- Round-tripping a GUI edit is deliberately manual. Rewriting `keymap.py`
  automatically would destroy the diagrams, which are the reason the file exists.
- The layer definitions are written in visual order for both halves. The right-half
  column reversal lives in exactly one function, `cornix.to_storage_right`.
