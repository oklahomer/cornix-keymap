# cornix-keymap

`keymap.py` is the source of truth. `build/oklahomer.vil` and `docs/layers.md` are
generated from it — never edit them by hand; run `make all`. `make check` compares
both artifacts against the source without rewriting them, then runs the full test
suite; it never regenerates anything for you.

Most of this repository's invariants are already enforced by code, not by this file:
`cornix.layer_to_matrix` performs the right-half reversal and places both encoder
push-buttons, validating every row and both encoders as it goes; `check_shape` rejects
a document of the wrong dimensions or with anything in an unwired slot; the whole
document is validated again before it is written; and `gen_vil.build` requires
exactly one definition per owned layer. Trust those and read the failure.
What follows is only what no check can decide for you.

## Verification boundary

`make check` verifies that this repository is internally consistent. It verifies
nothing about the keyboard: not RMK, not Vial, not Bluetooth, not HID behaviour, and
not whether the QMK settings block reached the board.

After any change to a layout, an encoder, a modifier, or `QMK_SETTINGS`:

1. Ask the user to load `build/oklahomer.vil` onto the board.
2. Ask them to export it again from Vial and run `make import FILE=<export>`.
3. Point them at the hardware checks in README.md.

Report hardware verification as pending until the user comes back with a result.
Passing tests are not evidence that the keyboard works.

## Writing a layer

Write both halves **visually, left to right, as the keys sit on the desk**. On the
right half that is inner-to-outer. The matrix stores that row reversed, and
`cornix.to_storage_right` is the only code that knows it — so putting a keycode in
the wrong visual position produces a perfectly valid `.vil` that is the wrong
keymap. Tests pin only a few base-layer positions, so most misplacements build and
pass; check the rendered diagram in `docs/layers.md` against the physical board.

## Layout decisions live in adr/

The tests catch some changes that contradict an accepted decision, but only by
accident and never by naming the ADR: collapsing right GUI onto the left side
(adr/0008) fails as a port-ledger and a reversal failure, neither of which mentions
adr/0008. Moving a key passes every check unless it moves to or from one of the few
positions a test happens to pin.

Before changing where something lives, read the ADR that put it there. If the
request contradicts an accepted decision, do not just edit the literal: tell the user
and let them decide. If they change the decision, update the existing ADR in place so
it describes the decision as it now stands — do not mark it superseded or add a
replacement. Add a new ADR only for a decision no existing one covers, and fix
anything left contradicting the updated ADR in a separate commit.

A failing test that pins a recorded decision is the same moment: never make it pass
on your own by editing the test or the port ledger. The change-keymap skill has the
procedure and the choices to offer.

## Pushing, pull requests and merges

Never push, open a pull request or merge unless the user explicitly agrees to that
exact action, every time. Agreement to edit or commit is not agreement to publish, and
the rule covers every route to the same effect — `gh api`, a GitHub MCP tool, a
browser. `.claude/settings.json` makes `git push`, `git merge`, `gh pr create` and
`gh pr merge` ask, but it cannot catch the other routes.

## Commands

`make all` (build + render + test) · `make check` (artifacts + tests, writes nothing) ·
`make import FILE=…`
