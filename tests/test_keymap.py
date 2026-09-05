"""Tests for the Cornix keymap generator.

Run with ``make test`` (``python3 -m unittest discover -s tests -t .``).
Standard library only, no virtualenv needed.
"""

from __future__ import annotations

import os
import unittest

import cornix
import gen_vil
import keymap
import render

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(HERE, "vendor", "cornix-default-keymap.vil")
ARTIFACT = os.path.join(HERE, "build", "oklahomer.vil")


def build_document() -> dict:
    return gen_vil.build(cornix.load_vil(TEMPLATE))


def used_keycodes(document: dict, layers=cornix.OWNED_LAYERS) -> set[str]:
    return {
        value
        for layer, _row, _col, value in cornix.iter_slots(document["layout"])
        if layer in layers and value != cornix.UNUSED
    }


class ReversalTest(unittest.TestCase):
    """The right half is stored in reverse visual order.

    The vendor's own keymap proves it: their arrow cluster only makes physical
    sense once the row is reversed, and Up must sit directly above Down.
    """

    def setUp(self):
        self.stock = cornix.load_vil(TEMPLATE)

    def test_stock_arrow_row_reads_correctly_when_reversed(self):
        row = self.stock["layout"][0][7][: cornix.MAIN_COLS]
        self.assertEqual(
            cornix.to_storage_right(row),
            ["KC_SPACE", "MO(4)", "MO(2)", "KC_LEFT", "KC_DOWN", "KC_RIGHT"],
        )

    def test_stock_up_sits_above_down(self):
        layer0 = self.stock["layout"][0]
        self.assertEqual(layer0[6][1], "KC_UP")
        self.assertEqual(layer0[7][1], "KC_DOWN")

    def test_reversal_is_its_own_inverse(self):
        row = ["a", "b", "c", "d", "e", "f"]
        self.assertEqual(cornix.to_storage_right(cornix.to_storage_right(row)), row)

    def test_outermost_right_keys_land_in_column_zero(self):
        matrix = cornix.layer_to_matrix(keymap.BASE_LAYER)
        self.assertEqual(matrix[4][0], "KC_BSPACE")
        self.assertEqual(matrix[5][0], "KC_ENTER")
        self.assertEqual(matrix[6][0], "KC_RSHIFT")
        self.assertEqual(matrix[7][0], "KC_RALT")
        # ...and the innermost ones in column 5.
        self.assertEqual(matrix[4][5], "KC_Y")
        self.assertEqual(matrix[7][5], "KC_RGUI")


class RoundTripTest(unittest.TestCase):
    def test_matrix_round_trips_back_to_the_source_layout(self):
        for layer in keymap.LAYERS:
            with self.subTest(layer=layer.name):
                view = cornix.matrix_to_visual(cornix.layer_to_matrix(layer))
                self.assertEqual(view["left_main"], [list(r) for r in layer.left_main])
                self.assertEqual(view["right_main"], [list(r) for r in layer.right_main])
                self.assertEqual(view["left_bottom"], list(layer.left_bottom))
                self.assertEqual(view["right_bottom"], list(layer.right_bottom))
                self.assertEqual(view["left_encoder"], layer.left_encoder)
                self.assertEqual(view["right_encoder"], layer.right_encoder)


class ShapeTest(unittest.TestCase):
    def setUp(self):
        self.document = build_document()

    def test_generated_document_has_the_shape_the_firmware_expects(self):
        cornix.check_shape(self.document)

    def test_unwired_slots_stay_unused_on_every_layer(self):
        for layer, row, col, value in cornix.iter_slots(self.document["layout"]):
            if (row, col) in cornix.DEAD_SLOTS:
                self.assertEqual(value, cornix.UNUSED, f"layer {layer} [{row}][{col}]")

    def test_encoder_push_slots_are_populated(self):
        for row, col in cornix.ENCODER_PUSH.values():
            for layer in cornix.OWNED_LAYERS:
                self.assertNotEqual(self.document["layout"][layer][row][col], cornix.UNUSED)

    def test_rejects_a_row_of_the_wrong_length(self):
        broken = keymap.BASE_LAYER._replace(left_bottom=["KC_A"])
        with self.assertRaises(ValueError):
            cornix.layer_to_matrix(broken)


class VendorPreservationTest(unittest.TestCase):
    """Only the layers this repository owns, plus the settings, may change."""

    def setUp(self):
        self.template = cornix.load_vil(TEMPLATE)
        self.document = build_document()

    def test_every_other_top_level_field_is_untouched(self):
        for key in set(self.template) | set(self.document):
            if key in ("layout", "settings"):
                continue
            with self.subTest(field=key):
                self.assertEqual(self.document[key], self.template[key])

    def test_unowned_layers_are_untouched(self):
        for index in range(cornix.N_LAYERS):
            if index in cornix.OWNED_LAYERS:
                continue
            with self.subTest(layer=index):
                self.assertEqual(self.document["layout"][index], self.template["layout"][index])

    def test_vendor_custom_keycodes_survive(self):
        used = used_keycodes(self.document)
        for code in ("USER00", "USER01", "USER02"):
            self.assertIn(code, used, "the firmware's own keycodes must stay reachable")


class VocabularyTest(unittest.TestCase):
    def test_every_emitted_keycode_is_one_vial_can_parse(self):
        for layer, row, col, value in cornix.iter_slots(build_document()["layout"]):
            if value == cornix.UNUSED:
                continue
            with self.subTest(slot=f"{layer}[{row}][{col}]"):
                self.assertTrue(cornix.is_valid_keycode(value), value)

    def test_modern_qmk_aliases_are_rejected(self):
        # KC_LSFT is what the ErgoDox source says; this firmware wants KC_LSHIFT.
        self.assertFalse(cornix.is_valid_keycode("KC_LSFT"))
        self.assertEqual(cornix.to_legacy("KC_LSFT"), "KC_LSHIFT")

    def test_nested_modifiers_and_mod_taps_are_accepted(self):
        self.assertTrue(cornix.is_valid_keycode("LALT(LGUI(KC_POWER))"))
        self.assertTrue(cornix.is_valid_keycode("LSFT_T(KC_ESCAPE)"))
        self.assertFalse(cornix.is_valid_keycode("LSFT_T(MO(1))"))


class PortLedgerTest(unittest.TestCase):
    """The ledger in keymap.py must keep telling the truth."""

    def setUp(self):
        self.used = used_keycodes(build_document())

    def test_every_ergodox_key_is_accounted_for(self):
        for keycode, (verdict, detail) in keymap.ERGODOX_DISPOSITION.items():
            with self.subTest(keycode=keycode, verdict=verdict):
                if verdict == keymap.KEPT:
                    self.assertIn(keycode, self.used)
                elif verdict == keymap.WRAPPED:
                    self.assertIn(detail, self.used)
                    self.assertNotIn(keycode, self.used)
                elif verdict == keymap.DROPPED:
                    self.assertNotIn(keycode, self.used)
                else:
                    self.fail(f"unknown verdict {verdict!r}")

    def test_nothing_was_invented_without_being_recorded(self):
        recorded = set(keymap.ERGODOX_DISPOSITION)
        recorded |= {
            detail
            for verdict, detail in keymap.ERGODOX_DISPOSITION.values()
            if verdict == keymap.WRAPPED
        }
        # Keycodes that are new to the Cornix rather than ported from the ErgoDox.
        recorded |= {"USER00", "USER01", "USER02"}
        self.assertEqual(self.used - recorded, set())

    def test_the_dual_role_keys_are_where_the_ledger_says(self):
        matrix = cornix.layer_to_matrix(keymap.BASE_LAYER)
        self.assertEqual(matrix[3][4], "LSFT_T(KC_ESCAPE)")
        self.assertEqual(matrix[7][4], "LCTL_T(KC_SPACE)")


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.template = cornix.load_vil(TEMPLATE)

    def test_we_only_set_ids_the_firmware_exposes(self):
        self.assertLessEqual(set(keymap.QMK_SETTINGS), set(self.template["settings"]))

    def test_tap_hold_decision_is_event_based_not_time_based(self):
        settings = keymap.QMK_SETTINGS
        self.assertEqual(settings["23"], 1, "hold on other key press must be on")
        self.assertEqual(settings["22"], 0, "exactly one hold-decision rule")
        self.assertEqual(settings["26"], 0, "chordal hold would break same-hand chords")
        self.assertEqual(settings["27"], 0, "flow tap would suppress holds while typing fast")
        self.assertEqual(settings["7"], 200, "tapping term matches the ErgoDox")


class ArtifactTest(unittest.TestCase):
    def test_committed_artifact_matches_the_source(self):
        if not os.path.exists(ARTIFACT):
            self.skipTest("build/oklahomer.vil has not been generated yet")
        self.assertEqual(cornix.load_vil(ARTIFACT), build_document(),
                         "build/oklahomer.vil is stale; run 'make build'")


class RenderTest(unittest.TestCase):
    def test_labels_stay_within_the_cell_width(self):
        for value in used_keycodes(build_document()):
            with self.subTest(keycode=value):
                self.assertLessEqual(len(render.label(value)), render.CELL)

    def test_diff_reports_a_changed_slot(self):
        document = build_document()
        other = cornix.load_vil(TEMPLATE)
        report = render.diff(document, other)
        self.assertTrue(any("[3][4]" in line for line in report))

    def test_diff_of_a_document_with_itself_is_empty(self):
        document = build_document()
        self.assertEqual(render.diff(document, document), [])


if __name__ == "__main__":
    unittest.main()
