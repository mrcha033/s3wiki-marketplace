# 관리자 릴리스 체크리스트

연구실 사용자는 `s3-lab-workspace` 하나만 설치합니다. 두 개의 이전 플러그인이나
별도 MCP 설정을 따로 배포하지 않습니다.

## 사용자에게 열어 줄 것

### Codex

1. Codex에서 이 마켓플레이스의 `S3 Lab Workspace`를 엽니다.
2. **Share**에서 연구실 워크스페이스 또는 정확한 사용자만 선택합니다.
3. 생성된 공유 링크 하나만 전달합니다.

사용자는 링크를 열고 **+**만 누릅니다. GitHub 저장소 권한은 필요하지 않습니다.

### Claude Code

1. 저장소 공개 여부와 사용자의 Git 접근을 확인합니다.
2. 저장소를 받은 폴더에서 `./scripts/install.sh --claude`를 실행하게 합니다.
3. `/mcp`에서 S3 Research Memory의 GitHub 로그인을 완료하게 합니다.

저장소를 공개하면 별도 GitHub 초대는 필요하지 않습니다. 저장소 배포 권한과 중앙
MCP의 GitHub OAuth 인증은 서로 다른 경계입니다.

## 릴리스 게이트

```bash
python3 tests/test_marketplace_packaging.py
python3 -m unittest discover -s skills/build-lab-meeting-slides/tests
bash -n scripts/install.sh
S3_LAB_MARKETPLACE_URL="$PWD" bash tests/test_clean_install.sh
claude plugin validate . --strict
claude plugin validate plugins/s3-lab-workspace --strict
```

`test_clean_install.sh`는 기존 설정을 재사용하지 않는 임시 사용자 디렉터리에서 실제
Codex와 Claude Code를 각각 두 번 설치해 최초 설치와 안전한 재실행을 함께 확인합니다.
GitHub Actions도 고정된 지원 버전의 두 CLI로 이 검사를 실행합니다. 그 뒤 다음을
확인합니다.

1. 마켓플레이스 추가
2. `s3-lab-workspace` 한 번 설치
3. 랩미팅 슬라이드 스킬 노출
4. 등록 앱 ID와 중앙 MCP URL 포함
5. 인증 전 연결이 OAuth 로그인을 요구함

자동 검사는 사용자 동의 화면을 대신 통과하지 않습니다. 실제 릴리스 확인에서는
Codex 설치 인증, `codex mcp login s3-research-memory` 또는 Claude Code `/mcp`에서
GitHub 로그인을 한 번 완료하고 `search_lessons(limit=1)`을 호출합니다.

## 릴리스 후

- 통합 플러그인을 먼저 설치하고 이전 두 플러그인을 제거합니다.
- 사용자 설정에 남은 수동 `s3-research-memory` Bearer MCP 항목을 제거합니다.
- Codex와 Claude Code를 새로 열어 중복 스킬이나 중복 MCP 서버가 없는지 확인합니다.
- 라이브 MCP, 쓰기 정책, 슬라이드 시각 품질은 패키징 검사와 별도로 확인합니다.
