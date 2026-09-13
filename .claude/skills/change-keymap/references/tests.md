# Tests: predicting failures, and reading them

Reference for the change-keymap skill. Its step 4 uses the first section to predict
failures before anything is edited, and the table in the second for the choices each
predicted failure offers; its step 7 uses the second when `make all` fails.

Several of these tests carry recorded decisions — the port ledger, the tap-hold
settings of adr/0004, positions other ADRs fix — so a failure is a question for the
user. Never make one pass on your own by editing the test, `ERGODOX_DISPOSITION` or a
pinned expectation.

## Predicting failures before editing

### The port ledger

List every keycode the change adds, and every keycode it removes whose last use in
layers 0-2 this is (check the matrix tables in `docs/layers.md`). Then ask the ledger
what each one is, replacing `KEYCODE...` with them:

```
python3 - KEYCODE... <<'PY'
import ast
import pathlib
import sys
import keymap as k

L = k.ERGODOX_DISPOSITION
# Keys new to the Cornix are the set literal inside the ledger test itself.
tree = ast.parse(pathlib.Path("tests/test_keymap.py").read_text())
test = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
            and n.name == "test_nothing_was_invented_without_being_recorded")
new_to_cornix = {e.value for n in ast.walk(test) if isinstance(n, ast.Set)
                 for e in n.elts if isinstance(e, ast.Constant)}
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

An added keycode that is a ledger key with verdict `kept`, or new to the Cornix,
passes, and so does removing `KC_NO` or `KC_TRNS`, which stay in use everywhere.
Otherwise:

- an added keycode that is `NOT recorded` fails
  `test_nothing_was_invented_without_being_recorded`;
- an added keycode that is a ledger key with verdict `wrapped`, `replaced` or `dropped`
  fails `test_every_ergodox_key_is_accounted_for`, because the ledger says it must not
  appear;
- a removed keycode that is a ledger key with verdict `kept`, or the destination of a
  `wrapped` or `replaced` entry, fails `test_every_ergodox_key_is_accounted_for`. The
  failure names the ledger key, not the keycode you removed: removing `LCG(KC_Q)`
  reports `keycode='LALT(LGUI(KC_POWER))', verdict='replaced'`;
- a removed `USER00`-`USER02` fails
  `VendorPreservationTest.test_vendor_custom_keycodes_survive` (adr/0010).

### Pinned positions and values

List them with `grep -nE '\]\[[0-9]+\], |\["[0-9]+"\], ' tests/test_keymap.py`. Reading
the hits:

- `matrix[…]` and `layer_to_matrix(keymap.BASE_LAYER)[…]` pin the **base** layer of
  `keymap.py`;
- `settings[…]` and `document["settings"][…]` pin a setting;
- `layer0[…]` checks the vendor template, and `layout[…][…][6]` a dead slot no edit can
  reach — ignore both.

A slot or setting of yours in that list fails its test. Setting 23 is also the worked
example in `test_diff_reports_a_setting_whose_type_changed`, whose expected report
line changes with it. The grep is a guide, not a complete list:
`test_diff_reports_a_changed_slot` also expects base `[3][4]` to differ from the vendor
template.

## Reading a failure

| Failure | Meaning | Choices, if the user has not already decided |
| --- | --- | --- |
| `KeycodeError: … unknown keycode '…'` — the build stops, only `keymap.py` changed | not in the vocabulary | fix the spelling, or go back to change-keymap step 4 |
| `ValueError` about a row's length or the layer indices | the edit broke the structure | fix the edit |
| `PortLedgerTest.test_nothing_was_invented_without_being_recorded` — `Items in the first set but not the second:`, then the keycode | an added keycode the ledger has never seen. The ledger records what became of the ErgoDox's keys and has no entry for a key new to the Cornix; the only such keys, `USER00`-`USER02`, are listed inside the test itself | (a) add the keycode to that set in the test, with a comment giving the reason — the existing precedent, though so far only for the firmware's own keys, and every later key new to the Cornix will need the same edit, so say so; (b) record it in `ERGODOX_DISPOSITION` as `REPLACED` from an ErgoDox key, only if it really takes over that key's job; (c) drop the new key |
| `PortLedgerTest.test_every_ergodox_key_is_accounted_for (keycode='…', verdict='…')` — it names the ledger key, which may not be the keycode you touched | `kept`: that key no longer appears. `wrapped` or `replaced`: the recorded destination no longer appears, or the source key itself now appears. `dropped`: the dropped key appears again | (a) change the ledger entry — its verdict or its destination — with a reason; (b) keep what the entry requires, somewhere in layers 0-2; (c) drop the request |
| `PortLedgerTest.test_the_dual_role_keys_are_where_the_ledger_says` | a dual-role key moved from `[3][4]` / `[7][4]` (adr/0004, adr/0006) | (a) change the decision: update the ADR (change-keymap step 6) and the pinned expectation, in the same commit; (b) adjust or drop the request |
| `SettingsTest.test_tap_hold_decision_is_event_based_not_time_based` | setting 7, 22, 23, 26 or 27 changed (adr/0004) | as the row above |
| `SettingsTest.test_we_only_set_ids_the_firmware_exposes` | `QMK_SETTINGS` has an id the vendor template does not | out of scope: take that setting back out and report |
| `ReversalTest.test_outermost_right_keys_land_in_column_zero` | the right half was written in storage order, or a base key it pins moved: BkSp, Enter (adr/0008), RShift, RAlt (adr/0008, adr/0009), Y, RGui (adr/0006, adr/0008) | check the visual order first; if the move was intended, as the dual-role row |
| `RenderTest.test_right_encoder_locks_the_screen` | the base right encoder push `[5][6]` changed (adr/0007) | as the dual-role row |
| any assertion whose message starts `guard:` | a test's precondition about the current keymap no longer holds — `guard: adr/0004 expects 1` once setting 23 changes | the decision changed: as the dual-role row, updating the guard together with the ADR |
| `RenderTest.test_labels_stay_within_the_cell_width` | a label is longer than six characters, which only a `SHORT` entry in `render.py` can produce | shorten the entry — a code change; tell the user |
| `VendorPreservationTest.test_vendor_custom_keycodes_survive` | a `USER00`-`USER02` key was removed from layers 0-2; they are the firmware's own controls (adr/0010) | (a) keep it somewhere else in layers 0-2; (b) change the decision: update adr/0010 and the test; (c) drop the request |
| `VendorPreservationTest.test_unowned_layers_are_untouched`, `test_every_other_top_level_field_is_untouched` | the generated document differs from the vendor template outside layers 0-2 and the settings — only a code change can do that, and the skill makes none | stop and report |
| `VendorTemplateTest.test_template_is_the_recorded_factory_export` | `vendor/cornix-default-keymap.vil` itself changed | stop and report; do not restore it yourself — the change may be the user's |

### Consulting the user

For a failure the agreed plan did not cover, stop and tell the user:

- which test failed, with the failure line;
- what it protects — the ledger's claim, or the ADR the pinned value comes from;
- why this change trips it;
- the choices from the table, and the one you recommend and why.

Then do what they choose.
