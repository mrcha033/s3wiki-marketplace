#!/usr/bin/env python3
"""Validate the unified private Codex and Claude marketplace package."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "s3-lab-workspace"
SLIDE_SKILL = "build-lab-meeting-slides"
MCP_NAME = "s3-research-memory"
MCP_URL = "https://s3wiki.yonsei.ac.kr/mcp"
LEGACY_PLUGINS = ("build-lab-meeting-slides", "s3-research-memory")
PERSONAL_APP_IDENTIFIERS = (
    "dev-6a58e7a411988191a74fda9cfcf6b604",
    "asdk_app_6a58e7a411988191a74fda9cfcf6b604",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def main() -> None:
    codex_marketplace_path = ROOT / ".agents/plugins/marketplace.json"
    claude_marketplace_path = ROOT / ".claude-plugin/marketplace.json"
    codex_marketplace = load_json(codex_marketplace_path)
    claude_marketplace = load_json(claude_marketplace_path)

    assert [entry["name"] for entry in codex_marketplace["plugins"]] == [PLUGIN]
    assert [entry["name"] for entry in claude_marketplace["plugins"]] == [PLUGIN]
    codex_entry = codex_marketplace["plugins"][0]
    claude_entry = claude_marketplace["plugins"][0]
    assert codex_entry["source"]["path"] == f"./plugins/{PLUGIN}"
    assert codex_entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_USE",
    }
    assert codex_entry["category"] == "Productivity"
    assert claude_entry["source"] == f"./plugins/{PLUGIN}"
    assert claude_entry["version"] == "0.2.0"

    plugin = ROOT / "plugins" / PLUGIN
    codex_manifest_path = plugin / ".codex-plugin/plugin.json"
    claude_manifest_path = plugin / ".claude-plugin/plugin.json"
    mcp_path = plugin / ".mcp.json"
    codex_manifest = load_json(codex_manifest_path)
    claude_manifest = load_json(claude_manifest_path)
    mcp = load_json(mcp_path)

    assert codex_manifest["name"] == PLUGIN
    assert codex_manifest["version"] == claude_manifest["version"] == "0.2.0"
    assert codex_manifest["skills"] == "./skills/"
    assert codex_manifest["mcpServers"] == "./.mcp.json"
    assert "apps" not in codex_manifest
    assert claude_manifest["name"] == PLUGIN
    assert claude_manifest["skills"] == "./skills/"
    assert "mcpServers" not in claude_manifest

    assert set(mcp) == {"mcpServers"}
    assert set(mcp["mcpServers"]) == {MCP_NAME}
    server = mcp["mcpServers"][MCP_NAME]
    assert server == {"type": "http", "url": MCP_URL}
    assert "headers" not in server and "env" not in server

    source = ROOT / "skills" / SLIDE_SKILL
    packaged = plugin / "skills" / SLIDE_SKILL
    assert source.is_dir() and packaged.is_dir()
    assert not packaged.is_symlink()
    assert files(source) == files(packaged)
    for relative in files(source):
        assert (source / relative).read_bytes() == (packaged / relative).read_bytes(), relative

    interface = codex_manifest["interface"]
    for asset in (
        interface["composerIcon"],
        interface["logo"],
        *interface["screenshots"],
    ):
        assert (plugin / asset).is_file(), asset

    active_documents = (
        codex_marketplace_path,
        claude_marketplace_path,
        codex_manifest_path,
        claude_manifest_path,
        mcp_path,
    )
    active_text = "\n".join(path.read_text(encoding="utf-8") for path in active_documents)
    assert all(identifier not in active_text for identifier in PERSONAL_APP_IDENTIFIERS)
    for legacy in LEGACY_PLUGINS:
        assert not (ROOT / "plugins" / legacy).exists()

    for installer in (ROOT / "scripts/install.sh", ROOT / "scripts/install.ps1"):
        text = installer.read_text(encoding="utf-8")
        assert PLUGIN in text and "S3RM_MCP_TOKEN" not in text

    print("unified private marketplace packaging: PASS")


if __name__ == "__main__":
    main()
