#!/usr/bin/env python3
"""Render a small Manim scene and inspect the resulting media."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
MANIM_VERSION = "0.20.1"
PRESETS = {
    "serving": (SKILL_DIR / "assets/manim/ai_serving_interaction.py", "ServingBatchFlow"),
    "syscall": (SKILL_DIR / "assets/manim/system_os_interaction.py", "SyscallPath"),
}
DEFAULT_PALETTE = {
    "background": "#FFFFFF",
    "surface": "#FFFFFF",
    "ink": "#001233",
    "muted": "#5C677D",
    "primary": "#0353A4",
    "focus": "#2269FE",
    "soft": "#D2E1FE",
}
SAFE_STEM = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
SAFE_SCENE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}\Z")


class MotionError(RuntimeError):
    pass


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout or "no diagnostic output").strip()
        raise MotionError(f"command failed: {' '.join(command)}\n{detail}")
    return result


def project_output(project: Path, value: str) -> Path:
    output = Path(value)
    if not output.is_absolute():
        output = project / output
    output = output.expanduser().resolve()
    try:
        output.relative_to(project)
    except ValueError as error:
        raise MotionError(f"output must stay inside the project: {output}") from error
    return output


def load_palette(path: Path | None) -> dict[str, str]:
    palette = dict(DEFAULT_PALETTE)
    if path is None:
        return palette
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MotionError(f"could not read palette file {path}: {error}") from error
    colors = document.get("colors", document)
    if not isinstance(colors, dict):
        raise MotionError("palette file must contain a colors object")
    aliases = {
        "background": ("background", "white"),
        "surface": ("surface", "white"),
        "ink": ("ink", "navy"),
        "muted": ("muted",),
        "primary": ("primary", "blue"),
        "focus": ("focus", "royal"),
        "soft": ("soft", "pale_blue"),
    }
    for target, candidates in aliases.items():
        value = next((colors.get(name) for name in candidates if colors.get(name)), None)
        if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            palette[target] = value.upper()
    return palette


def media_info(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size == 0:
        raise MotionError(f"media file is missing or empty: {path}")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"path": str(path), "bytes": path.stat().st_size, "duration_seconds": None}
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=width,height",
            "-of",
            "json",
            str(path),
        ],
        cwd=path.parent,
    )
    data = json.loads(result.stdout)
    streams = data.get("streams") or [{}]
    duration = data.get("format", {}).get("duration")
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "duration_seconds": round(float(duration), 3) if duration is not None else None,
        "width": streams[0].get("width"),
        "height": streams[0].get("height"),
    }


def command_doctor(_: argparse.Namespace) -> int:
    tools = {name: shutil.which(name) for name in ("uvx", "ffmpeg", "ffprobe")}
    report = {
        "status": "ok" if tools["uvx"] and tools["ffmpeg"] else "missing-tools",
        "manim": f"manim=={MANIM_VERSION}",
        "tools": tools,
        "presets": sorted(PRESETS),
    }
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "ok" else 2


def command_inspect(args: argparse.Namespace) -> int:
    print(json.dumps(media_info(Path(args.media).expanduser().resolve()), indent=2))
    return 0


def resolve_scene(args: argparse.Namespace) -> tuple[Path, str]:
    if args.preset:
        return PRESETS[args.preset]
    if not args.source or not args.scene:
        raise MotionError("use --preset or provide both --source and --scene")
    source = Path(args.source).expanduser().resolve()
    scene = str(args.scene).strip()
    if not source.is_file() or source.suffix.lower() != ".py":
        raise MotionError(f"Manim source must be an existing Python file: {source}")
    if not SAFE_SCENE.fullmatch(scene):
        raise MotionError(f"invalid scene name: {scene!r}")
    return source, scene


def convert_to_gif(source: Path, output: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MotionError("ffmpeg is required for GIF output")
    with tempfile.TemporaryDirectory(prefix="labdeck-gif-") as temporary:
        palette = Path(temporary) / "palette.png"
        run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-vf",
                "fps=15,scale=854:-2:flags=lanczos,palettegen=max_colors=96",
                str(palette),
            ],
            cwd=source.parent,
        )
        run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-i",
                str(palette),
                "-lavfi",
                "fps=15,scale=854:-2:flags=lanczos[x];[x][1:v]paletteuse=dither=none",
                "-loop",
                "0",
                str(output),
            ],
            cwd=source.parent,
        )


def extract_poster(media: Path, poster: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MotionError("ffmpeg is required to create the poster frame")
    run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(media),
            "-frames:v",
            "1",
            str(poster),
        ],
        cwd=media.parent,
    )


def command_render(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise MotionError(f"project directory does not exist: {project}")
    source, scene = resolve_scene(args)
    output = project_output(project, args.output)
    if output.suffix.lower() not in {".gif", ".mp4"}:
        raise MotionError("--output must end in .gif or .mp4")
    if not SAFE_STEM.fullmatch(output.stem):
        raise MotionError(f"output filename is not safe: {output.name!r}")
    uvx = shutil.which("uvx")
    if not uvx:
        raise MotionError("uvx is required to run the isolated Manim environment")
    palette_path = Path(args.palette).expanduser().resolve() if args.palette else None
    palette = load_palette(palette_path)
    render_env = dict(os.environ)
    render_env.update({f"LABDECK_{name.upper()}": value for name, value in palette.items()})
    quality = {"low": "-ql", "medium": "-qm", "high": "-qh"}[args.quality]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="labdeck-manim-") as temporary:
        media_dir = Path(temporary)
        run(
            [
                uvx,
                "--from",
                f"manim=={MANIM_VERSION}",
                "manim",
                quality,
                "--disable_caching",
                "--format",
                "mp4",
                "--media_dir",
                str(media_dir),
                "--output_file",
                output.stem,
                str(source),
                scene,
            ],
            cwd=project,
            env=render_env,
        )
        matches = sorted(media_dir.rglob(f"{output.stem}.mp4"))
        if not matches:
            raise MotionError("Manim completed without producing the requested video")
        if output.suffix.lower() == ".gif":
            convert_to_gif(matches[-1], output)
        else:
            shutil.copy2(matches[-1], output)
    poster = output.with_name(f"{output.stem}-poster.png")
    extract_poster(output, poster)
    result = {
        "status": "rendered",
        "media": media_info(output),
        "poster": str(poster),
        "source": str(source),
        "scene": scene,
        "palette": palette,
    }
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="show the available media tools")
    doctor.set_defaults(func=command_doctor)

    inspect = subparsers.add_parser("inspect", help="read basic media metadata")
    inspect.add_argument("media")
    inspect.set_defaults(func=command_inspect)

    render = subparsers.add_parser("render", help="render one preset or custom Manim scene")
    render.add_argument("--project", required=True)
    render.add_argument("--preset", choices=tuple(PRESETS))
    render.add_argument("--source")
    render.add_argument("--scene")
    render.add_argument("--output", required=True)
    render.add_argument("--quality", choices=("low", "medium", "high"), default="medium")
    render.add_argument("--palette", help="optional JSON palette or style manifest")
    render.set_defaults(func=command_render)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (MotionError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
