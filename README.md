# S3 Lab Workspace

연구실 공용 메모리와 랩미팅 슬라이드 제작을 한 번에 설치하는
Codex·Claude Code 플러그인입니다.

`s3-lab-workspace` 하나에 다음 기능이 함께 들어 있습니다.

- 중앙 `S3 Research Memory` 검색·근거 확인·정책에 따른 메모 작성
- 연구실 PPTX 템플릿을 보존하는 편집 가능한 랩미팅 슬라이드 제작
- 시스템·OS·AI serving 도식과 선택형 Manim GIF/동반 MP4 제작·검증

사용자가 개인 Codex 앱 ID, 로컬 MCP 서버, Docker와 별도 위키를 만들 필요는 없습니다.
두 클라이언트 모두 `https://s3wiki.yonsei.ac.kr/mcp`에 직접 연결합니다.

## 가장 쉬운 설치

### Codex

관리자가 보낸 `S3 Lab Workspace` 공유 링크를 열고 **+**를 한 번 누릅니다.
이것이 연구실 사용자의 기본 설치 경로입니다. 설치 뒤 새 작업을 열면 메모리 도구와
슬라이드 스킬이 함께 보입니다.

공유 링크를 받지 못했다면 저장소를 받은 폴더에서 아래 설치기를 실행합니다.

```bash
./scripts/install.sh --codex
```

### Claude Code

저장소를 받은 폴더에서 다음 한 줄을 실행합니다.

```bash
./scripts/install.sh --claude
```

Codex와 Claude Code가 모두 설치된 컴퓨터에서는 인자 없이 한 번 실행하면 둘 다
설치합니다.

```bash
./scripts/install.sh
```

Windows PowerShell에서는 다음을 사용합니다.

```powershell
.\scripts\install.ps1
```

설치기는 기존 마켓플레이스를 안전하게 갱신하고 `s3-lab-workspace` 하나만 설치한 뒤
설치 상태를 확인합니다. 다시 실행하면 중복 설치하지 않고 최신 버전으로 갱신합니다.
토큰 값을 요구하거나 출력하지 않습니다.

## 연결과 인증

Codex 앱 설치 화면의 **Authenticate**, Codex CLI의
`codex mcp login s3-research-memory` 또는 Claude Code의 `/mcp`에서 GitHub 로그인을
한 번 완료합니다. Codex 패키지에는 등록된 S3 Research Memory 앱 연결과 직접 HTTPS
MCP 설정이 함께 들어 있고, Claude Code는 같은 HTTPS MCP 설정을 자동으로 읽습니다.

공용 Bearer 토큰을 환경변수에 직접 저장하는 절차는 신규 사용자 기본 경로가 아닙니다.
서버 담당자의 제한된 호환·복구 작업에서만 사용합니다.

## 배포와 인증 경계

- Codex: 연구실 ChatGPT 워크스페이스 공유 또는 Git 마켓플레이스를 사용합니다.
- Claude Code: Git 마켓플레이스에서 같은 통합 플러그인을 설치합니다.
- 중앙 MCP 서비스 구현과 데이터는 플러그인에 복사하지 않습니다.
- 저장소가 공개돼도 S3 Research Memory는 GitHub OAuth 로그인을 요구합니다.

접근 권한이 없다는 오류가 나오면 설치 명령을 반복하지 말고 저장소 또는 워크스페이스
초대를 요청하세요.

## 관리자용 릴리스 확인

```bash
python3 tests/test_marketplace_packaging.py
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/s3-lab-workspace
claude plugin validate . --strict
claude plugin validate plugins/s3-lab-workspace --strict
```

릴리스 전에는 다음을 모두 확인합니다.

- Codex와 Claude 마켓플레이스에 `s3-lab-workspace`만 노출
- 통합 플러그인 안의 슬라이드 스킬이 원본과 byte-identical
- Codex와 Claude가 같은 중앙 MCP URL을 사용
- 등록된 S3 Research Memory 앱 ID와 중앙 MCP URL이 같은 서비스를 가리킴
- 깨끗한 사용자 설정에서 한 번의 설치로 플러그인이 활성화되고 OAuth 로그인을 요구함

릴리스와 사용자 권한 부여 절차는
[관리자 체크리스트](docs/admin-release.md)에 있습니다.

최종 프레젠테이션은 편집 가능한 PowerPoint 기본 개체를 우선하며, 시각 비율은
도식 종류별 범위로 제한합니다. 시간 의존 상호작용만 짧은 GIF 또는 포스터가 포함된
동반 MP4를 사용하고, 구조 QA·시각 검토·사용자 승인은 서로 다른 검증 단계로
유지합니다.
