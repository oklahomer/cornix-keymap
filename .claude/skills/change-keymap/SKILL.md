---
name: change-keymap
description: Change the keymap because the user asked for it — add, move, remove or swap keys, change an encoder push-button, or change a QMK setting — by editing keymap.py, carrying the change through build/ and docs/, keeping adr/ consistent, and proving it with make. Use for requests like "put Up on the left thumb", "swap these two keys" or "drop the mouse keys". Not for edits the user already made in the Vial GUI; use vial-import for those.
argument-hint: <what to change>
---

# Changing the keymap

If this skill was invoked with arguments, they are the request: $ARGUMENTS
Otherwise the request is in the conversation. Run every command below from the
repository root.

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
| README.md is still right | nothing — steps 4 and 8 |
| the change agrees with the ADRs | nothing reliable — step 3 |

`make check` compares both artifacts against the source without rewriting either,
then runs the whole test suite.

The last row of the table matters most. Tests catch some ADR violations by accident
and never name the ADR: moving right GUI onto the left side breaks adr/0008 and
surfaces as a port-ledger failure and a reversal failure, neither of which mentions
adr/0008.

Before editing, the user is asked at most twice: in step 2, only if the target slot
cannot be determined, and in step 4, with one plan that settles everything else.

## Steps

1. **Start from a consistent tree.** Run `make check`. A failure is either a stale
   artifact (`… is stale; run 'make build'`, or `… run 'make render'`) or a failing
   test; either way stop and report, and do not build a change on top of it. Note any
   uncommitted changes in `git status` that are not yours.

2. **Pin the request down physically.**

   - Read the affected layer in `docs/layers.md`. It is generated from the data, so it
     shows what is really on each key. Name every slot you will touch by its matrix
     position, for example `[3][1]`. A position named by its base-layer letter — "the
     Z position" — is the same `[row][col]` on the target layer.
   - Map positions to literals with the coordinate comments above `left_bottom` and
     `right_bottom` and the numbers under the rendered diagram. **Do not trust the
     module docstring's "the three flat keys …, then the three angled thumb-arc
     keys":** that holds for `left_bottom` only. `right_bottom` is written inner to
     outer, so it is the arc first — `[7][5]`, `[7][4]`, `[7][3]` — then the flat keys
     `[7][2]`, `[7][1]`, `[7][0]`.
   - The right half is written in visual order, inner to outer; the matrix stores it
     reversed (CLAUDE.md, "Writing a layer").
   - A slot is empty only when it holds `XX` — `KC_NO`, a blank cell. `__` — `KC_TRNS`,
     shown as `~` — is not empty: it passes the key from the layer below through, and
     overwriting it takes that key away on this layer.
   - **Ask now only if the request fits more than one slot** ("the left thumb" is three
     keys): nothing can be planned until the slot is known. Everything else that needs
     the user goes into the plan in step 4.
   - Note for that plan: what the target slot holds if it is not empty — overwriting it
     removes a function — and whether the keycode already sits elsewhere on the layer,
     in which case the user may mean move rather than add.
   - Out of scope — stop and say so: layers 3-9 and `vendor/` (adr/0010), adding or
     removing a layer (it changes `cornix.OWNED_LAYERS`, a code change), and encoder
     rotation (`encoder_layout`, carried over from the vendor template).

3. **Read every ADR before editing.** There are few and they are short. Read all of
   `adr/*.md` rather than guessing which apply: position, side, keycode spelling and
   settings are each pinned by a different one. Classify each against the change:

   | Finding | Meaning | Next |
   | --- | --- | --- |
   | contradicts | the change breaks the rule the ADR sets or the reasoning it records | the plan offers the user choices (step 4) |
   | makes a detail stale | the rule still holds, but something the ADR says about current contents stops being true: a table cell ("(unused)"), a sentence ("left empty", "mirroring the empty key"), or a fallback it records that is no longer available — adr/0007's "the empty flat bottom key on each half" | the plan proposes the edit (step 6); name a lost fallback explicitly |
   | stale only if the decision changes | the ADR restates part of a decision that another ADR makes and this change contradicts | list it under the "change the decision" choice |
   | unrelated | — | — |

   If you notice an ADR that is already wrong for a reason unrelated to this change,
   tell the user separately. Do not fix it as part of the change.

4. **Work out everything the change affects, then present one plan.**

   - **The keycode** must be one `cornix.is_valid_keycode` accepts:
     `python3 -c 'import cornix; print(cornix.is_valid_keycode("KC_UP"))'`. A chord of
     two or more modifiers uses Vial's combined name (`LCG(KC_Q)`, never nested), and a
     mod-tap wraps a basic key only. If the keycode is not accepted, do not guess a
     spelling: Vial turns a name it cannot parse into a dead key, silently (adr/0001).
     Ask the user to set the key in the Vial GUI and export, read the exact spelling
     from the file, and tell them that extending the vocabulary in `cornix.py` is a
     code change.
   - **The port ledger.** List every keycode the change adds, and every keycode it
     removes whose last use in layers 0-2 this is (check the matrix tables in
     `docs/layers.md`). Then see how the ledger records them. This builds the same set
     `test_nothing_was_invented_without_being_recorded` does:

     ```
     python3 - KC_UP KC_RGUI <<'PY'
     import sys
     import keymap as k

     L = k.ERGODOX_DISPOSITION
     recorded = set(L) | {d for v, d in L.values() if v in (k.WRAPPED, k.REPLACED)}
     recorded |= {"USER00", "USER01", "USER02"}  # listed inside the test itself
     for code in sys.argv[1:]:
         print(f"{code}: {'recorded' if code in recorded else 'NOT recorded'} {L.get(code, '')}")
     PY
     ```

     An added keycode that is `NOT recorded` will fail
     `test_nothing_was_invented_without_being_recorded`; a removed keycode recorded as
     `kept` will fail `test_every_ergodox_key_is_accounted_for`.
   - **Pinned positions and values.** List them with
     `grep -nE '\[[0-9]\]\[[0-9]\], "|settings\["[0-9]+"\]' tests/test_keymap.py`, and
     ignore the `layer0[…]` lines, which check the vendor template rather than
     `keymap.py`. A slot or setting of yours in that list fails its test.
   - **README.md.** `grep -n` it for the keycodes, labels and positions involved, so the
     plan can say what in it will change.
   - **Present the plan and wait for agreement** when any of these apply: the target
     slot is not empty; the keycode already appears elsewhere on the layer; an ADR is
     contradicted or made stale; a QMK setting changes; a test is predicted to fail.
     The plan lists:
     - each slot as `[row][col]` before → after, and what is lost if it was occupied;
     - each ADR finding from step 3, and the edit you propose;
     - the files expected to change, README.md included;
     - each predicted test failure with its choices from the table in step 7, and the
       one you recommend and why, so that one answer from the user settles it.
   - When an ADR is contradicted, the choices are: drop the request, change the request
     so it fits, or change the decision (step 6). The user picks.
   - Otherwise — one empty slot, no ADR involved, no predicted failure — go ahead.

5. **Edit `keymap.py`.** For every layer touched, in the same edit:

   - the literals, in visual order;
   - the layer's `doc` diagram. Nothing reads it — not the generator, the renderer or
     the tests — so a stale diagram passes everything. This step is all that keeps it
     true;
   - the explanatory text under the diagram and the comments next to the literals,
     including ADR links;
   - `QMK_SETTINGS` and its comment, if a setting changes;
   - the test and ledger choices the user made in step 4. When a ledger verdict
     changes, also fix reason strings that describe the keys involved — for example
     `"KC_LGUI": (KEPT, "left thumb")` once a Left GUI sits on the right.

   Do not edit `build/`, `docs/` or `vendor/`, and do not touch any test or ledger entry
   the user has not agreed to.

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
   - Then find anything that now contradicts the updated ADR — other ADRs, README.md,
     text and comments in `keymap.py`, CLAUDE.md, these skills. A grep is where the
     search starts, not where it ends: look for the ADR's number, the keycodes and
     positions, and the words that describe the slot's state ("empty", "unused",
     "fallback", "mirror"), then read the hits in context, because prose rarely names a
     keycode. Fix what you find **in a separate commit** (step 9).

7. **`make all`.** It exits 2 on any failure, so read the output. `build` and `render`
   run before the tests: after a test failure the artifacts are already regenerated,
   and a populated `git status` does not mean the change is sound. One change can trip
   several tests at once.

   | Failure | Meaning | Choices, if the user has not already decided |
   | --- | --- | --- |
   | `KeycodeError: … unknown keycode '…'` — the build stops, only `keymap.py` changed | not in the vocabulary | fix the spelling, or back to step 4 |
   | `ValueError` about a row's length or the layer indices | the edit broke the structure | fix the edit |
   | `PortLedgerTest.test_nothing_was_invented_without_being_recorded` — `Items in the first set but not the second:`, then the keycode | an added keycode the ledger has never seen. The ledger records what became of the ErgoDox's keys and has no entry for a key new to the Cornix; the only such keys, `USER00`-`USER02`, are listed inside the test itself | (a) add the keycode to that set in the test, with a comment giving the reason — the existing precedent; (b) record it in `ERGODOX_DISPOSITION` as `REPLACED` from an ErgoDox key, only if it really takes over that key's job; (c) drop the new key |
   | `PortLedgerTest.test_every_ergodox_key_is_accounted_for (keycode='…', verdict='kept')` | an ErgoDox key recorded as kept no longer appears | (a) change its verdict: `DROPPED` with a reason, or `REPLACED` with the new keycode; (b) keep the key somewhere else; (c) drop the request |
   | `PortLedgerTest.test_the_dual_role_keys_are_where_the_ledger_says` | a dual-role key moved from `[3][4]` / `[7][4]` (adr/0004, adr/0006) | (a) change the decision: update the ADR (step 6) and the pinned expectation, in the same commit; (b) adjust or drop the request |
   | `SettingsTest.test_tap_hold_decision_is_event_based_not_time_based` | setting 7, 22, 23, 26 or 27 changed (adr/0004) | as the row above |
   | `ReversalTest.test_outermost_right_keys_land_in_column_zero` | the right half was written in storage order, or a base key it pins moved: BkSp, Enter (adr/0008), RShift, RAlt (adr/0008, adr/0009), Y, RGui (adr/0006, adr/0008) | check the visual order first; if the move was intended, as the dual-role row |
   | `RenderTest.test_right_encoder_locks_the_screen` | the base right encoder push `[5][6]` changed (adr/0007) | as the dual-role row |
   | `RenderTest.test_labels_stay_within_the_cell_width` | a label is longer than six characters, which only a `SHORT` entry in `render.py` can produce | shorten the entry — a code change; tell the user |
   | `VendorPreservationTest`, `VendorTemplateTest` | `vendor/` or layers 3-9 changed | revert; never intended |

   ### When a test fails

   - **A failure the agreed plan predicted** is already handled: its choice was applied
     in step 5. If it still fails, the edit does not match the plan — fix the edit.
   - **Any other failure: never make it pass on your own** — not by editing the test,
     not by editing `ERGODOX_DISPOSITION`, not by changing a pinned expectation. These
     tests carry recorded decisions, and an unplanned failure is the moment to surface
     one. Stop and tell the user which test failed, with the failure line; what it
     protects, the ledger's claim or the ADR the pinned value comes from; why this
     change trips it; and the choices from the table, with the one you recommend and
     why. Then do what they choose.

   Run `make all` again until it passes.

8. **Prove the change reached every document.**

   - `make check` exits 0, having printed `… is up to date` for both artifacts before
     the tests ran. That proves `build/oklahomer.vil` is what `keymap.py` produces and
     `docs/layers.md` is what that artifact renders. A `… is stale` line means
     `make all` has not run since the last edit.
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
     `[row][col]`. This is the only check on physical position. If a label is truncated
     or unclear, a `SHORT` entry in `render.py` fixes it — a code change; tell the user.
   - Compare the layer's `doc` diagram in `keymap.py` against that rendering: the same
     keys in the same places.
   - README.md: make the changes the plan listed, and grep again for anything the plan
     missed. Fix what is now wrong. Where a description is only incomplete —
     "punctuation on the home row" once a symbol is added elsewhere — point it out and
     let the user decide.

9. **Commit** once the user agrees. Never push without asking first, every time.

   - Run `make check` yourself immediately before committing. The pre-commit hook that
     also runs it lives in `.git/hooks`, is not cloned (README.md, "Building") and may
     be missing; CI runs it again on push.
   - **Commit 1** — the change itself: `keymap.py`, the regenerated
     `build/oklahomer.vil` and `docs/layers.md`, README.md updates describing the new
     layout, the ADR update or addition, and any test or ledger change the user chose.
     They go together because `make check` has to pass at every commit, and a pinned
     test has to change with the value it pins.
   - **Commit 2** — only if step 6 found content contradicting the updated ADR: fix it
     separately, so commit 1 reads as the decision and commit 2 as its consequences.
   - Messages follow the repository's conventional format and say which ADR changed
     and why.

## Reporting back

Whether or not anything was committed, end by reporting hardware verification as
pending until the user comes back with a result, as CLAUDE.md requires:

- ask them to load `build/oklahomer.vil`, export it again and run
  `make import FILE=<export>`, which should print `no differences between …` (the
  vial-import skill explains the other outputs);
- point them at the checks in README.md, "Checking it on the hardware", that cover the
  keys that changed. If none does, say exactly what to press and what should happen,
  and offer to add that check to README.md;
- if a QMK setting changed, remind them that a layout load does not necessarily carry
  settings (README.md, "Applying it to the keyboard").
