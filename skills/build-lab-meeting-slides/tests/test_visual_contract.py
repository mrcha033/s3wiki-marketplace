from __future__ import annotations

import importlib.util
import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "lab_slides.py"
SPEC = importlib.util.spec_from_file_location("lab_slides_visual_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
lab_slides = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab_slides)


def slide(number: int, family: str = "process-flow", *, basis: object = None, underfill: bool = False) -> dict:
    spec = {
        "anchor_type": "process",
        "family": family,
        "content_basis": basis if basis is not None else [f"claim-{number}"],
        "allow_underfill": underfill,
        "underfill_rationale": "Intentional sparse transition with one evidence anchor." if underfill else "",
    }
    return {
        "slide": number,
        "template_frame": {"role": "content"},
        "visual_contract": spec,
        "evidence_refs": [f"claim-{number}"],
        "native_elements": [
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "diagram-node",
                "position": {"left": 15, "top": 20, "width": 22, "height": 60},
            },
            {
                "type": "line",
                "visual_role": "connector",
                "position": {"left": 37, "top": 45, "width": 26, "height": 10},
            },
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "diagram-node",
                "position": {"left": 63, "top": 20, "width": 22, "height": 60},
            },
            {
                "type": "text",
                "text_role": "figure-label",
                "text": "Input",
                "position": {"left": 16, "top": 43, "width": 20, "height": 10},
            },
            {
                "type": "text",
                "text_role": "figure-label",
                "text": "Output",
                "position": {"left": 64, "top": 43, "width": 20, "height": 10},
            },
        ],
    }


def frame_map(count: int) -> dict:
    return {
        "outputSlides": [
            {
                "outputSlide": number,
                "editTargets": [
                    {"action": "add", "zone": {"x": 0, "y": 0, "w": 100, "h": 100}}
                ],
            }
            for number in range(1, count + 1)
        ]
    }


class VisualContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "schema_version": 2,
            "style": {
                "active_palette": dict(lab_slides.DEFAULT_ACTIVE_PALETTE),
                "active_palette_sha256": lab_slides.active_palette_sha256(
                    lab_slides.DEFAULT_ACTIVE_PALETTE
                ),
            },
            "qa": {"visual_contract": dict(lab_slides.DEFAULT_VISUAL_CONTRACT)},
        }

    def test_content_anchor_and_coverage_pass(self) -> None:
        report = lab_slides.visual_contract_audit(
            self.config, {"slides": [slide(1)]}, frame_map(1)
        )
        self.assertEqual(report["status"], "pass", report)
        self.assertEqual(report["checks"][0]["figure_budget_profile"], "interaction")
        self.assertAlmostEqual(report["checks"][0]["figure_bbox_area_ratio"], 0.42)
        self.assertGreaterEqual(report["checks"][0]["information_area_ratio"], 0.08)

    def test_native_positions_use_the_production_builder_schema(self) -> None:
        entry = slide(1)
        entry["native_elements"][0]["position"] = {"x": 15, "y": 20, "w": 22, "h": 60}
        report = lab_slides.visual_contract_audit(
            self.config, {"slides": [entry]}, frame_map(1)
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(
            any("left/top/width/height" in error for error in report["errors"]),
            report,
        )

    def test_profile_budget_warns_before_hard_maximum(self) -> None:
        entry = slide(1)
        entry["native_elements"][0]["position"] = {"left": 15, "top": 15, "width": 25, "height": 70}
        entry["native_elements"][1]["position"] = {"left": 40, "top": 45, "width": 20, "height": 10}
        entry["native_elements"][2]["position"] = {"left": 60, "top": 15, "width": 25, "height": 70}
        report = lab_slides.visual_contract_audit(
            self.config, {"slides": [entry]}, frame_map(1)
        )
        self.assertEqual(report["status"], "pass", report)
        self.assertTrue(any("above the interaction preferred band" in item for item in report["warnings"]))

    def test_profile_budget_rejects_oversized_figure(self) -> None:
        entry = slide(1)
        entry["native_elements"][0]["position"] = {"left": 5, "top": 5, "width": 30, "height": 90}
        entry["native_elements"][1]["position"] = {"left": 35, "top": 45, "width": 30, "height": 10}
        entry["native_elements"][2]["position"] = {"left": 65, "top": 5, "width": 30, "height": 90}
        report = lab_slides.visual_contract_audit(
            self.config, {"slides": [entry]}, frame_map(1)
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("above the interaction hard maximum" in item for item in report["errors"]))

    def test_spoofed_closing_role_cannot_bypass_add_zone_figure_gate(self) -> None:
        entry = slide(1)
        entry["template_frame"]["role"] = "closing"
        entry["native_elements"] = []
        report = lab_slides.visual_contract_audit(
            self.config, {"slides": [entry]}, frame_map(1)
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("hard minimum" in item for item in report["errors"]))

    def test_missing_anchor_and_basis_fail(self) -> None:
        entry = slide(1, basis=[])
        entry.pop("visual_contract")
        report = lab_slides.visual_contract_audit(self.config, {"slides": [entry]}, frame_map(1))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("missing visual_contract" in error for error in report["errors"]))

    def test_forbidden_family_and_repetition_fail(self) -> None:
        plans = {"slides": [slide(1, "card-grid"), slide(2, "card-grid"), slide(3, "card-grid")]}
        report = lab_slides.visual_contract_audit(self.config, plans, frame_map(3))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("forbidden generic" in error for error in report["errors"]))
        self.assertTrue(any("repeats composition family" in error for error in report["errors"]))

    def test_repeated_rectangular_panel_sequence_is_blocked(self) -> None:
        plans = {"slides": [slide(1, "comparison-panel"), slide(2, "comparison-panel"), slide(3, "comparison-panel")]}
        report = lab_slides.visual_contract_audit(self.config, plans, frame_map(3))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("repeats composition family" in error for error in report["errors"]))
        self.assertTrue(any("composition signature" in error for error in report["errors"]))

    def test_body_slide_cannot_self_authorize_figure_exception(self) -> None:
        sparse = slide(1)
        sparse["native_elements"] = []
        report = lab_slides.visual_contract_audit(self.config, {"slides": [sparse]}, frame_map(1))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("hard minimum" in error for error in report["errors"]))
        sparse["visual_contract"]["allow_underfill"] = True
        sparse["visual_contract"]["underfill_rationale"] = "Intentional sparse transition with one evidence anchor."
        sparse["visual_contract"]["allow_figure_exception"] = True
        sparse["visual_contract"]["figure_exception_rationale"] = "No body figure is appropriate for this transition."
        report = lab_slides.visual_contract_audit(self.config, {"slides": [sparse]}, frame_map(1))
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("may not self-authorize underfill" in error for error in report["errors"]))
        self.assertTrue(any("may not self-authorize a figure exception" in error for error in report["errors"]))

    def test_text_only_area_does_not_satisfy_primary_figure(self) -> None:
        entry = slide(1)
        entry["native_elements"] = [
            {
                "type": "text",
                "text_role": "callout",
                "text": "Large text is not a figure",
                "position": {"left": 5, "top": 5, "width": 90, "height": 90},
            }
        ]
        report = lab_slides.visual_contract_audit(self.config, {"slides": [entry]}, frame_map(1))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("primary-figure bbox area" in error for error in report["errors"]))

    def test_raw_hex_and_unknown_colors_are_rejected(self) -> None:
        entry = slide(1)
        entry["native_elements"][0]["fill"] = "#0353A4"
        report = lab_slides.visual_contract_audit(self.config, {"slides": [entry]}, frame_map(1))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("raw hex" in error for error in report["errors"]))
        entry["native_elements"][0]["fill"] = "orange"
        report = lab_slides.visual_contract_audit(self.config, {"slides": [entry]}, frame_map(1))
        self.assertTrue(any("active palette tokens" in error for error in report["errors"]))

    def test_palette_tokens_and_declared_focus_pass(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["focus_target"] = "changed lane"
        entry["native_elements"][0]["fill"] = "soft"
        entry["native_elements"][0]["line"] = {"fill": "focus", "width": 2}
        report = lab_slides.visual_contract_audit(self.config, {"slides": [entry]}, frame_map(1))
        self.assertEqual(report["status"], "pass", report)

    def test_palette_values_and_token_set_are_template_pinned(self) -> None:
        entry = slide(1)
        changed = json.loads(json.dumps(self.config))
        changed["style"]["active_palette"]["focus"] = "#FF00FF"
        changed["style"]["active_palette"]["rogue"] = "#FF0000"
        changed["style"]["active_palette_sha256"] = lab_slides.active_palette_sha256(
            changed["style"]["active_palette"]
        )
        report = lab_slides.visual_contract_audit(
            changed,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("exactly" in error for error in report["errors"]))
        self.assertTrue(any("derived from the inspected template" in error for error in report["errors"]))

    def test_diagram_requires_nodes_and_connector(self) -> None:
        entry = slide(1)
        entry["native_elements"] = [entry["native_elements"][0]]
        report = lab_slides.visual_contract_audit(self.config, {"slides": [entry]}, frame_map(1))
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("diagram-node" in error for error in report["errors"]))
        self.assertTrue(any("connector" in error for error in report["errors"]))

    def test_connector_role_requires_line_path_or_arrow_geometry(self) -> None:
        entry = slide(1)
        entry["native_elements"][1] = {
            "type": "shape",
            "geometry": "rect",
            "visual_role": "connector",
            "position": {"left": 35, "top": 45, "width": 30, "height": 10},
        }
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(
            any("line/path/arrow connector" in error for error in report["errors"]),
            report,
        )

    def test_full_zone_rectangle_cannot_impersonate_plot(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "plot"
        entry["native_elements"] = [
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "plot",
                "position": {"left": 0, "top": 0, "width": 100, "height": 100},
            }
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("data-backed chart" in error for error in report["errors"]))

    def test_scalar_string_cannot_impersonate_chart_data(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "chart"
        entry["native_elements"] = [
            {
                "type": "chart",
                "visual_role": "plot",
                "series": "x",
                "position": {"left": 0, "top": 0, "width": 100, "height": 100},
            }
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("data-backed chart" in error for error in report["errors"]))

    def test_string_labels_cannot_impersonate_chart_data(self) -> None:
        for series in (
            ["x", "y"],
            [{"name": "x", "label": "First"}, {"name": "y", "label": "Second"}],
        ):
            entry = slide(1)
            entry["visual_contract"]["anchor_type"] = "chart"
            entry["native_elements"] = [
                {
                    "type": "chart",
                    "visual_role": "plot",
                    "series": series,
                    "position": {"left": 0, "top": 0, "width": 100, "height": 100},
                }
            ]
            report = lab_slides.visual_contract_audit(
                self.config,
                {"slides": [entry]},
                frame_map(1),
            )
            self.assertEqual(report["status"], "fail", report)
            self.assertTrue(
                any("data-backed chart" in error for error in report["errors"]),
                report,
            )

    def test_numeric_chart_data_remains_valid(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "chart"
        entry["native_elements"] = [
            {
                "type": "chart",
                "visual_role": "plot",
                "series": [1, 2],
                "position": {"left": 20, "top": 25, "width": 60, "height": 50},
            }
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "pass", report)

    def test_empty_code_box_cannot_impersonate_code_figure(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "code"
        entry["native_elements"] = [
            {
                "type": "code",
                "visual_role": "code",
                "position": {"left": 0, "top": 0, "width": 100, "height": 100},
            }
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(
            any("nonempty editable code" in error for error in report["errors"]),
            report,
        )

    def test_primitive_plot_requires_axes_and_data_marks(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "plot"
        entry["native_elements"] = [
            {
                "type": "line",
                "visual_role": "axis",
                "position": {"left": 20, "top": 20, "width": 2, "height": 60},
            },
            {
                "type": "line",
                "visual_role": "axis",
                "position": {"left": 20, "top": 78, "width": 60, "height": 2},
            },
            {
                "type": "shape",
                "visual_role": "data-mark",
                "value": 4,
                "position": {"left": 30, "top": 55, "width": 18, "height": 23},
            },
            {
                "type": "shape",
                "visual_role": "data-mark",
                "value": 9,
                "position": {"left": 57, "top": 35, "width": 18, "height": 43},
            },
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "pass", report)

    def test_boundary_and_tiny_unbound_marks_cannot_fake_figure_dominance(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "plot"
        entry["native_elements"] = [
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "boundary",
                "position": {"left": 0, "top": 0, "width": 100, "height": 100},
            },
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "axis",
                "position": {"left": 1, "top": 1, "width": 1, "height": 1},
            },
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "axis",
                "position": {"left": 2, "top": 2, "width": 1, "height": 1},
            },
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "data-mark",
                "position": {"left": 3, "top": 3, "width": 1, "height": 1},
            },
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "data-mark",
                "position": {"left": 4, "top": 4, "width": 1, "height": 1},
            },
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(
            any("data-backed chart" in error for error in report["errors"]),
            report,
        )
        self.assertLess(report["checks"][0]["information_area_ratio"], 0.01)
        self.assertLess(report["checks"][0]["figure_bbox_area_ratio"], 0.01)

    def test_unrelated_full_zone_role_cannot_inflate_plot_metrics(self) -> None:
        for unrelated in (
            {
                "type": "shape",
                "geometry": "rect",
                "visual_role": "diagram-node",
                "position": {"left": 0, "top": 0, "width": 100, "height": 100},
            },
            {
                "type": "code",
                "visual_role": "code",
                "code": "x = 1",
                "position": {"left": 0, "top": 0, "width": 100, "height": 100},
            },
        ):
            entry = slide(1)
            entry["visual_contract"]["anchor_type"] = "plot"
            entry["native_elements"] = [
                unrelated,
                {
                    "type": "line",
                    "visual_role": "axis",
                    "position": {"left": 10, "top": 10, "width": 1, "height": 10},
                },
                {
                    "type": "line",
                    "visual_role": "axis",
                    "position": {"left": 10, "top": 19, "width": 10, "height": 1},
                },
                {
                    "type": "shape",
                    "visual_role": "data-mark",
                    "value": 1,
                    "position": {"left": 12, "top": 17, "width": 1, "height": 1},
                },
                {
                    "type": "shape",
                    "visual_role": "data-mark",
                    "value": 2,
                    "position": {"left": 17, "top": 13, "width": 1, "height": 1},
                },
            ]
            report = lab_slides.visual_contract_audit(
                self.config,
                {"slides": [entry]},
                frame_map(1),
            )
            self.assertEqual(report["status"], "fail", report)
            self.assertLess(report["checks"][0]["information_area_ratio"], 0.01)
            self.assertLess(report["checks"][0]["figure_bbox_area_ratio"], 0.05)
            self.assertNotIn(
                unrelated["visual_role"],
                report["checks"][0]["figure_roles"],
            )

    def test_rewrite_only_body_slide_cannot_bypass_figure_gate(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "plot"
        entry["native_elements"] = []
        rewrite_only = {
            "outputSlides": [
                {
                    "outputSlide": 1,
                    "editTargets": [{"action": "rewrite", "contentRef": "title_claim"}],
                }
            ]
        }
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            rewrite_only,
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("no bounded figure zone" in error for error in report["errors"]))

    def test_tiny_marks_and_large_text_cannot_fake_dominant_figure(self) -> None:
        entry = slide(1)
        entry["visual_contract"]["anchor_type"] = "plot"
        entry["native_elements"] = [
            {
                "type": "text",
                "text_role": "annotation",
                "text": "Large prose rectangle",
                "position": {"left": 10, "top": 10, "width": 80, "height": 80},
            },
            {
                "type": "shape",
                "visual_role": "data-mark",
                "position": {"left": 1, "top": 1, "width": 1, "height": 1},
            },
            {
                "type": "shape",
                "visual_role": "data-mark",
                "position": {"left": 98, "top": 98, "width": 1, "height": 1},
            },
        ]
        report = lab_slides.visual_contract_audit(
            self.config,
            {"slides": [entry]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("information-bearing area" in error for error in report["errors"]))
        self.assertLess(report["checks"][0]["information_area_ratio"], 0.01)

    def test_visual_contract_cannot_be_removed_or_disabled(self) -> None:
        missing = {"schema_version": 2, "qa": {}}
        report = lab_slides.visual_contract_audit(
            missing,
            {"slides": [slide(1)]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")

        disabled = {
            "schema_version": 2,
            "qa": {
                "visual_contract": {
                    "enabled": False,
                    "disabled_reason": "self-authorized bypass",
                }
            },
        }
        report = lab_slides.visual_contract_audit(
            disabled,
            {"slides": [slide(1)]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("may not be disabled" in error for error in report["errors"]))

    def test_visual_contract_settings_are_pinned(self) -> None:
        weakened = json.loads(json.dumps(self.config))
        weakened["qa"]["visual_contract"]["require_primary_figure"] = False
        weakened["qa"]["visual_contract"]["figure_budget_profiles"]["interaction"][
            "hard_bbox_area_ratio"
        ] = [0, 1]
        weakened["qa"]["visual_contract"]["allowed_anchor_types"].append("rectangle")
        report = lab_slides.visual_contract_audit(
            weakened,
            {"slides": [slide(1)]},
            frame_map(1),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("pinned by the skill" in error for error in report["errors"]))

    def test_user_acceptance_is_sha_pinned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            final = Path(temp_name) / "final.pptx"
            final.write_bytes(b"deck")
            deck_sha = lab_slides.sha256_file(final)
            config = {"qa": {"user_acceptance": {
                "required": True,
                "status": "accepted",
                "reviewer": "lab member",
                "accepted_at": "2026-07-23T12:00:00+09:00",
                "reviewed_deck_sha256": deck_sha,
            }}}
            self.assertEqual(lab_slides.user_acceptance_errors(config, final, deck_sha), [])
            config["qa"]["user_acceptance"]["reviewed_deck_sha256"] = "stale"
            self.assertTrue(any("does not match" in error for error in lab_slides.user_acceptance_errors(config, final, deck_sha)))

    def test_qa_command_blocks_pending_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project = Path(temp_name)
            final = project / "final.pptx"
            final.write_bytes(b"deck")
            config = {
                "schema_version": 2,
                "deck": {"final_pptx": str(final)},
                "style": {"allowed_fonts": []},
                "notes": {"enabled": False},
                "qa": {
                    "expected_slides": 1,
                    "compatibility_probe": False,
                    "require_template_fidelity": False,
                    "require_review_reports": False,
                    "user_acceptance": {"required": True, "status": "pending"},
                },
            }
            config_path = project / "labdeck.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            package = {
                "zip_ok": True,
                "corrupt_member": None,
                "slide_count": 1,
                "fonts": [],
                "empty_placeholder_shapes": 0,
                "visible_text": "",
            }
            inspection = {"slide_count": 1, "notes": [], "notes_sha256": "notes", "source_manifest_sha256": "source"}
            completed = mock.Mock(returncode=0, stdout="", stderr="")
            with mock.patch.object(lab_slides, "audit_config", return_value={"status": "pass", "errors": [], "warnings": [], "slide_plan_entries": 0, "claim_count": 0}), \
                mock.patch.object(lab_slides, "pptx_package_stats", return_value=package), \
                mock.patch.object(lab_slides, "inspect_with_artifact_tool", return_value=inspection), \
                mock.patch.object(lab_slides, "find_presentations_skill", return_value=SKILL_ROOT), \
                mock.patch.object(lab_slides, "find_python", return_value=Path("/usr/bin/python3")), \
                mock.patch.object(lab_slides, "run_command", return_value=completed), \
                mock.patch.object(lab_slides, "render_deck", return_value=(project / "render", project / "montage.png", "render", "source")):
                result = lab_slides.command_qa(argparse.Namespace(config=str(config_path), skip_review_gate=False))
            self.assertEqual(result, 2)
            report = json.loads((project / "reports" / "qa-report.json").read_text(encoding="utf-8"))
            self.assertTrue(any("visual acceptance is pending" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
