#!/usr/bin/env bash
set -Eeuo pipefail

readonly ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

for command_name in codex claude jq; do
  command -v "$command_name" >/dev/null 2>&1 || {
    printf 'missing required command: %s\n' "$command_name" >&2
    exit 1
  }
done

test_root="$(mktemp -d "${TMPDIR:-/tmp}/s3-lab-clean-install.XXXXXX")"
cleanup() {
  case "$test_root" in
    "${TMPDIR:-/tmp}"/s3-lab-clean-install.*)
      find "$test_root" -depth -delete
      ;;
    *)
      printf 'refusing to remove unexpected test path: %s\n' "$test_root" >&2
      ;;
  esac
}
trap cleanup EXIT INT TERM

mkdir -p "$test_root/home" "$test_root/codex" "$test_root/claude"
git clone --quiet --bare "$ROOT" "$test_root/marketplace.git"
git config --file "$test_root/gitconfig" \
  url."file://$test_root/marketplace.git".insteadOf \
  "https://github.com/mrcha033/s3wiki-marketplace.git"
export HOME="$test_root/home"
export CODEX_HOME="$test_root/codex"
export CLAUDE_CONFIG_DIR="$test_root/claude"
export GIT_CONFIG_GLOBAL="$test_root/gitconfig"
export S3_LAB_MARKETPLACE_URL="https://github.com/mrcha033/s3wiki-marketplace.git"

"$ROOT/scripts/install.sh" --all
"$ROOT/scripts/install.sh" --all

codex_plugins="$(codex plugin list --json)"
claude_plugins="$(claude plugin list --json)"
codex_mcp="$(codex mcp list --json)"

jq -e '
  [.installed[] | select(
    .pluginId == "s3-lab-workspace@s3wiki-marketplace"
    and .version == "0.4.0"
    and .enabled == true
  )] | length == 1
' <<<"$codex_plugins" >/dev/null

jq -e '
  [.[] | select(
    .id == "s3-lab-workspace@s3wiki-marketplace"
    and .version == "0.4.0"
    and .enabled == true
    and .mcpServers."s3-research-memory".url
      == "https://s3wiki.yonsei.ac.kr/mcp"
  )] | length == 1
' <<<"$claude_plugins" >/dev/null

jq -e '
  [.[] | select(
    .name == "s3-research-memory"
    and .enabled == true
    and .transport.url == "https://s3wiki.yonsei.ac.kr/mcp"
    and .transport.bearer_token_env_var == null
    and .auth_status == "not_logged_in"
  )] | length == 1
' <<<"$codex_mcp" >/dev/null

claude mcp get plugin:s3-lab-workspace:s3-research-memory |
  grep -Eq 'Status: .*Needs authentication'

printf '%s\n' 'clean Codex and Claude install: PASS'
