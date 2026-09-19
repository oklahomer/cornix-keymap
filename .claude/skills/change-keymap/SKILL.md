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

Two reference files hold the tables, commands and examples. Read the whole file when a
step sends you to it:

| File | Read it at |
| --- | --- |
| `.claude/skills/change-keymap/references/adrs.md` | step 3, and again at step 6 if an ADR is to change |
| `.claude/skills/change-keymap/references/tests.md` | step 4, and again at step 7 if `make all` fails |

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
     `right_bottom` and the numbers under the rendered diagram. `left_bottom` runs
     outer to inner: the flat keys `[3][0]`, `[3][1]`, `[3][2]`, then the arc `[3][3]`,
     `[3][4]`, `[3][5]`. `right_bottom` runs inner to outer, so it is the arc first —
     `[7][5]`, `[7][4]`, `[7][3]` — then the flat keys `[7][2]`, `[7][1]`, `[7][0]`.
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
     in which case the user may mean move rather than add. For a key added to BASE, also
     note whether SYMB and MDIA hold `__` or `XX` in that slot: with `XX`, the new key is
     unavailable while that layer is held.
   - Out of scope — stop and say so: layers 3-9 and `vendor/` (adr/0010), adding or
     removing a layer (it changes `cornix.OWNED_LAYERS`, a code change), and encoder
     rotation (`encoder_layout`, carried over from the vendor template).

3. **Read every ADR before editing.** There are few and they are short. Read all of
   `adr/*.md` rather than guessing which apply: position, side, keycode spelling and
   settings are each pinned by a different one. Then read `references/adrs.md` and
   classify each ADR against the change — contradicts, makes a detail stale, stale only
   if the decision changes, or unrelated.

   If you notice anything in the repository that is already wrong for a reason
   unrelated to this change — an ADR, README.md, a comment in `keymap.py` — tell the
   user in a separate section at the end of the plan or the final report, apart from
   anything they have to decide. Do not fix it as part of the change.

4. **Work out everything the change affects, then present one plan.**

   - **The keycode** must be one `cornix.is_valid_keycode` accepts:
     `python3 -c 'import cornix; print(cornix.is_valid_keycode("KC_UP"))'`. A chord of
     two or more modifiers uses Vial's combined name (`LCG(KC_Q)`, never nested), and a
     mod-tap wraps a basic key only. If the keycode is not accepted, do not guess a
     spelling: Vial turns a name it cannot parse into a dead key, silently (adr/0001).
     Ask the user to set the key in the Vial GUI and export, read the exact spelling
     from the file, and tell them that extending the vocabulary in `cornix.py` is a
     code change.
   - **A QMK setting** must use an id the firmware exposes:
     `python3 -c 'import cornix; print(sorted(cornix.load_vil("vendor/cornix-default-keymap.vil")["settings"], key=int))'`.
     An id that is not listed is out of scope — a firmware question, not a keymap
     change; stop and say so.
   - **Tests.** Read `references/tests.md`. Use "Predicting failures before editing" to
     predict every test the change will fail — the port ledger, the pinned positions and
     settings, the vendor keycodes — before anything is edited, and take each predicted
     failure's choices from "Reading a failure".
   - **README.md.** Grep it for the keycodes, labels and positions involved, then read
     the sections that describe the layout in prose — "The layers", "QMK Settings",
     "Checking it on the hardware" — because a summary such as "punctuation on the home
     row" names no keycode, and no grep finds it. Hits under "The keyboard" describe the
     vendor's stock keymap, not this one. The plan says what in README.md will change,
     and when no hardware check covers the changed keys, it proposes one.
   - **Present the plan and wait for agreement** when any of these apply: the target
     slot is not empty; the keycode already appears elsewhere on the layer; an ADR is
     contradicted or made stale; a QMK setting changes; a test is predicted to fail;
     README.md has to change. The plan lists:
     - each slot as `[row][col]` before → after, and what is lost if it was occupied;
     - each ADR finding from step 3 other than "unrelated", and the edit you propose;
     - the files expected to change, README.md included;
     - each predicted test failure with its choices from `references/tests.md`, and the
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

6. **Update or add ADRs** — only as agreed in step 4, and as `references/adrs.md`,
   "Updating or adding an ADR", describes. The rules that govern it:

   - A stale detail is corrected where it stands — that cell or sentence only — as part
     of the change itself.
   - When the decision itself changes, the ADR that covers it is **updated in place** —
     never marked superseded, never replaced by a new ADR.
   - A new ADR is added only when no existing one covers the topic.
   - After a decision changes, anything left contradicting the updated ADR is fixed
     **in a separate commit** (step 9).

7. **`make all`.** It exits 2 on any failure, so read the output. `build` and `render`
   run before the tests: after a test failure the artifacts are already regenerated,
   and a populated `git status` does not mean the change is sound. One change can trip
   several tests at once. Look up every failure in `references/tests.md`, "Reading a
   failure".

   - **A failure the agreed plan predicted** is already handled: its choice was applied
     in step 5. If it still fails, the edit does not match the plan — fix the edit.
   - **Any other failure: never make it pass on your own** — not by editing the test,
     not by editing `ERGODOX_DISPOSITION`, not by changing a pinned expectation. These
     tests carry recorded decisions, and an unplanned failure is the moment to surface
     one. Stop, consult the user as `references/tests.md` describes, and do what they
     choose.

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
     labels and positions involved and re-read the sections step 4 names. Do not finish
     while anything in it is false or leaves out what the change did — "punctuation on
     the home row" once a symbol is added elsewhere.

9. **Commit** once the user agrees. Never push, open a pull request or merge without
   asking first, every time.

   - Run `make check` yourself immediately before committing. The pre-commit hook that
     also runs it lives in `.git/hooks`, is not cloned (README.md, "Building") and may
     be missing; CI runs it again on push.
   - Stage this change's files by name. Never `git add -A` or `git add .`, which sweep
     in changes that are not yours.
   - **Commit 1** — the change itself: `keymap.py`, the regenerated
     `build/oklahomer.vil` and `docs/layers.md`, README.md updates describing the new
     layout, stale ADR details corrected, the ADR update or addition, and any test or
     ledger change the user chose.
     They go together because `make check` has to pass at every commit, and a pinned
     test has to change with the value it pins.
   - **Commit 2** — only when a decision changed and step 6 found content contradicting
     the updated ADR: fix it separately, so commit 1 reads as the decision and commit 2
     as its consequences.
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
  keys that changed, including any added for this change. If the user declined to add
  one, say exactly what to press and what should happen;
- if a QMK setting changed, remind them that a layout load does not necessarily carry
  settings (README.md, "Applying it to the keyboard").
