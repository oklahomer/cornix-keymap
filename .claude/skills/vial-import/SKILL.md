---
name: vial-import
description: Take a .vil exported from the Vial GUI and fold its changes back into keymap.py. Use when the user says they edited the keyboard directly in Vial, or asks to import, reconcile, or diff an exported .vil against this repository.
---

# Importing a Vial export

An edit made in the Vial GUI lands on the board and nowhere else, so it is a
proposal (README.md, "The board is not the source of truth"). `make import` reports
the drift and prints the rows of every changed layer 0-2 as `keymap.py` literals.
Applying them is manual on purpose: the diagram and the reasoning have to move with
the literal (adr/0002).

This skill covers what is particular to an import: reading the report, sorting the
drift by owner, and choosing which differences to adopt. Carrying an adopted
difference into `keymap.py`, the ADRs, README.md and the tests works exactly as for a
change the user asks for, and the change-keymap skill governs it.

## Steps

1. **Start from a clean, consistent tree.** This replaces change-keymap's step 1.

   - Run `git status --short` and read `git diff`. If uncommitted changes touch
     `keymap.py`, `build/`, `docs/`, README.md, `adr/` or `tests/`, stop and ask the
     user how to keep them apart. Never overwrite, stage or commit changes you did not
     make without their agreement.
   - Run `make check`, and stop if it fails. A stale artifact makes the comparison
     report drift that is not real, a stale `docs/layers.md` misleads every later
     reading of the layout, and a test that already fails would later look like the
     import's doing.

2. `make import FILE=<path>`

   Read the report, not the exit status. make echoes the command first and then prints
   the result. Unless the result is "no differences", it ends with a
   `make: *** [import] Error …` line and exits 2 — for drift and failure alike:

   | Output after the echoed command | Meaning |
   | --- | --- |
   | `no differences between …`, exit 0 | the export already matches; nothing to import |
   | `N difference(s) between …`, then the report and the emitted literals | drift found — **the expected case**; continue |
   | `usage: make import …`, a Python traceback, or anything else | the import did not run; fix the command or the file and retry |

3. **Sort the report by who owns what changed.** `gen_vil.build` decides it: layers
   0-2 and the settings block are written from `keymap.py`, and everything else is
   carried over from the vendor template.

   | Drift in | Owned by |
   | --- | --- |
   | `layer 0`-`layer 2` lines, encoder push-buttons included | `keymap.py` layers |
   | `setting …` lines | `keymap.QMK_SETTINGS` |
   | `layer 3`-`layer 9` lines, `encoder_layout differs`, `field …` lines | vendor template |

   Vendor-owned drift is never adopted here. It means the board or the vendor baseline
   differs from what this repository assumes, and those layers hold the firmware's own
   controls (adr/0010). The import of owned differences carries on regardless, and
   step 5 reports the vendor drift with these choices:

   - leave it: the board and the repository differ in that slot, and loading the
     regenerated `build/oklahomer.vil` would put the vendor value back on the board;
   - make the repository follow the board: that means refreshing the vendor template or
     changing what the generator owns, which is out of scope here.

4. **Assess every owned difference before asking anything.** Read
   `.claude/skills/change-keymap/SKILL.md` now; from here on it governs, with the
   import-specific points below. Treat every `layer 0`-`layer 2` line and every
   `setting …` line as a separate candidate, and run change-keymap's steps 2 to 4 over
   all of them. From step 2, skip only the question about which slot is meant — the
   report names each one exactly — and keep the rest: whether the slot is empty,
   whether the keycode already sits elsewhere on the layer, and what is out of scope.
   Then step 3's ADR classification, and step 4's port-ledger, pinned-value,
   settings-id and README checks.

   - Do not assume every difference is a GUI edit the user means to keep. An export
     from a board that was not loaded from the current artifact carries old values
     alongside the new edit, and adopting those would undo later changes.
   - A keycode that already sits elsewhere on the layer is a move when the report also
     shows its old slot changing, and an addition when it does not. Say which in step 5.
   - `--emit` does not print settings, and `make all` rewrites the whole settings block
     from `keymap.QMK_SETTINGS`. A setting changed in Vial that is not copied into
     `QMK_SETTINGS` is lost from the repository, and the next load of the regenerated
     file reverts it on the board. Settings 7, 22, 23, 26 and 27 are the tap-hold
     decision recorded in adr/0004; adopting a different value changes that decision.
   - A setting that differs only by being back at its stock value — the value in
     `vendor/cornix-default-keymap.vil` — may come from a layout load rather than a GUI
     edit: README.md, "Applying it to the keyboard", warns that a load does not
     necessarily carry settings. Say so in step 5, and tell the user the board is
     running that value now, whichever way they decide.

5. **Ask once which differences to adopt, and how.** Skip this only when every owned
   difference in the report is one the user explicitly named, there is no vendor-owned
   drift, and nothing from step 4 needs their decision. Otherwise send one message that
   lists each candidate with what adopting it involves — its ADR findings, any predicted
   test failure with its choices, any README change — and the vendor-owned drift with
   the choices from step 3.

   - For a difference the user did not mention, recommend not adopting it unless there
     is a reason to think it was intended.
   - Not adopting a difference is change-keymap's "drop the request" for that candidate.
   - The user's answer is change-keymap's agreed plan. Stopping here to ask is part of
     the procedure, not a failure.

6. **Apply what was adopted** with change-keymap's steps 5 to 8. Edit only the adopted
   slots in the current literals, in `keymap.py`'s own style: `XX` and `__` for `KC_NO`
   and `KC_TRNS`, double quotes, the existing column alignment. The emitted literals
   are reference only. They print every row of each changed layer in Python's repr
   style, so pasting them would both erase that style and carry in differences that
   were not adopted.

7. **`make import FILE=<path>` again**, once `make check` passes.

   - `no differences between …` and exit 0: the repository now reproduces the export,
     which README.md calls the acceptance test.
   - Any drift still reported must be exactly what was not adopted, vendor-owned drift
     included. Tell the user, because loading the regenerated `build/oklahomer.vil`
     would change the board.

8. **Commit** as change-keymap's step 9 describes.

## After importing

This replaces change-keymap's "Reporting back".

- If the procedure stopped on a problem before the adopted differences were applied
  and `make check` passed — a failing baseline, an import that did not run, a failure
  the plan did not cover — report what blocked it and ask for nothing else. Waiting for
  the user's answer in step 5 is not such a stop.
- Otherwise, when step 7 reports no differences the board already runs this layout, so
  there is nothing to reload. That is not the same as the keyboard behaving as
  intended: the GUI edit itself was never verified. As CLAUDE.md requires for every
  layout change, report hardware verification — README.md, "Checking it on the
  hardware" — as pending until the user comes back with a result.
- If drift remains, the board and the repository now differ: say so, and let the user
  decide whether to load the regenerated file.
