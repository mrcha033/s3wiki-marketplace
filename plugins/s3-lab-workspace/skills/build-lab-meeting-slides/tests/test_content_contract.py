from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "lab_slides.py"
SPEC = importlib.util.spec_from_file_location("lab_slides_content_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
lab_slides = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab_slides)


def config() -> dict:
    return {
        "schema_version": 2,
        "style": {
            "active_palette": dict(lab_slides.DEFAULT_ACTIVE_PALETTE),
            "active_palette_sha256": lab_slides.active_palette_sha256(
                lab_slides.DEFAULT_ACTIVE_PALETTE
            ),
            "language_exceptions": [],
        },
        "qa": {
            "content_contract": dict(lab_slides.DEFAULT_CONTENT_CONTRACT),
        },
    }


def plan(title: str = "Memory Coalescing", text: str = "Merged transaction") -> dict:
    return {
        "slides": [
            {
                "slide": 1,
                "title_claim": title,
                "template_frame": {"role": "content"},
                "native_elements": [
                    {
                        "type": "text",
                        "text_role": "figure-label",
                        "text": text,
                    }
                ],
            }
        ]
    }


class ContentContractTests(unittest.TestCase):
    def test_english_keyword_title_and_grounded_label_pass(self) -> None:
        report = lab_slides.content_contract_audit(
            config(),
            plan(),
            {"slides": [{"slide": 1, "text": "Explain the merged memory transaction and its measured consequence."}]},
        )
        self.assertEqual(report["status"], "pass", report)

    def test_sentence_title_is_rejected(self) -> None:
        report = lab_slides.content_contract_audit(
            config(),
            plan("Coalesced access removes redundant memory transactions"),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("keyword phrase" in error for error in report["errors"]))

        report = lab_slides.content_contract_audit(config(), plan("This is faster"))
        self.assertTrue(any("reads as a clause" in error for error in report["errors"]))

        for title in (
            "Coalescing Reduces Memory Traffic",
            "Cache Misses Dominate Runtime",
            "Warp Divergence Cuts Throughput",
            "Latency Hides Costs",
            "Fusion Saves Memory",
            "Caches Absorb Reads",
            "Threads Share Lines",
            "Latency Hides",
            "Threads Share",
            "Fusion Saves",
            "Costs Rise",
            "Memory Costs Rise",
            "Results Show",
            "Evidence Shows",
            "Data Reveal",
            "People Share",
            "Traffic Changes",
            "Caches Block",
            "Experiments Demonstrate",
            "Measurements Confirm",
            "Results Suggest",
            "Data Validate",
            "Results Indicate",
            "Benchmarks Confirm",
            "Results Demonstrate Gains",
            "Experiment Failed",
            "Experiments Ran",
            "Fish Reveal",
            "Sheep Show",
            "Deer Show",
            "Aircraft Show",
            "Offspring Show",
            "Alumni Show",
            "Nuclei Show",
            "Stimuli Show",
            "Fungi Show",
            "Bacteria Show",
            "Media Show",
        ):
            report = lab_slides.content_contract_audit(config(), plan(title))
            self.assertTrue(
                any(
                    "declarative sentence" in error or "finite verb" in error
                    for error in report["errors"]
                ),
                report,
            )

    def test_ambiguous_nouns_remain_valid_keyword_titles(self) -> None:
        for title in (
            "Transaction Merge",
            "Cache Miss",
            "Flow Control",
            "Model Fit",
            "Data Processing",
            "Cache Control Logic",
            "Ablation Effects",
            "Next Experiments",
            "Performance Results",
            "Cache Misses",
            "Memory Costs",
            "Experiment Results",
        ):
            report = lab_slides.content_contract_audit(config(), plan(title))
            self.assertEqual(report["status"], "pass", report)

    def test_content_contract_settings_are_pinned(self) -> None:
        weakened = config()
        weakened["qa"]["content_contract"]["title_max_words"] = 8
        report = lab_slides.content_contract_audit(
            weakened,
            plan("Memory Bandwidth Optimization Strategy"),
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("pinned by the skill" in error for error in report["errors"]))

    def test_non_english_generated_copy_and_notes_are_rejected(self) -> None:
        report = lab_slides.content_contract_audit(
            config(),
            plan("메모리 병합", "병합된 트랜잭션"),
            {"slides": [{"slide": 1, "text": "이 설명은 허용되지 않는다."}]},
        )
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("title must use English" in error for error in report["errors"]))
        self.assertTrue(any("speaker notes must use English" in error for error in report["errors"]))

    def test_latin_script_non_english_copy_is_rejected(self) -> None:
        for title, label, note_text in (
            ("Resultados Clave", "Latencia reducida", "Esta explicacion muestra el cambio."),
            ("Tiempo Bajo", "Matriz Dispersa", "Calculo rapido para cada etapa."),
            ("Acceso Unificado", "Memoria compartida", "Comparacion antes y despues."),
        ):
            report = lab_slides.content_contract_audit(
                config(),
                plan(title, label),
                {"slides": [{"slide": 1, "text": note_text}]},
            )
            self.assertEqual(report["status"], "fail", report)
            self.assertTrue(any("must use English" in error for error in report["errors"]))

    def test_uppercase_non_english_copy_is_rejected(self) -> None:
        report = lab_slides.content_contract_audit(
            config(),
            plan("TIEMPO BAJO", "MATRIZ DISPERSA"),
            {"slides": [{"slide": 1, "text": "CALCULO RAPIDO"}]},
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("title must use English" in error for error in report["errors"]))
        self.assertTrue(any("must use English visible copy" in error for error in report["errors"]))
        self.assertTrue(any("speaker notes must use English" in error for error in report["errors"]))

    def test_known_research_acronyms_remain_valid(self) -> None:
        report = lab_slides.content_contract_audit(
            config(),
            plan("CUDA Memory", "GPU HBM Bandwidth"),
            {"slides": [{"slide": 1, "text": "Compare GPU and HBM bandwidth."}]},
        )
        self.assertEqual(report["status"], "pass", report)

    def test_source_code_and_equation_literals_are_scoped_exceptions(self) -> None:
        entry = plan()["slides"][0]
        entry["native_elements"] = [
            {"type": "text", "text_role": "source", "text": "Résultats Clave"},
            {"type": "text", "text_role": "code", "text": "matriz_disperse()"},
            {"type": "text", "text_role": "equation", "text": "λ = α + β"},
        ]
        report = lab_slides.content_contract_audit(config(), {"slides": [entry]})
        self.assertEqual(report["status"], "pass", report)
        exceptions = lab_slides.planned_language_exceptions({"slides": [entry]})
        package = {"text_runs": ["Memory Coalescing", "Résultats Clave", "λ = α + β"]}
        self.assertEqual(
            lab_slides.final_visible_copy_errors(config(), package, exceptions),
            [],
        )

    def test_filler_missing_role_and_excess_copy_are_rejected(self) -> None:
        entry = plan()["slides"][0]
        entry["native_elements"] = [
            {
                "type": "text",
                "text": "TODO " + "word " * 50,
            }
        ]
        report = lab_slides.content_contract_audit(config(), {"slides": [entry]})
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("text_role" in error for error in report["errors"]))
        self.assertTrue(any("filler or placeholder" in error for error in report["errors"]))
        self.assertTrue(any("visible body words" in error for error in report["errors"]))

    def test_inherited_filler_fields_and_visible_copy_count_are_rejected(self) -> None:
        entry = plan()["slides"][0]
        entry["content"] = {
            "subtitle": "A decorative sentence that should never appear.",
            "body": "word " * 46,
        }
        report = lab_slides.content_contract_audit(config(), {"slides": [entry]})
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("forbidden filler field" in error for error in report["errors"]))
        self.assertTrue(any("visible body words" in error for error in report["errors"]))

    def test_arbitrary_content_fields_cannot_bypass_text_roles(self) -> None:
        for field in ("body", "footer", "blurb", "title", "decktitle"):
            entry = plan()["slides"][0]
            entry["content"] = {field: "This slide shows the key result"}
            report = lab_slides.content_contract_audit(config(), {"slides": [entry]})
            self.assertEqual(report["status"], "fail", report)
            self.assertTrue(
                any("undeclared visible-copy field" in error for error in report["errors"]),
                report,
            )

    def test_arbitrary_top_level_copy_fields_are_rejected(self) -> None:
        for field in ("headline", "title", "deck_title", "body"):
            entry = plan()["slides"][0]
            entry[field] = "This result improves performance"
            report = lab_slides.content_contract_audit(config(), {"slides": [entry]})
            self.assertEqual(report["status"], "fail", report)
            self.assertTrue(
                any("not reachable visible copy" in error for error in report["errors"]),
                report,
            )

    def test_compact_cover_metadata_is_allowed(self) -> None:
        entry = plan()["slides"][0]
        entry["template_frame"]["role"] = "cover"
        entry["content"] = {
            "subtitle": "27 July 2026 · Yunmin Cha",
            "meeting_subject": "Lab Meeting",
        }
        report = lab_slides.content_contract_audit(config(), {"slides": [entry]})
        self.assertEqual(report["status"], "pass", report)

    def test_contract_cannot_be_removed_or_disabled(self) -> None:
        missing = {"schema_version": 2, "qa": {}}
        report = lab_slides.content_contract_audit(missing, plan())
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("required" in error for error in report["errors"]))

        disabled = config()
        disabled["qa"]["content_contract"] = {
            "enabled": False,
            "disabled_reason": "self-authorized bypass",
        }
        report = lab_slides.content_contract_audit(disabled, plan())
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("may not be disabled" in error for error in report["errors"]))

    def test_preserved_speaker_notes_must_be_english(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            project = Path(temp_name)
            notes_path = project / "notes.json"
            notes_path.write_text(
                json.dumps(
                    {
                        "slides": [
                            {
                                "slide": 1,
                                "mode": "preserve",
                                "preserve_rationale": "Retain verified source narration.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            current = {
                "notes": {
                    "enabled": True,
                    "path": "notes.json",
                    "preserve_forbidden_fragments": [],
                }
            }
            with mock.patch.object(
                lab_slides,
                "pptx_notes_text_by_slide",
                return_value={1: "Tiempo bajo y calculo rapido."},
            ):
                errors = lab_slides.validate_notes_contract(
                    current,
                    project,
                    expected_slides=1,
                    inherited_deck=MODULE_PATH,
                )
            self.assertTrue(any("must use English" in error for error in errors))

    def test_final_visible_copy_allows_only_exact_inherited_language_exceptions(self) -> None:
        current = config()
        current["style"]["language_exceptions"] = ["연세", "대학교"]
        package = {"text_runs": ["Memory Coalescing", "연세", "대학교"]}
        self.assertEqual(lab_slides.final_visible_copy_errors(current, package), [])

        package["text_runs"].append("새로운 연세 프로젝트")
        errors = lab_slides.final_visible_copy_errors(current, package)
        self.assertTrue(any("not English" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
