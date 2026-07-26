# 관리자 릴리스 체크리스트

연구실 사용자는 `s3-lab-workspace` 하나만 설치합니다. 두 개의 이전 플러그인이나 개인
Codex 앱을 따로 공유하지 않습니다.

## 사용자에게 열어 줄 것

### Codex

1. Codex에서 이 마켓플레이스의 `S3 Lab Workspace`를 엽니다.
2. **Share**에서 연구실 워크스페이스 또는 정확한 사용자만 선택합니다.
3. 생성된 공유 링크 하나만 전달합니다.

사용자는 링크를 열고 **+**만 누릅니다. GitHub 저장소 권한은 필요하지 않습니다.

### Claude Code

1. GitHub의 `mrcha033/s3wiki-marketplace`에 사용자를 **Read** 권한으로 초대합니다.
2. 초대 수락을 확인합니다.
3. 저장소를 받은 폴더에서 `./scripts/install.sh --claude`를 실행하게 합니다.

저장소가 비공개인 동안 GitHub 초대 없이 Claude Code 원클릭 설치가 된다고 안내하면
안 됩니다. 사용자 이름을 모르는 상태에서 저장소를 공개하거나 넓은 조직에 권한을
주지 않습니다.

## 릴리스 게이트

```bash
python3 tests/test_marketplace_packaging.py
python3 -m unittest discover -s skills/build-lab-meeting-slides/tests
bash -n scripts/install.sh
claude plugin validate . --strict
claude plugin validate plugins/s3-lab-workspace --strict
```

그 뒤 기존 설정을 재사용하지 않는 임시 사용자 디렉터리에서 다음을 확인합니다.

1. 마켓플레이스 추가
2. `s3-lab-workspace` 한 번 설치
3. 랩미팅 슬라이드 스킬 노출
4. 중앙 MCP 연결과 도구 열 개 노출
5. `search_lessons(limit=1)` 읽기 호출

운영 서버가 GitHub OAuth 모드라면 이 단계에서 로그인 한 번을 완료합니다. 현재
`open` 시험 운영은 별도 로그인이 없으므로, 운영 전환 완료로 간주하지 않습니다.

## 릴리스 후

- 통합 플러그인을 먼저 설치하고 이전 두 플러그인을 제거합니다.
- Codex와 Claude Code를 새로 열어 중복 스킬이나 중복 MCP 서버가 없는지 확인합니다.
- 라이브 MCP, 쓰기 정책, 슬라이드 시각 품질은 패키징 검사와 별도로 확인합니다.
