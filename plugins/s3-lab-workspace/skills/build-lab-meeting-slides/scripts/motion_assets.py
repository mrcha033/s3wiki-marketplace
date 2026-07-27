#!/usr/bin/env python3
"""Render and validate restrained Manim assets for lab-meeting decks."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import lab_slides


MANIM_VERSION = str(lab_slides.DEFAULT_MOTION_CONTRACT["manim_version"])
ASSET_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
SCENE_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}\Z")


def project_path(project: Path, value: str, label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (project / candidate).resolve()
    try:
        resolved.relative_to(project.resolve())
    except ValueError as error:
        raise lab_slides.LabDeckError(f"{label} escapes the deck project: {value}") from error
    return resolved


def require_identifier(value: str, pattern: re.Pattern[str], label: str) -> str:
    normalized = str(value).strip()
    if not pattern.fullmatch(normalized):
        raise lab_slides.LabDeckError(f"{label} is not a safe identifier: {value!r}")
    return normalized


def run_checked(
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise lab_slides.LabDeckError(
            "motion command failed:\n"
            + " ".join(command)
            + "\n"
            + (result.stderr or result.stdout or "no diagnostic output").strip()
        )


def command_doctor(_: argparse.Namespace) -> int:
    tools = {
        "uvx": shutil.which("uvx"),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "graphviz_dot": shutil.which("dot"),
        "direct_manim": shutil.which("manim"),
    }
    direct_manim_ok = False
    if tools["direct_manim"]:
        try:
            direct_manim_ok = subprocess.run(
                [str(tools["direct_manim"]), "--version"],
                text=True,
                capture_output=True,
                timeout=8,
                check=False,
            ).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            direct_manim_ok = False
    required = {"uvx": bool(tools["uvx"]), "ffmpeg": bool(tools["ffmpeg"])}
    report = {
        "status": "ok" if all(required.values()) else "missing-core-tools",
        "pinned_manim": f"manim=={MANIM_VERSION}",
        "render_command": f"uvx --from manim=={MANIM_VERSION} manim",
        "tools": tools,
        "required": required,
        "direct_manim_runtime_ok": direct_manim_ok,
        "note": (
            "The isolated uvx runtime is authoritative. A broken global Manim "
            "installation is reported but does not block rendering."
        ),
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ok" else 2


def command_validate(args: argparse.Namespace) -> int:
    config_path = Path(args.config).expanduser().resolve()
    config, _, project = lab_slides.load_config(config_path)
    plan_path = project / "content/slide-plan.json"
    if not plan_path.is_file():
        raise lab_slides.LabDeckError(f"slide plan is missing: {plan_path}")
    report = lab_slides.motion_contract_audit(config, lab_slides.read_json(plan_path), project)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in {"pass", "not-applicable"} else 2


def manim_command(
    uvx: str,
    source: Path,
    scene: str,
    media_dir: Path,
    output_name: str,
    output_format: str,
    quality: str,
) -> list[str]:
    quality_flags = {"low": "-ql", "medium": "-qm", "high": "-qh"}
    return [
        uvx,
        "--from",
        f"manim=={MANIM_VERSION}",
        "manim",
        quality_flags[quality],
        "--disable_caching",
        "--format",
        output_format,
        "--media_dir",
        str(media_dir),
        "--output_file",
        output_name,
        str(source),
        scene,
    ]


def render_once(
    project: Path,
    source: Path,
    scene: str,
    output_name: str,
    output_format: str,
    quality: str,
    palette: dict[str, str],
) -> Path:
    uvx = shutil.which("uvx")
    if not uvx:
        raise lab_slides.LabDeckError("uvx is required for the pinned Manim runtime")
    with tempfile.TemporaryDirectory(prefix="labdeck-manim-") as temp_name:
        media_dir = Path(temp_name)
        render_env = dict(os.environ)
        render_env.update(
            {
                f"LABDECK_{token.upper()}": color
                for token, color in palette.items()
            }
        )
        run_checked(
            manim_command(
                uvx,
                source,
                scene,
                media_dir,
                output_name,
                output_format,
                quality,
            ),
            project,
            render_env,
        )
        matches = sorted(
            media_dir.rglob(f"{output_name}.{output_format}"),
            key=lambda item: item.stat().st_mtime_ns,
        )
        if not matches:
            raise lab_slides.LabDeckError(
                f"Manim did not emit {output_name}.{output_format}"
            )
        staged = project / "work/motion" / f"{output_name}-{quality}.{output_format}"
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(matches[-1], staged)
        return staged


def convert_mp4_to_gif(source: Path, output: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise lab_slides.LabDeckError("ffmpeg is required to encode embedded GIF assets")
    with tempfile.TemporaryDirectory(prefix="labdeck-gif-palette-") as temp_name:
        palette_path = Path(temp_name) / "palette.png"
        run_checked(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-vf",
                (
                    "fps=15,scale=854:-2:flags=lanczos,"
                    "palettegen=max_colors=64:reserve_transparent=0:stats_mode=full"
                ),
                "-frames:v",
                "1",
                str(palette_path),
            ],
            source.parent,
        )
        run_checked(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-i",
                str(palette_path),
                "-lavfi",
                (
                    "fps=15,scale=854:-2:flags=lanczos[scaled];"
                    "[scaled][1:v]paletteuse=dither=none"
                ),
                "-loop",
                "0",
                str(output),
            ],
            source.parent,
        )


def extract_gif_frames(media: Path, poster: Path, end_state: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise lab_slides.LabDeckError("ffmpeg is required to extract motion proof frames")
    _, _, frames = lab_slides.gif_dimensions_and_frames(media)
    run_checked(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(media),
            "-vf",
            "select=eq(n\\,0)",
            "-frames:v",
            "1",
            str(poster),
        ],
        media.parent,
    )
    run_checked(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(media),
            "-vf",
            f"select=eq(n\\,{frames - 1})",
            "-frames:v",
            "1",
            str(end_state),
        ],
        media.parent,
    )


def extract_mp4_frames(
    media: Path,
    poster: Path,
    end_state: Path,
    target_width: int | None = None,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise lab_slides.LabDeckError("ffmpeg is required to extract motion proof frames")
    first_frame_command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            "0",
            "-i",
            str(media),
        ]
    if target_width is not None:
        first_frame_command.extend(
            ["-vf", f"scale={target_width}:-2:flags=lanczos"]
        )
    first_frame_command.extend(
        [
            "-frames:v",
            "1",
            str(poster),
        ]
    )
    run_checked(first_frame_command, media.parent)
    final_frame_command = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-sseof",
            "-0.1",
            "-i",
            str(media),
        ]
    if target_width is not None:
        final_frame_command.extend(
            ["-vf", f"scale={target_width}:-2:flags=lanczos"]
        )
    final_frame_command.extend(
        [
            "-frames:v",
            "1",
            str(end_state),
        ]
    )
    run_checked(final_frame_command, media.parent)


def command_render_manim(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise lab_slides.LabDeckError(f"project directory is missing: {project}")
    asset_id = require_identifier(args.asset_id, ASSET_ID_RE, "--asset-id")
    scene = require_identifier(args.scene, SCENE_NAME_RE, "--scene")
    duration = float(args.duration_seconds)
    if not math.isfinite(duration) or not 3 <= duration <= 8:
        raise lab_slides.LabDeckError("--duration-seconds must be between 3 and 8")
    alt = str(args.alt).strip()
    if not alt or lab_slides.english_copy_issues(alt):
        raise lab_slides.LabDeckError("--alt must be concise English alternative text")
    source_refs = [str(value).strip() for value in args.source_ref]
    if any(not value for value in source_refs):
        raise lab_slides.LabDeckError("--source-ref values must be nonempty")
    config_path = project / "labdeck.json"
    if not config_path.is_file():
        raise lab_slides.LabDeckError("the motion project must contain labdeck.json")
    config, _, _ = lab_slides.load_config(config_path)
    configured_source_ids = {
        str(item.get("id", "")).strip()
        for item in config.get("sources", [])
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    unknown_source_refs = sorted(set(source_refs) - configured_source_ids)
    if unknown_source_refs:
        raise lab_slides.LabDeckError(
            "--source-ref contains IDs absent from labdeck.json: "
            + ", ".join(unknown_source_refs)
        )
    allowed_domain_archetypes = {
        str(value)
        for value in lab_slides.DEFAULT_MOTION_CONTRACT["domain_archetypes"].get(
            args.domain,
            [],
        )
    }
    if args.archetype not in allowed_domain_archetypes:
        raise lab_slides.LabDeckError(
            f"--archetype {args.archetype!r} is not valid for --domain {args.domain!r}"
        )
    trusted_palette = None
    if lab_slides.template_mode(config):
        template = lab_slides.template_paths(config, project)["pptx"]
        if not template.is_file():
            raise lab_slides.LabDeckError(f"template PPTX is missing: {template}")
        trusted_palette = lab_slides.active_palette_for_template(template)
    palette_errors = lab_slides.active_palette_contract_errors(config, trusted_palette)
    if palette_errors:
        raise lab_slides.LabDeckError(
            "motion palette contract failed:\n" + "\n".join(palette_errors)
        )
    palette = lab_slides.configured_active_palette(config)
    source = project_path(project, args.source, "--source")
    if not source.is_file() or source.suffix.casefold() != ".py":
        raise lab_slides.LabDeckError("--source must be an existing project-local Python file")
    render_format = "mp4"
    output_format = "gif" if args.delivery == "embedded-gif" else "mp4"
    output_dir = project / "assets/motion"
    output_dir.mkdir(parents=True, exist_ok=True)

    smoke = render_once(
        project,
        source,
        scene,
        f"{asset_id}-smoke",
        render_format,
        "low",
        palette,
    )
    candidate = (
        smoke
        if args.quality == "low"
        else render_once(
            project,
            source,
            scene,
            asset_id,
            render_format,
            args.quality,
            palette,
        )
    )
    media = output_dir / f"{asset_id}.{output_format}"
    if output_format == "gif":
        convert_mp4_to_gif(candidate, media)
    else:
        shutil.copy2(candidate, media)
    poster = output_dir / f"{asset_id}-start.png"
    end_state = output_dir / f"{asset_id}-end.png"
    if output_format == "gif":
        extract_mp4_frames(candidate, poster, end_state, target_width=854)
        metadata = lab_slides.gif_metadata(media)
        actual_duration = float(metadata["duration_seconds"])
        if metadata["loop_count"] != 0:
            raise lab_slides.LabDeckError("encoded GIF is missing its infinite loop extension")
    else:
        extract_mp4_frames(media, poster, end_state)
        actual_duration, duration_error = lab_slides._ffprobe_duration(media)
        if duration_error or actual_duration is None:
            raise lab_slides.LabDeckError(duration_error or "media duration is unavailable")
    if not 3 <= actual_duration <= 8:
        raise lab_slides.LabDeckError(
            f"actual rendered duration {actual_duration:.3f}s is outside 3-8s"
        )
    duration_tolerance = max(0.25, actual_duration * 0.10)
    if abs(duration - actual_duration) > duration_tolerance:
        raise lab_slides.LabDeckError(
            f"--duration-seconds {duration:.3f}s differs from actual render "
            f"{actual_duration:.3f}s"
        )
    if output_format == "gif":
        size_limit = int(lab_slides.DEFAULT_MOTION_CONTRACT["max_embedded_gif_bytes"])
    else:
        size_limit = int(lab_slides.DEFAULT_MOTION_CONTRACT["max_companion_mp4_bytes"])
    if media.stat().st_size > size_limit:
        raise lab_slides.LabDeckError(
            f"rendered {output_format.upper()} exceeds {size_limit} bytes"
        )
    color_profile, color_error = lab_slides._motion_color_profile(media, palette)
    if color_error:
        raise lab_slides.LabDeckError(color_error)
    if float(color_profile["off_palette_ratio"]) > 0.005:
        raise lab_slides.LabDeckError(
            f"rendered motion has {float(color_profile['off_palette_ratio']):.2%} "
            "off-palette pixels"
        )

    result = {
        "status": "rendered",
        "smoke_render": str(smoke.relative_to(project)),
        "media_path": str(media.relative_to(project)),
        "poster_path": str(poster.relative_to(project)),
        "end_state_path": str(end_state.relative_to(project)),
        "actual_duration_seconds": round(actual_duration, 3),
        "palette_profile": color_profile,
        "manifest_entry": {
            "id": asset_id,
            "engine": "manim",
            "delivery": args.delivery,
            "domain": args.domain,
            "archetype": args.archetype,
            "media_path": str(media.relative_to(project)),
            "poster_path": str(poster.relative_to(project)),
            "end_state_path": str(end_state.relative_to(project)),
            "source_path": str(source.relative_to(project)),
            "source_refs": source_refs,
            "duration_seconds": round(actual_duration, 3),
            "loop": args.delivery == "embedded-gif",
            "static_fallback": args.static_fallback,
            "alt": alt,
        },
    }
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="check the isolated motion runtime")
    doctor.set_defaults(func=command_doctor)

    validate = subparsers.add_parser("validate", help="validate a deck motion manifest")
    validate.add_argument("--config", required=True)
    validate.set_defaults(func=command_validate)

    render = subparsers.add_parser(
        "render-manim",
        help="run a low-quality smoke render, then emit GIF/MP4 and proof frames",
    )
    render.add_argument("--project", required=True)
    render.add_argument("--source", required=True)
    render.add_argument("--scene", required=True)
    render.add_argument("--asset-id", required=True)
    render.add_argument(
        "--delivery",
        choices=("embedded-gif", "companion-mp4"),
        default="embedded-gif",
    )
    render.add_argument("--quality", choices=("low", "medium", "high"), default="medium")
    render.add_argument("--domain", choices=("systems", "os", "ai-serving"), required=True)
    render.add_argument(
        "--archetype",
        choices=tuple(lab_slides.DEFAULT_MOTION_CONTRACT["allowed_archetypes"]),
        required=True,
    )
    render.add_argument("--source-ref", action="append", required=True)
    render.add_argument("--duration-seconds", type=float, default=5.0)
    render.add_argument(
        "--static-fallback",
        choices=("poster", "progressive-native"),
        default="poster",
    )
    render.add_argument("--alt", required=True)
    render.set_defaults(func=command_render_manim)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except lab_slides.LabDeckError as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
