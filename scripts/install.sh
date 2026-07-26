#!/usr/bin/env bash
set -Eeuo pipefail

readonly MARKETPLACE_NAME="s3wiki-marketplace"
readonly DEFAULT_MARKETPLACE_URL="https://github.com/mrcha033/s3wiki-marketplace.git"
readonly MARKETPLACE_URL="${S3_LAB_MARKETPLACE_URL:-$DEFAULT_MARKETPLACE_URL}"
readonly PLUGIN_ID="s3-lab-workspace@${MARKETPLACE_NAME}"

usage() {
  printf '%s\n' \
    '사용법: ./scripts/install.sh [--codex|--claude|--all]' \
    '인자가 없으면 설치된 Codex와 Claude Code를 모두 설정합니다.'
}

want_codex=false
want_claude=false
case "${1:-}" in
  "")
    command -v codex >/dev/null 2>&1 && want_codex=true
    command -v claude >/dev/null 2>&1 && want_claude=true
    ;;
  --codex) want_codex=true ;;
  --claude) want_claude=true ;;
  --all) want_codex=true; want_claude=true ;;
  --help|-h) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

if [[ "$want_codex" == false && "$want_claude" == false ]]; then
  printf '%s\n' 'Codex 또는 Claude Code를 찾지 못했습니다.' >&2
  exit 1
fi

marketplace_registered() {
  local client=$1
  "$client" plugin marketplace list --json |
    grep -Eq "\"name\"[[:space:]]*:[[:space:]]*\"${MARKETPLACE_NAME}\""
}

plugin_installed() {
  local client=$1
  "$client" plugin list --json |
    grep -Eq "\"(pluginId|id)\"[[:space:]]*:[[:space:]]*\"${PLUGIN_ID}\""
}

install_codex() {
  command -v codex >/dev/null 2>&1 || {
    printf '%s\n' 'Codex를 찾지 못했습니다.' >&2
    return 1
  }
  if marketplace_registered codex; then
    codex plugin marketplace upgrade "$MARKETPLACE_NAME"
  else
    codex plugin marketplace add "$MARKETPLACE_URL"
  fi
  if ! plugin_installed codex; then
    codex plugin add "$PLUGIN_ID"
  fi
  codex plugin list --json |
    grep -Eq "\"pluginId\"[[:space:]]*:[[:space:]]*\"${PLUGIN_ID}\"" ||
    {
      printf '%s\n' 'Codex 설치 상태를 확인하지 못했습니다.' >&2
      return 1
    }
  printf '%s\n' 'Codex: S3 Lab Workspace 설치 완료'
}

install_claude() {
  command -v claude >/dev/null 2>&1 || {
    printf '%s\n' 'Claude Code를 찾지 못했습니다.' >&2
    return 1
  }
  if marketplace_registered claude; then
    claude plugin marketplace update "$MARKETPLACE_NAME"
  else
    claude plugin marketplace add "$MARKETPLACE_URL"
  fi
  if plugin_installed claude; then
    claude plugin update "$PLUGIN_ID"
  else
    claude plugin install "$PLUGIN_ID"
  fi
  claude plugin list --json |
    grep -Eq "\"id\"[[:space:]]*:[[:space:]]*\"${PLUGIN_ID}\"" ||
    {
      printf '%s\n' 'Claude Code 설치 상태를 확인하지 못했습니다.' >&2
      return 1
    }
  printf '%s\n' 'Claude Code: S3 Lab Workspace 설치 완료'
}

if [[ "$want_codex" == true ]]; then
  install_codex
fi
if [[ "$want_claude" == true ]]; then
  install_claude
fi

printf '%s\n' \
  '새 작업 또는 세션을 열어 사용하세요.' \
  '연결이 인증을 요청하면 Authenticate 또는 /mcp에서 GitHub 로그인을 완료하세요.' \
  '권한 오류가 나면 명령을 반복하지 말고 연구실 관리자에게 접근 권한을 요청하세요.'
