---
name: change-keymap
description: Change the keymap because the user asked for it — add, move, remove or swap keys, change an encoder push-button, or change a QMK setting — by editing keymap.py, carrying the change through build/ and docs/, keeping adr/ consistent, and proving it with make. Use for requests like "put Up on the left thumb", "swap these two keys" or "drop the mouse keys". Not for edits the user already made in the Vial GUI; use vial-import for those.
argument-hint: <what to change>
---

# Changing the keymap

Request, if one was passed: $ARGUMENTS

`keymap.py` is the only file edited by hand (adr/0002). `build/oklahomer.vil` and
`docs/layers.md` follow from it through `make`, and `adr/` records why things are
where they are. A change is finished when all three agree — and only part of that
can be proved mechanically:

| What must hold | What proves it |
| --- | --- |
| `build/oklahomer.vil` is what `keymap.py` produces | `make check` |
| `docs/layers.md` is what the artifact renders | `make check` |
| every keycode is one Vial can parse | `make all` — the build stops with `KeycodeError` |
| the key is where the user meant | nothing — step 8 reads the rendered diagram |
| the `doc` diagram inside `keymap.py` is current | nothing — `Layer.doc` is never read; step 5 |
| README.md is still right | nothing — step 8 |
| the change agrees with the ADRs | nothing reliable — step 3 |

The last row matters most. Tests catch some ADR violations by accident and never
name the ADR: moving right GUI onto the left side breaks adr/0008 and surfaces as a
port-ledger failure and a reversal failure, neither of which mentions adr/0008.

## Steps

1. **Start from a consistent tree.** Run `make check`. If it fails, stop and report;
   do not build a change on a stale or broken baseline. Note any uncommitted changes
   in `git status` that are not yours.

2. **Pin the request down physically.**

   - Read the affected layer in `docs/layers.md`. It is generated from the data, so it
     shows what is really on each key. Name every slot you will touch by its matrix
     position, for example `[3][1]`.
   - Ask when the request fits more than one slot ("the left thumb" is three keys) or
     when the target slot is not empty: overwriting a key removes a function, and the
     user may not know what is there.
   - The right half is written in visual order, inner to outer; the matrix stores it
     reversed (CLAUDE.md, "Writing a layer").
   - Out of scope — stop and say so: layers 3-9 and `vendor/` (adr/0010), adding or
     removing a layer (it changes `cornix.OWNED_LAYERS`, a code change), and encoder
     rotation (`encoder_layout`, carried over from the vendor template).

3. **Read every ADR before editing.** There are few and they are short. Read all of
   `adr/*.md` rather than guessing which apply: position, side, keycode spelling and
   settings are each pinned by a different one. Classify each against the change:

   | Finding | Meaning | Next |
   | --- | --- | --- |
   | contradicts | the change breaks the rule the ADR sets or the reasoning it records | step 4: the user decides |
   | makes a detail stale | the rule still holds, but a table or sentence describing current contents becomes wrong — for example adr/0007's per-layer encoder table | step 6: plan the edit |
   | unrelated | — | — |

4. **Check the keycode and settle the plan.**

   - The keycode must be one `cornix.is_valid_keycode` accepts:
     `python3 -c 'import cornix; print(cornix.is_valid_keycode("KC_UP"))'`. A chord of
     two or more modifiers uses Vial's combined name (`LCG(KC_Q)`, never nested), and
     a mod-tap wraps a basic key only. If the keycode is not accepted, do not guess a
     spelling: Vial turns a name it cannot parse into a dead key, silently (adr/0001).
     Ask the user to set the key in the Vial GUI and export, read the exact spelling
     from the file, and tell them that extending the vocabulary in `cornix.py` is a
     code change.
   - Present the plan and wait for agreement before editing when any of these apply:
     an ADR is contradicted or will be edited; the slot was ambiguous or not empty; a
     QMK setting changes; a keycode is new to the port ledger or disappears from the
     keymap (step 7 will fail — say so in the plan).
   - The plan lists each slot as `[row][col]` before → after, the ADRs affected and
     how, the files expected to change (step 8), and any test expected to fail and
     why.
   - When an ADR is contradicted, give the user the choices and let them pick: drop
     the request, change the request so it fits, or change the decision and update
     the ADR (step 6).
   - Otherwise — one unambiguous empty slot, no ADR involved, nothing new to the
     ledger — go ahead.

5. **Edit `keymap.py`.** For every layer touched, in the same edit:

   - the literals, in visual order;
   - the layer's `doc` diagram. Nothing reads it — not the generator, the renderer or
     the tests — so a stale diagram passes everything. This step is all that keeps
     it true;
   - the explanatory text under the diagram and the comments next to the literals,
     including ADR links;
   - `QMK_SETTINGS` and its comment, if a setting changes.

   Do not edit `build/`, `docs/` or `vendor/`. Do not touch `ERGODOX_DISPOSITION` or
   any test yet; step 7 settles those with the user.

6. **Update or add ADRs** — only as agreed in step 4.

   - **An existing ADR covers the topic: update it in place.** Do not mark it
     superseded and do not add a replacement ADR. Keep `Status: accepted` and rewrite
     the Decision and Consequences — and the Context, if the reasoning changed — so the
     file describes the decision as it now stands and argues for the old one nowhere.
     The old version lives in git history; the commit message says what changed and
     why.
   - **No existing ADR covers it** and the change is a decision worth recording: add
     `adr/NNNN-slug.md` with the next number, in the existing format (`# N. Title`,
     `Status: accepted`, then Context, Decision, Consequences), and a row in
     `adr/README.md`.
   - Then look for anything that now contradicts the updated ADR: other ADRs,
     README.md, text and comments in `keymap.py`, CLAUDE.md, these skills.
     `grep -rn` for the ADR's number, the keycodes and the positions involved. Fix what
     you find **in a separate commit** (step 9).

7. **`make all`.** It exits 2 on any failure, so read the output. `build` and `render`
   run before the tests: after a test failure the artifacts are already regenerated,
   and a populated `git status` does not mean the change is sound.

   | Failure | Meaning | Next |
   | --- | --- | --- |
   | `KeycodeError: … unknown keycode '…'` — the build stops, only `keymap.py` changed | not in the vocabulary | fix the spelling, or step 4 |
   | `ValueError` about a row's length or the layer indices | the edit broke the structure | fix the edit |
   | `PortLedgerTest.test_nothing_was_invented_without_being_recorded` — `Items in the first set but not the second:` then the keycode | a keycode the port ledger has never seen | **consult the user** |
   | `PortLedgerTest.test_every_ergodox_key_is_accounted_for (keycode='…', verdict='kept')` | an ErgoDox key recorded as kept no longer appears anywhere | **consult the user** |
   | `PortLedgerTest.test_the_dual_role_keys_are_where_the_ledger_says` | a dual-role key moved from `[3][4]` / `[7][4]` (adr/0004, adr/0006) | **consult the user** |
   | `SettingsTest.test_tap_hold_decision_is_event_based_not_time_based` | setting 7, 22, 23, 26 or 27 changed (adr/0004) | **consult the user** |
   | `ReversalTest.test_outermost_right_keys_land_in_column_zero` | the right half was written in storage order, or one of the base keys it pins moved: BkSp, Enter (adr/0008), RShift, RAlt (adr/0008, adr/0009), Y, RGui (adr/0006, adr/0008) | check visual order first; if the move was intended, **consult the user** |
   | `RenderTest.test_right_encoder_locks_the_screen` | the base right encoder push `[5][6]` changed (adr/0007) | **consult the user** |
   | `VendorPreservationTest`, `VendorTemplateTest` | `vendor/` or layers 3-9 changed | revert; never intended |

   ### Consulting the user about a failing test

   **Never make a test pass on your own** — not by editing the test, not by editing
   `ERGODOX_DISPOSITION`, not by changing a pinned expectation. These tests carry
   recorded decisions, and a failure is the moment to surface one. Stop and tell the
   user:

   - which test failed, with the failure line;
   - what it protects — the ledger's claim, or the ADR the pinned value comes from;
   - why this change trips it;
   - the choices below, and which you recommend and why.

   Then do what they choose, and run `make all` again until it passes.

   | Failing test | Choices |
   | --- | --- |
   | `test_nothing_was_invented_without_being_recorded` | The ledger records what became of the ErgoDox's keys; it has no entry for a key new to the Cornix, and the only such keys, `USER00`-`USER02`, are listed inside the test itself. (a) Add the keycode to that set in the test, with a comment giving the reason — the existing precedent. (b) Record it in `ERGODOX_DISPOSITION` as `REPLACED` from an ErgoDox key — only if it really takes over that key's job. (c) Drop the new key. |
   | `test_every_ergodox_key_is_accounted_for` | (a) Change its verdict in `ERGODOX_DISPOSITION`: `DROPPED` with a reason, or `REPLACED` with the new keycode. (b) Keep the key, somewhere else. (c) Drop the request. |
   | `test_the_dual_role_keys_are_where_the_ledger_says`, `SettingsTest`, the `ReversalTest` position pins, `test_right_encoder_locks_the_screen` | (a) Change the decision: update the ADR (step 6) and the pinned expectation in the test, in the same commit. (b) Adjust or drop the request. |

8. **Prove the change reached every document.**

   - `make check` exits 0 and prints `… is up to date` for both artifacts. It compares
     without regenerating, so it proves `build/oklahomer.vil` is what `keymap.py`
     produces and `docs/layers.md` is what that artifact renders. A `… is stale; run
     'make build'` line means `make all` has not run since the last edit.
   - `git status --porcelain` matches the kind of change:

     | Change | Must change | Must not change |
     | --- | --- | --- |
     | a key in layers 0-2, encoder push-buttons included | `keymap.py`, `build/oklahomer.vil`, `docs/layers.md` | `vendor/` |
     | a QMK setting only | `keymap.py`, `build/oklahomer.vil` | `docs/layers.md` — settings are not rendered — and `vendor/` |

     Plus `adr/`, README.md and tests only as agreed. A key change with
     `docs/layers.md` untouched means `make all` did not run, or the edit changed
     nothing.
   - Read the affected layer in `docs/layers.md`. The diagram must show the new key
     where the user asked, and the matrix table must hold it at the planned
     `[row][col]`. This is the only check on physical position. If a label is
     truncated or unclear, a `SHORT` entry in `render.py` fixes it — a code change;
     tell the user.
   - Compare the layer's `doc` diagram in `keymap.py` against that rendering: the same
     keys in the same places.
   - `grep -n` README.md for the keycodes, labels and positions involved and fix what
     is now wrong — "The layers", "QMK Settings" and "Checking it on the hardware"
     all describe specific keys.

9. **Commit** once `make check` passes and the user agrees. Never push without asking
   first, every time.

   - **Commit 1** — the change itself: `keymap.py`, the regenerated
     `build/oklahomer.vil` and `docs/layers.md`, README.md updates describing the new
     layout, the ADR update or addition, and any test or ledger change the user chose.
     These go together because the pre-commit hook runs `make check`, and a pinned
     test has to change with the value it pins.
   - **Commit 2** — only if step 6 found content contradicting the updated ADR: fix it
     separately, so commit 1 reads as the decision and commit 2 as its consequences.
   - Messages follow the repository's conventional format and say which ADR changed
     and why.

## After the change

Report hardware verification as pending, as CLAUDE.md requires. Ask the user to load
`build/oklahomer.vil`, export it again and run `make import FILE=<export>` — it should
print `no differences between …` (the vial-import skill explains the other outputs) —
then run the checks in README.md, "Checking it on the hardware", that cover the keys
that changed. If a QMK setting changed, remind them that a layout load does not
necessarily carry settings (README.md, "Applying it to the keyboard").
