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

1. **Start from a clean, consistent tree.**

   - Run `git status --short` and read `git diff`. If uncommitted changes touch
     `keymap.py`, `build/`, `docs/`, README.md, `adr/` or `tests/`, stop and ask the
     user how to keep them apart. Never overwrite, stage or commit changes you did not
     make without their agreement.
   - Run `python3 gen_vil.py --check`, and stop if the committed artifact is stale:
     comparing an export against an out-of-date baseline produces drift that is not
     real.

2. `make import FILE=<path>`

   Read the output, not the exit status. `make import` exits 0 only when there is no
   drift. Drift and failure both exit 2 — make's status for a failed recipe — so a
   non-zero exit on its own does not mean there is something to import:

   | Output | Meaning |
   | --- | --- |
   | `no differences between …` | the export already matches; nothing to import |
   | `N difference(s) between …`, then the report | drift found — **the expected case**; continue |
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
   controls (adr/0010): report it, and ask the user how to proceed.

4. **Assess every owned difference before asking anything.** Read
   `.claude/skills/change-keymap/SKILL.md` now; from here on it governs, with the
   import-specific points below. Treat every `layer 0`-`layer 2` line and every
   `setting …` line as a separate candidate, and run change-keymap's steps 3 and 4 over
   all of them: the ADR classification, and the port-ledger, pinned-value, settings-id
   and README checks. Its step 2 does not apply — the report names each slot exactly —
   and its step 1 is step 1 here.

   - Do not assume every difference is a GUI edit the user means to keep. An export
     from a board that was not loaded from the current artifact carries old values
     alongside the new edit, and adopting those would undo later changes.
   - `--emit` does not print settings, and `make all` rewrites the whole settings block
     from `keymap.QMK_SETTINGS`. A setting changed in Vial that is not copied into
     `QMK_SETTINGS` is lost from the repository, and the next load of the regenerated
     file reverts it on the board. Settings 7, 22, 23, 26 and 27 are the tap-hold
     decision recorded in adr/0004; adopting a different value changes that decision.

5. **Ask once which differences to adopt, and how.** Skip this only when the user has
   already said exactly which differences to take and nothing from step 4 needs their
   decision. Otherwise send one message listing each candidate with what adopting it
   involves — its ADR findings, any predicted test failure with its choices, any README
   change — together with the vendor-owned drift from step 3. The user's answer is
   change-keymap's agreed plan.

6. **Apply what was adopted** with change-keymap's steps 5 to 8. Edit only the adopted
   slots in the current literals. The emitted rows are reference: they show each slot
   in visual order, inner to outer on the right half. Paste a whole emitted row only
   when every differing slot in it has been adopted.

7. **`make import FILE=<path>` again**, once `make check` passes.

   - `no differences between …` and exit 0: the repository now reproduces the export,
     which README.md calls the acceptance test.
   - Any drift still reported must be exactly what was not adopted. Tell the user,
     because loading the regenerated `build/oklahomer.vil` would change the board.

8. **Commit** as change-keymap's step 9 describes.

## After importing

This replaces change-keymap's "Reporting back". If the procedure stopped before the
adopted differences were applied and `make check` passed, report what blocked it and
ask for nothing else.

Otherwise, when step 7 reports no differences the board already runs this layout, so
there is nothing to reload. That is not the same as the keyboard behaving as intended:
the GUI edit itself was never verified. As CLAUDE.md requires for every layout change,
report hardware verification — README.md, "Checking it on the hardware" — as pending
until the user comes back with a result. If drift remains, the board and the
repository now differ: say so, and let the user decide whether to load the regenerated
file.
