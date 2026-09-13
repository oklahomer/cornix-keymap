---
name: change-keymap
description: Change the keymap because the user asked for it — add, move, remove or swap keys, change an encoder push-button, or change a QMK setting — by editing keymap.py, carrying the change through build/ and docs/, keeping adr/ consistent, and proving it with make. Use for requests like "put Up on the left thumb", "swap these two keys" or "drop the mouse keys". Not for edits the user already made in the Vial GUI; use vial-import for those.
argument-hint: <what to change>
---

# Changing the keymap

If this skill was invoked with arguments, they are the request: $ARGUMENTS
Otherwise the request is in the conversation. Run every command below from the
repository root.

`keymap.py` is the only hand-edited source of the layers and settings (adr/0002).
`build/oklahomer.vil` and `docs/layers.md` follow from it and change only through
`make`, and `adr/` records why things are where they are. ADRs, README.md, and any
test or ledger entry the user agrees to, are edited by hand as the steps describe. A
change is finished when all of them agree — and only part of that can be proved
mechanically:

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

Apart from stopping on a problem, the user is asked at most twice before editing: in
step 2, only if the target slot cannot be determined, and in step 4, with one plan
that settles everything else.

## Steps

1. **Start from a clean, consistent tree.**

   - Run `git status --short` and read `git diff` for anything already uncommitted. If
     those changes touch a file this request will edit or regenerate — `keymap.py`,
     `build/`, `docs/`, README.md, `adr/`, `tests/` — stop and ask the user how to keep
     them apart. Never overwrite, stage or commit changes you did not make without
     their agreement.
   - Run `make check`. A failure is either a stale artifact (`… is stale; run 'make
     build'`, or `… run 'make render'`) or a failing test; either way stop and report,
     and do not build a change on top of it.

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

   If you notice anything in the repository that is already wrong for a reason
   unrelated to this change — an ADR, README.md, a comment in `keymap.py` — tell the
   user separately. Do not fix it as part of the change.

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
     `docs/layers.md`). Then ask the ledger what each one is, replacing `KEYCODE...`
     with them:

     ```
     python3 - KEYCODE... <<'PY'
     import sys
     import keymap as k

     L = k.ERGODOX_DISPOSITION
     new_to_cornix = {"USER00", "USER01", "USER02"}  # listed inside the test itself
     for code in sys.argv[1:]:
         roles = []
         if code in L:
             roles.append(f"ledger key, verdict {L[code][0]!r}")
         roles += [f"destination of {src} ({v})" for src, (v, d) in L.items()
                   if v in (k.WRAPPED, k.REPLACED) and d == code]
         if code in new_to_cornix:
             roles.append("new to the Cornix, listed in the test")
         print(f"{code}: {'; '.join(roles) or 'NOT recorded'}")
     PY
     ```

     Then predict. An added keycode that is a ledger key with verdict `kept`, or new to
     the Cornix, passes, and so does removing `KC_NO` or `KC_TRNS`, which stay in use
     everywhere. Otherwise:
     - an added keycode that is `NOT recorded` fails
       `test_nothing_was_invented_without_being_recorded`;
     - an added keycode that is a ledger key with verdict `wrapped`, `replaced` or
       `dropped` fails `test_every_ergodox_key_is_accounted_for`, because the ledger
       says it must not appear;
     - a removed keycode that is a ledger key with verdict `kept`, or the destination of
       a `wrapped` or `replaced` entry, fails `test_every_ergodox_key_is_accounted_for`.
       The failure names the ledger key, not the keycode you removed: removing
       `LCG(KC_Q)` reports `keycode='LALT(LGUI(KC_POWER))', verdict='replaced'`;
     - a removed `USER00`-`USER02` fails
       `VendorPreservationTest.test_vendor_custom_keycodes_survive` (adr/0010).
   - **A QMK setting** must use an id the firmware exposes:
     `python3 -c 'import cornix; print(sorted(cornix.load_vil("vendor/cornix-default-keymap.vil")["settings"], key=int))'`.
     An id that is not listed is out of scope — a firmware question, not a keymap
     change; stop and say so.
   - **Pinned positions and values.** List them with
     `grep -nE '\]\[[0-9]+\], |\["[0-9]+"\], ' tests/test_keymap.py`. Reading the hits:
     `matrix[…]` and `layer_to_matrix(keymap.BASE_LAYER)[…]` pin the **base** layer of
     `keymap.py`; `settings[…]` and `document["settings"][…]` pin a setting;
     `layer0[…]` checks the vendor template and `layout[…][…][6]` a dead slot no edit
     can reach, so ignore both. A slot or setting of yours in that list fails its test.
     Setting 23 is also the worked example in
     `test_diff_reports_a_setting_whose_type_changed`, whose expected report line
     changes with it.
   - **README.md.** Grep it for the keycodes, labels and positions involved, then read
     the sections that describe the layout in prose — "The layers", "QMK Settings",
     "Checking it on the hardware" — because a summary such as "punctuation on the home
     row" names no keycode, and no grep finds it. The plan says what in README.md will
     change.
   - **Present the plan and wait for agreement** when any of these apply: the target
     slot is not empty; the keycode already appears elsewhere on the layer; an ADR is
     contradicted or made stale; a QMK setting changes; a test is predicted to fail;
     README.md has to change.
     The plan lists:
     - each slot as `[row][col]` before → after, and what is lost if it was occupied;
     - each ADR finding from step 3, and the edit you propose;
     - the files expected to change, README.md included;
     - each predicted test failure with its choices from the table in step 7, and the
       one you recommend and why, so that one answer from the user settles it.
   - When an ADR is contradicted, the choices are: drop the request, change the request
     so it fits, or change the decision (step 6). The user picks.
   - Otherwise — one empty slot, no ADR involved, no predicted failure, nothing in
     README.md to change — go ahead.

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
   | `PortLedgerTest.test_every_ergodox_key_is_accounted_for (keycode='…', verdict='…')` — it names the ledger key, which may not be the keycode you touched | `kept`: that key no longer appears. `wrapped` or `replaced`: the recorded destination no longer appears, or the source key itself now appears. `dropped`: the dropped key appears again | (a) change the ledger entry — its verdict or its destination — with a reason; (b) keep what the entry requires, somewhere in layers 0-2; (c) drop the request |
   | `PortLedgerTest.test_the_dual_role_keys_are_where_the_ledger_says` | a dual-role key moved from `[3][4]` / `[7][4]` (adr/0004, adr/0006) | (a) change the decision: update the ADR (step 6) and the pinned expectation, in the same commit; (b) adjust or drop the request |
   | `SettingsTest.test_tap_hold_decision_is_event_based_not_time_based` | setting 7, 22, 23, 26 or 27 changed (adr/0004) | as the row above |
   | `SettingsTest.test_we_only_set_ids_the_firmware_exposes` | `QMK_SETTINGS` has an id the vendor template does not | out of scope: take that setting back out and report |
   | `ReversalTest.test_outermost_right_keys_land_in_column_zero` | the right half was written in storage order, or a base key it pins moved: BkSp, Enter (adr/0008), RShift, RAlt (adr/0008, adr/0009), Y, RGui (adr/0006, adr/0008) | check the visual order first; if the move was intended, as the dual-role row |
   | `RenderTest.test_right_encoder_locks_the_screen` | the base right encoder push `[5][6]` changed (adr/0007) | as the dual-role row |
   | any assertion whose message starts `guard:` | a test's precondition about the current keymap no longer holds — `guard: adr/0004 expects 1` once setting 23 changes | the decision changed: as the dual-role row, updating the guard together with the ADR |
   | `RenderTest.test_labels_stay_within_the_cell_width` | a label is longer than six characters, which only a `SHORT` entry in `render.py` can produce | shorten the entry — a code change; tell the user |
   | `VendorPreservationTest.test_vendor_custom_keycodes_survive` | a `USER00`-`USER02` key was removed from layers 0-2; they are the firmware's own controls (adr/0010) | (a) keep it somewhere else in layers 0-2; (b) change the decision: update adr/0010 and the test; (c) drop the request |
   | `VendorPreservationTest.test_unowned_layers_are_untouched`, `test_every_other_top_level_field_is_untouched` | the generated document differs from the vendor template outside layers 0-2 and the settings — only a code change can do that, and this skill makes none | stop and report |
   | `VendorTemplateTest.test_template_is_the_recorded_factory_export` | `vendor/cornix-default-keymap.vil` itself changed | stop and report; do not restore it yourself — the change may be the user's |

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
   - README.md: make every change the plan listed, then grep again for the keycodes,
     labels and positions involved and re-read the sections step 4 names. Do not finish while anything in it is
     false or leaves out what the change did — "punctuation on the home row" once a
     symbol is added elsewhere.

9. **Commit** once the user agrees. Never push, open a pull request or merge without
   asking first, every time.

   - Run `make check` yourself immediately before committing. The pre-commit hook that
     also runs it lives in `.git/hooks`, is not cloned (README.md, "Building") and may
     be missing; CI runs it again on push.
   - Stage this change's files by name. Never `git add -A` or `git add .`, which sweep
     in changes that are not yours.
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

Only when the requested change is fully applied and the final `make check` passes —
committed or not — report hardware verification as pending until the user comes back
with a result, as CLAUDE.md requires. If the procedure stopped earlier, report what
blocked it instead, and do not ask the user to load or export anything.

For a finished change:

- ask them to load `build/oklahomer.vil`, export it again and run
  `make import FILE=<export>`, which should print `no differences between …` (the
  vial-import skill explains the other outputs);
- point them at the checks in README.md, "Checking it on the hardware", that cover the
  keys that changed. If none does, say exactly what to press and what should happen,
  and offer to add that check to README.md;
- if a QMK setting changed, remind them that a layout load does not necessarily carry
  settings (README.md, "Applying it to the keyboard").
