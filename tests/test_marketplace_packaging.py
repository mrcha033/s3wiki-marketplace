#!/usr/bin/env python3
"""Validate the private single-plugin marketplace contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "build-lab-meeting-slides"


def files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> None:
    codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    assert [entry["name"] for entry in codex["plugins"]] == [PLUGIN]
    assert [entry["name"] for entry in claude["plugins"]] == [PLUGIN]
    assert codex["plugins"][0]["source"]["path"] == f"./plugins/{PLUGIN}"
    assert claude["plugins"][0]["source"] == f"./plugins/{PLUGIN}"

    source = ROOT / "skills" / PLUGIN
    packaged = ROOT / "plugins" / PLUGIN / "skills" / PLUGIN
    assert source.is_dir() and packaged.is_dir()
    assert not packaged.is_symlink()
    assert files(source) == files(packaged)
    for relative in files(source):
        assert (source / relative).read_bytes() == (packaged / relative).read_bytes(), relative

    print("private marketplace packaging: PASS")


if __name__ == "__main__":
    main()
