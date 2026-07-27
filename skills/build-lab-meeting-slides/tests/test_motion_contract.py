from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "lab_slides.py"
SPEC = importlib.util.spec_from_file_location("lab_slides_motion_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
lab_slides = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab_slides)
REAL_PNG_DECODE_ERROR = lab_slides._png_decode_error


def write_gif(
    path: Path,
    frames: int,
    *,
    duration_hundredths: int = 400,
    loop: bool = True,
) -> None:
    """Write a tiny timed GIF with the requested frame and loop metadata."""
    header = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x12\x33\xff\xff\xff"
    application = (
        b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00"
        if loop
        else b""
    )
    image = (
        b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00"
        b"\x02\x02\x44\x01\x00"
    )
    delay = max(1, round(duration_hundredths / max(1, frames)))
    graphics_control = (
        b"\x21\xf9\x04\x00"
        + int(delay).to_bytes(2, "little")
        + b"\x00\x00"
    )
    path.write_bytes(
        header
        + application
        + b"".join(graphics_control + image for _ in range(frames))
        + b"\x3b"
    )


def write_png_header(path: Path, width: int = 1, height: int = 1) -> None:
    if (width, height) != (1, 1):
        raise ValueError("the test fixture provides one valid 1x1 PNG")
    path.write_bytes(
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
            "AAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
    )


def write_truncated_png_header(path: Path, width: int = 1, height: int = 1) -> None:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + (13).to_bytes(4, "big")
        + b"IHDR"
        + width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
    )


def motion_config() -> dict:
    return {
        "schema_version": 2,
        "sources": [{"id": "source-1"}],
        "qa": {"motion_contract": dict(lab_slides.DEFAULT_MOTION_CONTRACT)},
    }


def motion_asset(
    *,
    asset_id: str = "decode-flow",
    delivery: str = "embedded-gif",
    media_path: str = "assets/decode-flow.gif",
) -> dict:
    return {
        "id": asset_id,
        "engine": "manim",
        "delivery": delivery,
        "domain": "ai-serving",
        "archetype": "request-flow",
        "duration_seconds": 4.0,
        "loop": delivery == "embedded-gif",
        "source_refs": ["source-1"],
        "alt": "Requests enter the active decode batch",
        "static_fallback": "poster",
        "media_path": media_path,
        "poster_path": "assets/decode-flow-poster.png",
        "end_state_path": "assets/decode-flow-end.png",
        "source_path": "work/motion/decode-flow.py",
    }


def motion_slide(number: int, asset: dict, *, bound_path: str | None = None) -> dict:
    delivery = asset["delivery"]
    expected_path = asset["media_path"] if delivery == "embedded-gif" else asset["poster_path"]
    return {
        "slide": number,
        "visual_contract": {"motion_ref": asset["id"]},
        "native_elements": [
            {
                "type": "image",
                "motion_ref": asset["id"],
                "asset_path": bound_path if bound_path is not None else expected_path,
            }
        ],
    }


class MotionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name)
        self.color_patch = mock.patch.object(
            lab_slides,
            "_motion_color_profile",
            return_value=(
                {
                    "sampled_pixels": 100,
                    "off_palette_pixels": 0,
                    "off_palette_ratio": 0.0,
                    "tolerance_rgb": 36,
                },
                None,
            ),
        )
        self.color_patch.start()
        self.png_decode_patch = mock.patch.object(
            lab_slides,
            "_png_decode_error",
            return_value=None,
        )
        self.png_decode_patch.start()
        (self.project / "content").mkdir()
        (self.project / "assets").mkdir()
        (self.project / "work/motion").mkdir(parents=True)
        write_gif(self.project / "assets/decode-flow.gif", frames=2)
        write_png_header(self.project / "assets/decode-flow-poster.png")
        write_png_header(self.project / "assets/decode-flow-end.png")
        (self.project / "work/motion/decode-flow.py").write_text("# source\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.png_decode_patch.stop()
        self.color_patch.stop()
        self.tempdir.cleanup()

    def write_manifest(self, assets: list[dict]) -> None:
        (self.project / "content/motion-assets.json").write_text(
            json.dumps({"schema_version": 1, "assets": assets}), encoding="utf-8"
        )

    def test_empty_manifest_is_not_applicable(self) -> None:
        self.write_manifest([])
        report = lab_slides.motion_contract_audit(motion_config(), {"slides": []}, self.project)
        self.assertEqual(report["status"], "not-applicable", report)
        self.assertEqual(report["errors"], [])

    def test_embedded_gif_with_source_poster_end_state_and_binding_passes(self) -> None:
        asset = motion_asset()
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "pass", report)
        media = report["checks"][0]["media"]
        self.assertEqual(
            {key: media[key] for key in ("width", "height", "frames", "loop_count")},
            {"width": 1, "height": 1, "frames": 2, "loop_count": 0},
        )
        self.assertEqual(report["checks"][0]["actual_duration_seconds"], 4.0)

    def test_single_frame_gif_fails(self) -> None:
        write_gif(self.project / "assets/decode-flow.gif", frames=1)
        asset = motion_asset()
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("at least two frames" in error for error in report["errors"]), report)

    def test_missing_required_fallback_or_source_fails(self) -> None:
        asset = motion_asset()
        asset["poster_path"] = "assets/missing-poster.png"
        asset["source_path"] = "work/motion/missing.py"
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("poster_path does not exist" in error for error in report["errors"]), report)
        self.assertTrue(any("source_path does not exist" in error for error in report["errors"]), report)

    def test_invalid_proof_png_fails(self) -> None:
        (self.project / "assets/decode-flow-poster.png").write_bytes(b"PNG")
        asset = motion_asset()
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("poster_path is not a valid PNG" in error for error in report["errors"]), report)

    def test_truncated_png_header_fails_actual_decode(self) -> None:
        write_truncated_png_header(self.project / "assets/decode-flow-poster.png")
        asset = motion_asset()
        self.write_manifest([asset])
        with mock.patch.object(
            lab_slides,
            "_png_decode_error",
            side_effect=REAL_PNG_DECODE_ERROR,
        ):
            report = lab_slides.motion_contract_audit(
                motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
            )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(
            any("poster_path is not a decodable PNG" in error for error in report["errors"]),
            report,
        )

    def test_gif_without_infinite_loop_extension_fails(self) -> None:
        write_gif(self.project / "assets/decode-flow.gif", frames=2, loop=False)
        asset = motion_asset()
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("infinite loop extension" in error for error in report["errors"]), report)

    def test_off_palette_decoded_pixels_fail(self) -> None:
        asset = motion_asset()
        self.write_manifest([asset])
        with mock.patch.object(
            lab_slides,
            "_motion_color_profile",
            return_value=(
                {
                    "sampled_pixels": 100,
                    "off_palette_pixels": 4,
                    "off_palette_ratio": 0.04,
                    "tolerance_rgb": 36,
                },
                None,
            ),
        ):
            report = lab_slides.motion_contract_audit(
                motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
            )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("off-palette pixels" in error for error in report["errors"]), report)

    def test_actual_duration_outside_contract_fails(self) -> None:
        write_gif(
            self.project / "assets/decode-flow.gif",
            frames=2,
            duration_hundredths=1000,
        )
        asset = motion_asset()
        asset["duration_seconds"] = 4.0
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("actual media duration" in error for error in report["errors"]), report)

    def test_domain_and_archetype_must_be_coherent(self) -> None:
        asset = motion_asset()
        asset["domain"] = "os"
        asset["archetype"] = "prefill-decode"
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("is not valid for domain" in error for error in report["errors"]), report)

    def test_motion_image_must_bind_the_declared_asset(self) -> None:
        asset = motion_asset()
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(),
            {"slides": [motion_slide(1, asset, bound_path="assets/decode-flow-poster.png")]},
            self.project,
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("must use media_path" in error for error in report["errors"]), report)

    def test_motion_source_ref_must_be_a_configured_source(self) -> None:
        asset = motion_asset()
        asset["source_refs"] = ["self-declared"]
        self.write_manifest([asset])
        plan = {
            "slides": [
                {
                    **motion_slide(1, asset),
                    "evidence_refs": ["self-declared"],
                }
            ]
        }
        report = lab_slides.motion_contract_audit(motion_config(), plan, self.project)
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("unknown IDs: self-declared" in error for error in report["errors"]), report)

    def test_motion_source_ref_may_not_be_blank(self) -> None:
        asset = motion_asset()
        asset["source_refs"] = [""]
        self.write_manifest([asset])
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("may not contain blank IDs" in error for error in report["errors"]), report)

    def test_render_cli_rejects_path_like_asset_id_before_rendering(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_ROOT / "scripts/motion_assets.py"),
                "render-manim",
                "--project",
                str(self.project),
                "--source",
                "work/motion/decode-flow.py",
                "--scene",
                "DecodeFlow",
                "--asset-id",
                "../../escape",
                "--domain",
                "ai-serving",
                "--archetype",
                "request-flow",
                "--source-ref",
                "source-1",
                "--alt",
                "Requests enter the active batch",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2, result)
        self.assertIn("--asset-id is not a safe identifier", result.stdout)

    def test_deck_motion_ratio_blocks_overuse(self) -> None:
        asset = motion_asset()
        self.write_manifest([asset])
        slides = [motion_slide(1, asset), motion_slide(2, asset)]
        slides.extend({"slide": number, "native_elements": []} for number in range(3, 6))
        report = lab_slides.motion_contract_audit(
            motion_config(), {"slides": slides}, self.project
        )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("above the 25% deck limit" in error for error in report["errors"]), report)

    def test_companion_mp4_requires_h264_and_aac(self) -> None:
        (self.project / "assets/decode-flow.mp4").write_bytes(b"not-real-media")
        asset = motion_asset(delivery="companion-mp4", media_path="assets/decode-flow.mp4")
        self.write_manifest([asset])
        bad_streams = [
            {"codec_type": "video", "codec_name": "hevc"},
            {"codec_type": "audio", "codec_name": "opus"},
        ]
        with mock.patch.object(lab_slides, "_ffprobe_video", return_value=(bad_streams, None)):
            report = lab_slides.motion_contract_audit(
                motion_config(), {"slides": [motion_slide(1, asset)]}, self.project
            )
        self.assertEqual(report["status"], "fail", report)
        self.assertTrue(any("must use H.264" in error for error in report["errors"]), report)
        self.assertTrue(any("audio must be AAC" in error for error in report["errors"]), report)


if __name__ == "__main__":
    unittest.main()
