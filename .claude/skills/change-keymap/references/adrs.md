# ADRs: classifying a change, and updating a decision

Reference for the change-keymap skill. Its step 3 uses the first section; its step 6
uses the second.

## Classifying an ADR against a change

Read every ADR in `adr/`, then give each one of these findings:

| Finding | Meaning | What the plan does |
| --- | --- | --- |
| contradicts | the change breaks the rule the ADR sets, or the reasoning it records | offers the user choices: drop the request, change it so it fits, or change the decision |
| makes a detail stale | the rule still holds, but something the ADR says about current contents stops being true: a table cell ("(unused)"), a sentence ("left empty", "mirroring the empty key"), or a fallback it records that is no longer available | proposes the edit; names a lost fallback explicitly, since the user may not want to give it up |
| stale only if the decision changes | the ADR restates part of a decision that another ADR makes, and this change contradicts that other ADR | lists the edit under the "change the decision" choice only |
| unrelated | — | — |

Patterns the dry runs of this skill turned up. They quote the ADRs as they read when
this was written; always classify against the ADRs as they read now.

- **Filling a key an ADR describes as empty.** An ADR that lists a slot as "(unused)",
  calls it the place for anything new, says another key mirrors it, or names it as a
  fallback is not contradicted when the slot is filled — but each such statement goes
  stale, and a lost fallback is a real cost to name. adr/0006, adr/0007 and adr/0009
  all say something of this kind about the empty flat bottom keys.
- **Moving a key onto the other side.** Mapping one side's modifier onto the other
  side's key contradicts adr/0008. An ADR whose table merely names the original key in
  its place — adr/0006 names `RGui` on the right arc — is stale only if the user
  chooses to change adr/0008.

A Decision section can hold a table of current contents — adr/0006's arc order,
adr/0007's per-layer encoder table. Changing a cell of that table is "makes a detail
stale" while the rule the table illustrates still holds, and "contradicts" when it
breaks that rule.

## Updating or adding an ADR

Only as the user agreed in the plan.

- **A detail went stale** while the decision still holds: correct that cell or sentence
  and nothing else. Leave the rule and the reasoning alone, and commit the correction
  with the change itself (change-keymap, step 9).
- **The decision changed, and an existing ADR covers it: update it in place.** Do not
  mark it superseded and do not add a replacement ADR. Keep `Status: accepted` and rewrite the Decision
  and Consequences — and the Context, if the reasoning changed — so the file describes
  the decision as it now stands and argues for the old one nowhere. The old version
  lives in git history; the commit message says what changed and why.
- **No existing ADR covers it** and the change is a decision worth recording: add
  `adr/NNNN-slug.md` with the next number, in the existing format (`# N. Title`,
  `Status: accepted`, then Context, Decision, Consequences), and a row in
  `adr/README.md`.

After a decision changes, find anything that now contradicts the updated ADR — other ADRs, README.md, text
and comments in `keymap.py`, CLAUDE.md, these skills. A grep is where the search
starts, not where it ends: look for the ADR's number, the keycodes and positions, and
the words that describe the slot's state ("empty", "unused", "fallback", "mirror"),
then read the hits in context, because prose rarely names a keycode. Fix what you find
**in a separate commit** from the change itself (change-keymap, step 9).
