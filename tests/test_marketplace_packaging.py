#!/usr/bin/env python3
"""Validate the private cross-platform marketplace contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLIDE_PLUGIN = "build-lab-meeting-slides"
MEMORY_PLUGIN = "s3-research-memory"
PLUGINS = [SLIDE_PLUGIN, MEMORY_PLUGIN]
APP_KEY = "dev-6a58e7a411988191a74fda9cfcf6b604"
APP_ID = "asdk_app_6a58e7a411988191a74fda9cfcf6b604"
MCP_URL = "https://s3wiki.yonsei.ac.kr/mcp"


def files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> None:
    codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    assert [entry["name"] for entry in codex["plugins"]] == PLUGINS
    assert [entry["name"] for entry in claude["plugins"]] == PLUGINS
    for entry, plugin in zip(codex["plugins"], PLUGINS):
        assert entry["source"]["path"] == f"./plugins/{plugin}"
        assert entry["policy"] == {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        }
        assert entry["category"] == "Productivity"
    for entry, plugin in zip(claude["plugins"], PLUGINS):
        assert entry["source"] == f"./plugins/{plugin}"

    source = ROOT / "skills" / SLIDE_PLUGIN
    packaged = ROOT / "plugins" / SLIDE_PLUGIN / "skills" / SLIDE_PLUGIN
    assert source.is_dir() and packaged.is_dir()
    assert not packaged.is_symlink()
    assert files(source) == files(packaged)
    for relative in files(source):
        assert (source / relative).read_bytes() == (packaged / relative).read_bytes(), relative

    memory = ROOT / "plugins" / MEMORY_PLUGIN
    codex_plugin = json.loads(
        (memory / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    claude_plugin = json.loads(
        (memory / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    app_manifest = json.loads((memory / ".app.json").read_text(encoding="utf-8"))

    assert codex_plugin["name"] == MEMORY_PLUGIN
    assert codex_plugin["apps"] == "./.app.json"
    assert "skills" not in codex_plugin
    assert app_manifest == {"apps": {APP_KEY: {"id": APP_ID}}}

    assert claude_plugin["name"] == MEMORY_PLUGIN
    server = claude_plugin["mcpServers"][MEMORY_PLUGIN]
    assert server["type"] == "http"
    assert server["url"] == MCP_URL
    assert server["headers"]["Authorization"] == "Bearer ${S3RM_MCP_TOKEN}"
    assert not (memory / ".mcp.json").exists()

    print("private marketplace packaging: PASS")


if __name__ == "__main__":
    main()
