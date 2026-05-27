# cmux 폴더 매니페스트

> 대상: `cmux/` read-only 참조 트리의 최상위 디렉터리 전체  
> 생성 기준: 직접 탐색 + `_workspace/cmux-spec/project-overview.md`, `_workspace/17-functional-spec.md`, `_workspace/18-cmux-parity.md` 참조  
> 파일명 규칙: `NN-<slug>.md` (NN = 정렬 번호, dot-dirs는 `dot-` 접두사)

---

## 폴더 목록

| # | 소스 폴더 | 분류 | win-relevance | 역할 요약 | 폴더 문서 |
|---|-----------|------|---------------|-----------|-----------|
| 00 | `.claude` | config | macos-only | Claude Code 슬래시 커맨드 정의 | [00-dot-claude.md](folders/00-dot-claude.md) |
| 01 | `.github` | automation | needs-win-equiv | GitHub Actions CI/CD 워크플로 (PR CI, 릴리즈, 나이틀리, Homebrew 갱신) | [01-dot-github.md](folders/01-dot-github.md) |
| 02 | `Assets.xcassets` | packaging | needs-win-equiv | Xcode 앱 아이콘·이미지 에셋 카탈로그 | [02-assets-xcassets.md](folders/02-assets-xcassets.md) |
| 03 | `CLI` | primary source | needs-win-equiv | `cmux` CLI 전체 구현 (단일 Swift 파일, ~135KB) | [03-cli.md](folders/03-cli.md) |
| 04 | `docs` | docs | port-target | 내부 기술 스펙 (알림 API, 브라우저 포트, v2 마이그레이션, Ghostty 포크 노트) | [04-docs.md](folders/04-docs.md) |
| 05 | `docs-site` | docs | reference-only | 공개 문서 사이트 (Next.js + Fumadocs, Vercel 배포) | [05-docs-site.md](folders/05-docs-site.md) |
| 06 | `ghostty` | external | needs-win-equiv | git 서브모듈: manaflow-ai/ghostty (Zig 터미널 엔진, GhosttyKit.xcframework 원천) | [06-ghostty.md](folders/06-ghostty.md) |
| 07 | `GhosttyTabs.xcodeproj` | primary source | macos-only | 주 빌드 경로 — Xcode 프로젝트 정의 (타겟, 빌드 설정, 코드 사이닝) | [07-ghosttytabs-xcodeproj.md](folders/07-ghosttytabs-xcodeproj.md) |
| 08 | `GhosttyTabsTests` | tests | reference-only | Swift 유닛 테스트 (호스트에서 직접 실행 가능) | [08-ghosttytabstests.md](folders/08-ghosttytabstests.md) |
| 09 | `GhosttyTabsUITests` | tests | reference-only | Swift XCTest UI 자동화 테스트 (VM 필수) | [09-ghosttytabsuitests.md](folders/09-ghosttytabsuitests.md) |
| 10 | `graphify-out` | generated | macos-only | graphify 에이전트 스킬이 생성한 지식 그래프 캐시 — 무시 대상 | [10-graphify-out.md](folders/10-graphify-out.md) |
| 11 | `homebrew-cmux` | external | macos-only | git 서브모듈: Homebrew Cask 정의 (릴리즈 파이프라인 자동 갱신) | [11-homebrew-cmux.md](folders/11-homebrew-cmux.md) |
| 12 | `node_modules` | generated | macos-only | 루트 `vercel` 의존성 설치 산출물 — 무시 대상 | [12-node-modules.md](folders/12-node-modules.md) |
| 13 | `Resources` | packaging | needs-win-equiv | 앱 번들 런타임 리소스 (셸 통합 스크립트, terminfo, Info.plist) | [13-resources.md](folders/13-resources.md) |
| 14 | `scripts` | support | needs-win-equiv | 빌드·개발·테스트·릴리즈 Shell 스크립트 | [14-scripts.md](folders/14-scripts.md) |
| 15 | `skills` | docs | reference-only | AI 에이전트용 스킬 문서 (cmux 소켓 API, 브라우저, 릴리즈) | [15-skills.md](folders/15-skills.md) |
| 16 | `Sources` | primary source | port-target | Swift 앱 소스 전체 (UI, IPC, 터미널/브라우저 패인, 알림, 업데이트) | [16-sources.md](folders/16-sources.md) |
| 17 | `tests` | tests | reference-only | Python e2e 테스트 v1 (소켓 API v1, 레거시, VM 필수) | [17-tests.md](folders/17-tests.md) |
| 18 | `tests_v2` | tests | reference-only | Python e2e 테스트 v2 (소켓 API v2, 현행, VM 필수) | [18-tests-v2.md](folders/18-tests-v2.md) |
| 19 | `vendor` | external | reference-only | git 서브모듈 루트 (bonsplit: 스플릿 패인 레이아웃 엔진) | [19-vendor.md](folders/19-vendor.md) |
| 20 | `web` | docs | reference-only | 마케팅·랜딩 사이트 (Next.js, Vercel 배포, docs-site와 별개) | [20-web.md](folders/20-web.md) |

---

## 분류 정의

| 분류 | 설명 |
|------|------|
| **primary source** | 앱·CLI 핵심 Swift 소스. 기능 변경 시 직접 수정 대상. |
| **support** | 빌드·개발·릴리즈 보조 스크립트. 앱 로직 변경과 간접 연동. |
| **docs** | 기술 문서, 공개 문서 사이트, 에이전트 스킬 문서. |
| **tests** | 유닛·UI·e2e 테스트. |
| **external** | git 서브모듈 (upstream 저장소 소유). 직접 수정 지양. |
| **generated** | 빌드·도구 생성물. 무시 또는 재생성 대상. |
| **packaging** | 앱 번들·배포 리소스 (에셋, Info.plist, Cask). |
| **automation** | CI/CD 워크플로 (.github/workflows). |
| **config** | 에이전트/도구 설정 (.claude). |

`win-relevance` 값은 아래 의미를 가진다.

| 값 | 의미 |
|----|------|
| `port-target` | Windows 포트가 직접 기능/계약을 계승해야 하는 핵심 입력 |
| `needs-win-equiv` | 동등 기능은 필요하지만 구현 경로나 자산은 새로 가져가야 함 |
| `reference-only` | 동작 참고용 문서·테스트·외부 자산 |
| `macos-only` | macOS 전용이거나 생성물/운영 보조 경로라 포팅 대상 아님 |

---

## 중요도 / 읽기 우선순위

에이전트가 cmux 앱 기능을 분석·포팅할 때 권장 읽기 순서:

1. **`docs/`** — API 계약 정의 (특히 `agent-browser-port-spec.md`, `v2-api-migration.md`)
2. **`Sources/`** — 앱 핵심 구현 (`cmuxApp.swift` → `TerminalController.swift` → `Workspace.swift`)
3. **`CLI/`** — CLI 명령 구현 전체
4. **`tests_v2/`** — 현행 동작 검증 기준
5. **`Resources/shell-integration/`** — 셸 통합 동작 파악
6. **`scripts/`** — 빌드·개발 워크플로

### Windows 포트 에이전트용 빠른 읽기 순서

1. **`docs/`** — 사용자 행동 계약과 IPC/브라우저/알림 의미를 먼저 고정
2. **`Sources/`** — 실제 macOS 구현 구조 확인
3. **`CLI/`** — 명령 표면과 IPC 호출 방식 확인
4. **`tests_v2/` → `tests/`** — 현행 동작과 레거시 호환 기준 확인
5. **`Resources/`** — 셸 통합·번들 리소스 중 Windows 동등물이 필요한 영역 확인
6. **`ghostty/`, `GhosttyTabs.xcodeproj`** — macOS 전용 제약과 대체 필요 지점만 확인

---

## 무시 대상

- `graphify-out/` — 생성물, 완전히 무시
- `node_modules/` — JS 의존성, 완전히 무시
- `ghostty/` 내부 — 읽기는 가능, 수정은 upstream 저장소에서
- `homebrew-cmux/` — 릴리즈 파이프라인 자동 관리
