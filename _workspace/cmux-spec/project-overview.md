# cmux 프로젝트 개요

> 작성 기준: `cmux/` 소스 트리 직접 분석 (read-only 참조용)  
> 위치: `C:\Users\hdmun\repo\cmux-win\cmux\`  
> 최종 갱신: 2026-06 (에이전트 초기 작성)

---

## 1. 프로젝트 정체

**cmux**는 AI 코딩 에이전트(Claude Code, OpenCode, Codex 등)를 위한 **네이티브 macOS 터미널 앱**이다.  
Ghostty 터미널 엔진(libghostty, Zig 빌드)을 렌더링 코어로 채용하고, **Swift/SwiftUI + AppKit 어댑터 계층**으로 묶어 다음 기능을 제공한다.

| 사용자-facing 기능 | 설명 |
|--------------------|------|
| 수직 사이드바 탭 | 워크스페이스별 git 브랜치·CWD·포트·알림 텍스트 표시 |
| 알림 시스템 | OSC 9/99/777 시퀀스·CLI `cmux notify` 수신, 파란 링 + 탭 하이라이트 |
| 알림 패널 | 미읽은 알림 일람, `Cmd+Shift+U` 최신 미읽음 점프 |
| 스플릿 패인 & 수평 탭 | 수평/수직 분할 (Bonsplit 레이아웃 엔진), 각 패인별 수평 탭 바 (새 터미널/브라우저 생성 `+` 메뉴 버튼 제공) |
| 인앱 브라우저 | WKWebView 브라우저 패인 + `agent-browser` 포트(스냅샷·클릭·JS 평가) |
| CLI & 소켓 API | `cmux` CLI(50개 top-level 명령) + Unix 소켓(`/tmp/cmux.sock`) v1/v2 프로토콜(v2 메서드 142개 + v1 사이드바 15개 + DEBUG 20개) |
| Claude Code 통합 | `Resources/bin/claude` 래퍼·세션 추적·`SessionStart`/`Stop`/`Notification` 훅 라우팅·사이드바 상태 |
| 자동 업데이트 | Sparkle 프레임워크 (stable · nightly 채널) |
| 크래시 리포팅 | Sentry SDK (`Sources/AppDelegate.swift`, `Sources/GhosttyTerminalView.swift`). PostHog 사용 분석과 별도로 운영됨 |

**라이선스**: AGPL-3.0-or-later  
**배포**: DMG 직접 다운로드, Homebrew Cask (`manaflow-ai/cmux`), GitHub Releases  
**플랫폼 요건**: macOS 13+  

---

## 2. 최상위 디렉터리 구조

```
cmux/
├── [빌드·프로젝트 정의]
│   ├── GhosttyTabs.xcodeproj/     Xcode 프로젝트 (주 빌드 경로)
│   ├── Package.swift              SwiftPM 매니페스트 (SwiftTerm 의존; 보조/레거시)
│   ├── Package.resolved           SwiftPM lock
│   ├── cmux.entitlements          macOS 샌드박스 권한 선언
│   └── cmux-Bridging-Header.h     ObjC ↔ Swift 브리지 헤더
│
├── [앱 소스]
│   ├── Sources/                   Swift 앱 소스 (SwiftUI + AppKit 어댑터 + Ghostty API)
│   │   ├── cmuxApp.swift          `@main` 진입점 (SwiftUI App). Settings·About·Debug 창 컨트롤러 포함 (~2700줄)
│   │   ├── AppDelegate.swift      NSApplication delegate 어댑터·서비스·키 이벤트 핸들러. Sentry SDK 사용
│   │   ├── TerminalController.swift  Unix 소켓 IPC (v1/v2 프로토콜)
│   │   ├── TabManager.swift       워크스페이스 CRUD·선택·순서 관리
│   │   ├── Workspace.swift        사이드바 탭 모델 (Bonsplit + Panel 소유)
│   │   ├── Panels/                패인 타입 (TerminalPanel, BrowserPanel, …)
│   │   ├── Find/                  표면 검색 오버레이
│   │   ├── PostHogAnalytics.swift 운영 분석 연동 지점
│   │   └── Update/                Sparkle 업데이터 서브시스템
│   └── CLI/
│       └── cmux.swift             CLI 도구 전체 구현 (단일 파일, ~135 KB)
│
├── [외부 의존성·서브모듈]
│   ├── ghostty/                   git 서브모듈: manaflow-ai/ghostty 포크 (Zig)
│   │                              → libghostty / GhosttyKit.xcframework 빌드 원천
│   └── vendor/bonsplit/           git 서브모듈: manaflow-ai/bonsplit (스플릿 레이아웃)
│
├── [테스트]
│   ├── GhosttyTabsTests/          Swift 유닛 테스트 (xcodebuild)
│   ├── GhosttyTabsUITests/        Swift UI 테스트 (UTM VM에서 실행)
│   ├── tests/                     Python e2e 테스트 v1 (소켓 API v1 기반)
│   └── tests_v2/                  Python e2e 테스트 v2 (소켓 API v2 기반)
│
├── [문서·콘텐츠]
│   ├── docs/                      기술 스펙 문서 (Markdown)
│   │   ├── notifications.md       알림 API 가이드
│   │   ├── agent-browser-port-spec.md  브라우저 포트 스펙
│   │   ├── ghostty-fork.md        ghostty 포크 diff 노트
│   │   └── v2-api-migration.md    v1→v2 마이그레이션 가이드
│   ├── docs-site/                 문서 사이트 (Next.js + Vercel)
│   └── README*.md                 18개 언어 README
│
├── [빌드·배포 스크립트]
│   ├── scripts/                   Shell 스크립트
│   │   ├── setup.sh               서브모듈 초기화 + GhosttyKit 빌드
│   │   ├── reload.sh / reload*.sh Debug/Release 앱 재시작 유틸
│   │   ├── rebuild.sh             전체 재빌드 보조 스크립트
│   │   ├── bump-version.sh        버전 번프 (MARKETING/BUILD)
│   │   ├── run-tests-v1.sh        v1 e2e 테스트 스위트 실행
│   │   ├── run-tests-v2.sh        v2 e2e 테스트 스위트 실행
│   │   └── sparkle_generate_*.sh  Sparkle 키·appcast 운영 스크립트
│   └── .github/workflows/
│       ├── ci.yml                 PR CI
│       ├── release.yml            릴리즈 빌드·공증·DMG 생성
│       ├── nightly.yml            나이틀리 빌드 (new commits 감지)
│       └── update-homebrew.yml    Homebrew 카스크 자동 갱신
│
├── [웹·마케팅]
│   └── web/                       마케팅/랜딩 사이트 (Next.js)
│
├── [에이전트 스킬·지식]
│   └── skills/                    cmux·cmux-browser 등 에이전트용 스킬 문서
│
├── [배포 지원]
│   ├── homebrew-cmux/             Homebrew Cask 정의
│   └── Resources/                 앱 번들 리소스
│
└── [저부가치/생성물]
    ├── graphify-out/              생성된 그래프 출력물
    └── node_modules/              루트 package.json의 `vercel` 의존성 설치물 (docs-site·web은 각자 node_modules 보유)
```

**루트 주요 파일**

| 파일 | 역할 |
|------|------|
| `GhosttyTabs.xcodeproj/` | Xcode 빌드 정의 (scheme: `cmux`) |
| `Package.swift` | SwiftPM – SwiftTerm 의존; 보조적 역할 |
| `package.json` | 루트 JS 매니페스트 — `vercel` 단일 의존성만 선언 (워크스페이스 정의 아님) |
| `bun.lock` | Bun lockfile; JS 의존성 재현은 `bun install` 기준 |
| `CLAUDE.md` | 에이전트용 개발 워크플로 가이드 |
| `AGENTS.md` | 에이전트 규칙 인덱스 |
| `PROJECTS.md` | 크로스-프로젝트 버그/기능 추적 로그 |
| `TODO.md` | 작업 백로그 |
| `CHANGELOG.md` | 릴리즈 히스토리 |
| `ghostty.h` | Ghostty 임베딩 API C 헤더; Zig 코어 ↔ Swift 계약 |
| `.gitmodules` | git 서브모듈 3개 참조: `ghostty`, `homebrew-cmux`, `vendor/bonsplit` |

---

## 3. 실행 모델 / 아키텍처

### 레이어 구조

```
┌─────────────────────────────────────────────────────┐
│  cmux 앱 (Swift/SwiftUI + AppKit 어댑터)              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ 사이드바/탭  │  │ Bonsplit 패인 │  │ 브라우저패인│  │
│  │ TabManager  │  │  레이아웃    │  │ WKWebView  │  │
│  └─────────────┘  └──────┬───────┘  └────────────┘  │
│                          │                           │
│              ┌───────────┴──────────┐                │
│              │ GhosttyKit.xcframework│               │
│              │  (libghostty, Zig)   │                │
│              └──────────────────────┘                │
│                                                       │
│  TerminalController ──▶ Unix 소켓 /tmp/cmux.sock     │
└────────────────────────┬────────────────────────────┘
                         │ (IPC)
                    ┌────┴─────┐
                    │ cmux CLI │  (CLI/cmux.swift)
                    └──────────┘
```

### 핵심 객체 관계

- **`cmuxApp`**: `@main` 진입점. SwiftUI App lifecycle 시작, `AppDelegate` 주입. Settings/About/Debug 창 컨트롤러도 이 파일에 포함됨 (~2700줄)
- **`AppDelegate`**: NSApplication delegate 어댑터, Finder 통합·서비스 라우팅·키 이벤트 처리. **Sentry SDK** 크래시 리포팅 초기화 포함  
- **`TabManager`**: 윈도우-워크스페이스 전체 상태 소유, 소켓 명령 실행 위임  
- **`Workspace`**: 사이드바 탭 단위; `BonsplitController` + `Panel` 배열 소유  
- **`TerminalController`** (싱글턴): Unix 소켓 수신, v1/v2 커맨드 파싱·디스패치  
- **`Panel`** (프로토콜): `TerminalPanel` (Ghostty surface) / `BrowserPanel` (WKWebView)  
- **`TerminalNotificationStore`**: OSC 시퀀스 파싱, 알림 상태 저장·읽음 처리  
- **`PostHogAnalytics`**: 운영 분석 이벤트 송신 지점; 개인정보/opt-in 영향이 큰 보조 경계  

### IPC 프로토콜

| 버전 | 상태 | 참조 |
|------|------|------|
| v1 | 유지(레거시 호환) | `tests/` |
| v2 | 현행 (CLI 기본) | `tests_v2/`, `docs/v2-api-migration.md` |

- `surface`, `pane`, `workspace`, `window` 4계층 식별 체계  
- 짧은 ref(`surface:1`) 기본, UUID는 `--id-format uuids` 옵션으로 선택 가능  
- `system.identify` = 에이전트 자기 위치 확인용 필수 엔드포인트  

### 터미널 렌더링

- `ghostty/` 서브모듈(Zig) → `zig build -Demit-xcframework=true -Doptimize=ReleaseFast` → `GhosttyKit.xcframework`  
- GPU 가속, 기존 `~/.config/ghostty/config` (테마·폰트·색상) 그대로 읽음  

---

## 4. 빌드·테스트·툴링

### 빌드

| 단계 | 명령 |
|------|------|
| 최초 설정 | `./scripts/setup.sh` (서브모듈 초기화 + GhosttyKit 빌드) |
| 앱 빌드 | `xcodebuild -project GhosttyTabs.xcodeproj -scheme cmux -configuration Debug build` |
| Ghostty 재빌드 | `cd ghostty && zig build -Demit-xcframework=true -Doptimize=ReleaseFast` |
| Dev 재시작 | `./scripts/reload.sh --tag <tag>` |
| Release 재시작 | `./scripts/reloadp.sh` |

> **주의**: `--tag`를 지정하면 번들 ID·소켓·DerivedData가 격리되어 병렬 실행 가능.

### 웹/문서 tooling

| 영역 | 기준 도구 |
|------|-----------|
| `docs-site/`, `web/` | Bun (`bun.lock` 기준) |
| Ghostty 서브모듈 빌드 | Zig |
| 앱/테스트 | Xcode / `xcodebuild` |

### 테스트

| 종류 | 위치 | 실행 |
|------|------|------|
| Swift 유닛 테스트 | `GhosttyTabsTests/` | `xcodebuild … test` |
| Swift UI 테스트 | `GhosttyTabsUITests/` | `ssh cmux-vm '… test'` (반드시 UTM VM) |
| Python e2e v1 | `tests/*.py` | `./scripts/run-tests-v1.sh` (VM) |
| Python e2e v2 | `tests_v2/*.py` | `./scripts/run-tests-v2.sh` (VM) |

> **규칙**: e2e 및 UI 테스트는 호스트 머신에서 실행하지 않는다 – 항상 `ssh cmux-vm`.

### 릴리즈 파이프라인

1. `./scripts/bump-version.sh` → `CHANGELOG.md` + `docs-site/content/docs/changelog.mdx` 갱신  
2. `git tag vX.Y.Z && git push origin vX.Y.Z` → GitHub Actions `release.yml` 트리거  
3. 빌드 → Apple 공증 → `cmux-macos.dmg` GitHub Release 첨부  
4. `update-homebrew.yml` → Homebrew 카스크 자동 갱신  
5. Sparkle appcast → 앱 내 자동 업데이트 (stable / nightly 채널)  

---

## 5. 문서·테스트·배포·지원 자산

| 자산 | 위치 | 용도 |
|------|------|------|
| 기술 스펙 | `docs/` | 알림 API, 브라우저 포트 스펙, ghostty 포크 노트, v2 마이그레이션 |
| 사용자 문서 | `docs-site/` | Next.js 기반 공개 문서 사이트 (Vercel 배포) |
| 다국어 README | `README*.md` (18개) | 사용자-facing 설치·기능 안내 |
| 에이전트 스킬 | `skills/` | `cmux`, `cmux-browser`, `cmux-debug-windows` 등 AI 에이전트용 가이드 |
| 변경 이력 | `CHANGELOG.md` | 릴리즈 별 변경 내역 |
| 기여 가이드 | `CONTRIBUTING.md` | 기여자 워크플로 |
| 라이선스 | `LICENSE`, `THIRD_PARTY_LICENSES.md` | AGPL-3.0, 서드파티 고지 |
| 프로젝트 추적 | `PROJECTS.md`, `TODO.md` | 완료/예정 작업 일람 |
| 배포 운영 스크립트 | `scripts/sparkle_generate_*.sh`, `scripts/derive_sparkle_public_key.swift` | Sparkle 키·appcast 운영 |

---

## 6. 향후 에이전트/개발자를 위한 읽기 우선순위

1. **`CLAUDE.md`** — 빌드·개발·릴리즈·테스트 워크플로 전체 요약. 작업 시작 전 필수.  
2. **`README.md`** — 사용자 기능 전체 조감, 키보드 단축키 레퍼런스.  
3. **`Sources/cmuxApp.swift`** — 실제 `@main` 진입점. SwiftUI App bootstrap 확인용.  
4. **`docs/agent-browser-port-spec.md`** — v1/v2 API 개념 용어(`window`/`workspace`/`pane`/`surface`) 정의, 브라우저 자동화 현황.  
5. **`docs/v2-api-migration.md`** — 소켓 API v2 변경 사항.  
6. **`docs/notifications.md`** — 알림 CLI 사용법과 에이전트 훅 패턴.  
7. **`Sources/TerminalController.swift`** — IPC 프로토콜 서버 구현 전체. 소켓 명령 추가 시 필독.  
8. **`Sources/Workspace.swift`** / **`Sources/TabManager.swift`** — 상태 모델 핵심.  
9. **`CLI/cmux.swift`** — CLI 명령 구현 전체 (~135 KB 단일 파일).  
10. **`vendor/bonsplit/`** — 스플릿 레이아웃 동작 파악 필요 시.  

---

## 7. 제외 또는 저부가치 영역

| 디렉터리/파일 | 분류 | 취급 방법 |
|---------------|------|-----------|
| `node_modules/` | JS 의존성 생성물 | 무시. `docs-site/`, `web/` 빌드 시 자동 재생성. |
| `graphify-out/` | 그래프 생성 출력물 | 무시. 코드 탐색 시 스킵. |
| `ghostty/` (서브모듈 내부) | 업스트림 Ghostty 포크 | 읽기만. 변경 시 별도 `manaflow-ai/ghostty` 포크 PR 필요. `docs/ghostty-fork.md` 참조. |
| `vendor/bonsplit/` | git 서브모듈 | 직접 수정 최소화. split 로직 실체는 `vendor/bonsplit/Sources/Bonsplit/`이며, `Sources/Workspace.swift`가 `import Bonsplit`로 `BonsplitController`를 직접 소비한다 (별도 wrapper 계층 없음). |
| `homebrew-cmux/` | 배포 지원 서브모듈 | 릴리즈 파이프라인이 자동 갱신. 수동 편집 전 submodule 업데이트 흐름부터 확인. |
| `Assets.xcassets/` | 이미지 자산 | UI 아이콘·이미지 변경 시만 참조. |
| `Package.swift` (루트) | 보조/레거시 | 주 빌드는 Xcode 프로젝트 사용. 현행 코드와 불일치 가능. |
| `.claude/` | Claude Code 설정 | 에이전트 설정 전용. 코드 로직과 무관. |
| `Sources/UITestRecorder.swift` | 앱 번들 내 테스트 훅 | 테스트 보조 코드지만 앱 소스에 포함되므로 무심코 수정하지 않기. |
| `Sources/PostHogAnalytics.swift` | 분석/프라이버시 경계 | 텔레메트리·개인정보 영향이 크므로 의도 없는 수정 금지. |
| Sentry SDK | 크래시 리포팅 경계 | `AppDelegate.swift` + `GhosttyTerminalView.swift`에 `import Sentry`. PostHog와 별도로 운영됨. 의도 없는 수정 금지. |

---

## 8. 가정 및 불확실성 플래그

| # | 항목 | 불확실 이유 |
|---|------|-------------|
| 1 | `Package.swift` 실사용 여부 | `Sources/` 목표로 SwiftTerm 의존을 선언하지만 실제 앱은 Xcode 프로젝트를 통해 GhosttyKit 기반으로 빌드됨. 레거시이거나 대안 빌드 경로일 가능성이 있음. |
| 2 | `ghostty/` 서브모듈 커밋 상태 | 서브모듈이 현재 체크아웃되어 있는지, 빌드된 `GhosttyKit.xcframework`가 존재하는지 Windows 환경에서 확인 불가. |
| 3 | `cmuxd` 위치 미확인 | `CLAUDE.md`에 `cd cmuxd && zig build -Doptimize=ReleaseFast`가 릴리즈/번들링 빌드 단계로 능동 기재되어 있다 (2곳). `.gitmodules`에는 ghostty/homebrew-cmux/vendor-bonsplit 3개만 등록되며 `cmuxd/`는 현재 트리에 존재하지 않음. 미커밋·미체크아웃된 별도 Zig 컴포넌트(cmux daemon 추정)이거나 dead reference일 수 있다. **dead reference로 단정하지 않는다**. |
| 4 | `web/` vs `docs-site/` 구분 | 두 Next.js 앱의 정확한 역할 분리가 `web/README.md`를 읽지 않아 불명확. 마케팅 사이트 vs 문서 사이트로 추정. |
| 5 | ~~`Sources/Panels/bonsplit/`와 `vendor/bonsplit/`의 관계~~ (해소됨) | **해소**: `Sources/Panels/bonsplit/`는 존재하지 않는다. Bonsplit 실체는 `vendor/bonsplit/Sources/Bonsplit/`(서브모듈)이며 `Sources/Workspace.swift`가 `import Bonsplit`로 `BonsplitController`를 직접 소비한다. wrapper/복사본 계층 없음. (출처: `Sources/Workspace.swift:3,50,131`) |
| 6 | v1 소켓 API 폐기 시점 | `docs/agent-browser-port-spec.md`에서 v1 폐기 언급이 있으나 구체적 마일스톤 미정. |
