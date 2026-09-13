---
name: vial-import
description: Take a .vil exported from the Vial GUI and fold its changes back into keymap.py. Use when the user says they edited the keyboard directly in Vial, or asks to import, reconcile, or diff an exported .vil against this repository.
---

# Importing a Vial export

An edit made in the Vial GUI lands on the board and nowhere else, so it is a
proposal (README.md, "The board is not the source of truth"). `make import` reports
the drift and prints the changed layer 0-2 rows as `keymap.py` literals. Applying
them is manual on purpose: the diagram and the reasoning have to move with the
literal (adr/0002).

## Steps

1. `python3 gen_vil.py --check`

   Stop if the committed artifact is stale. Comparing an export against an
   out-of-date baseline produces drift that is not real.

2. `make import FILE=<path>`

   Read the output, not the exit status. `make import` exits 0 only when there is no
   drift. Drift and failure both exit 2 — make's status for a failed recipe — so a
   non-zero exit on its own does not mean there is something to import:

   | Output | Meaning |
   | --- | --- |
   | `no differences between …` | the export already matches; nothing to import |
   | `N difference(s) between …`, then the report | drift found — **the expected case**; continue |
   | `usage: make import …`, a Python traceback, or anything else | the import did not run; fix the command or the file and retry |

3. Sort the report by who owns what changed. `gen_vil.build` decides it: layers 0-2
   and the settings block are written from `keymap.py`, and everything else is
   carried over from the vendor template.

   | Drift in | Owned by | Go to |
   | --- | --- | --- |
   | layers 0-2, including the encoder push-buttons | `keymap.py` layers | step 4 |
   | `setting …` lines | `keymap.QMK_SETTINGS` | step 5 |
   | layers 3-9, `encoder_layout` (rotation), any other top-level field | vendor template | step 6 |

4. **Layers 0-2.** For each changed layer, update three things in the same edit:

   - the literals: paste the emitted rows into `left_main`, `left_bottom`,
     `left_encoder`, `right_main`, `right_bottom` and `right_encoder`. They come out
     in visual order (inner-to-outer on the right half) and go in as printed;
   - the layer's `doc` diagram, so it shows the new keys;
   - the explanatory text and comments that describe the keys that moved, including
     any ADR link.

   Nothing checks the diagram. `Layer.doc` is never read by the generator, the
   renderer or the tests, so a stale diagram passes `make all`. This step is the
   only thing keeping it true.

   If the change reverses an accepted decision (CLAUDE.md, "Layout decisions live in
   adr/"), ask the user before applying it.

5. **Settings.** `--emit` does not print settings, and `make all` rewrites the whole
   settings block from `keymap.QMK_SETTINGS`. A setting changed in Vial that is not
   copied into `QMK_SETTINGS` is lost from the repository, and loading the
   regenerated file later reverts it on the board.

   Show the user each changed setting and confirm before copying it in. Settings 7,
   22, 23, 26 and 27 are the tap-hold decision recorded in adr/0004, and
   `SettingsTest` pins them: changing one reverses that decision, so it needs a new
   ADR, not just a new value and an edited test.

6. **Vendor-owned drift.** Do not apply it and do not drop it. It means the board or
   the vendor baseline differs from what this repository assumes, and those layers
   hold the firmware's own controls (adr/0010). Report it and ask the user how to
   proceed.

7. `make all`, then `make import FILE=<path>` again.

   It should print `no differences between …` and exit 0: the repository now
   reproduces the export, which README.md calls the acceptance test. Any drift still reported is drift that was deliberately not
   adopted. Tell the user, because loading the regenerated `build/oklahomer.vil`
   would change the board.

## After importing

When step 7 reports no differences the board already runs this layout, so there is
nothing to reload. That is not the same as the keyboard behaving as intended: the
GUI edit itself was never verified. As CLAUDE.md requires for every layout change,
report hardware verification — README.md, "Checking it on the hardware" — as pending
until the user comes back with a result.
