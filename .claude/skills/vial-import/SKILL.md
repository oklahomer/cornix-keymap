---
name: vial-import
description: Take a .vil exported from the Vial GUI and fold its changes back into keymap.py. Use when the user says they edited the keyboard directly in Vial, or asks to import, reconcile, or diff an exported .vil against this repository.
---

# Importing a Vial export

The board, not this repository, is the thing that changed. `make import` reports the
drift and prints the layer 0-2 rows as `keymap.py` literals; applying them is a
manual step, because the diagrams and intent comments in `keymap.py` are the point of
the file (adr/0002).

## Steps

1. `python3 gen_vil.py --check`

   Stop if the committed artifact is stale. Comparing an export against an
   out-of-date baseline produces drift that is not real.

2. `make import FILE=<path>`

   **Exit status 1 is the expected outcome when drift exists.** It is not an error;
   it means there is something to look at. Exit 0 means the export already matches.

3. Apply the emitted literals to the matching layer in `keymap.py`.

   Only layers 0-2 are emitted — `render.visual_literals` iterates `OWNED_LAYERS`.
   Rows come out in visual order (inner-to-outer on the right half) and go straight
   into `right_main` / `right_bottom` as printed.

4. Report any other drift; do not silently drop it.

   The diff covers all ten layers plus the top-level fields, the settings block and
   the encoder layout. Drift in layers 3-9, in a top-level field, or in the encoder
   actions means the board or the vendor baseline differs from what this repository
   assumes — that is a finding, not noise, and those layers hold the firmware's own
   controls (adr/0010). Surface it and ask the user how to proceed.

5. `make all`

## After importing

The `.vil` on disk now matches the board, so no hardware check is needed for the
imported change itself. It is needed for anything you edited afterwards.
