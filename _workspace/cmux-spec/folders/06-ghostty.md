# `ghostty`

## 역할 / 목적

**git 서브모듈** — `manaflow-ai/ghostty` 포크(upstream: `ghostty-org/ghostty`). Zig로 작성된 터미널 렌더링 엔진 원천 코드다. 빌드 결과물인 `GhosttyKit.xcframework`(libghostty)가 cmux 앱의 터미널 렌더링 코어로 사용된다. GPU 가속 렌더링, VT 시퀀스 파싱, PTY 관리를 담당한다.

## 주요 내용

```
ghostty/
├── src/                   # Zig 소스 (터미널 엔진 핵심)
├── macos/                 # macOS 전용 Swift/ObjC 바인딩
│   └── GhosttyKit.xcframework (빌드 출력물)
├── include/               # C API 헤더 (ghostty.h 소스)
├── dist/                  # 배포 바이너리 (사전 빌드 XCFramework 포함 가능)
├── build.zig              # Zig 빌드 정의
├── build.zig.zon          # Zig 패키지 의존성
├── AGENTS.md              # 이 서브모듈 전용 에이전트 규칙
├── AI_POLICY.md           # AI 기여 정책
└── HACKING.md             # 개발자 가이드
```

빌드 명령: `cd ghostty && zig build -Demit-xcframework=true -Doptimize=ReleaseFast`

루트의 `ghostty.h`는 이 서브모듈의 `include/` 헤더에서 파생된 Swift ↔ C 브리지 계약이다.

## 저장소 상호작용 / 의존성

- `scripts/setup.sh`가 서브모듈 초기화 + GhosttyKit 빌드를 자동 수행한다.
- `Sources/GhosttyTerminalView.swift`, `Sources/GhosttyConfig.swift`가 GhosttyKit API를 직접 사용한다.
- `cmux-Bridging-Header.h`가 `ghostty.h`를 포함해 Swift에서 C API 접근을 허용한다.
- `.gitmodules`에서 `https://github.com/manaflow-ai/ghostty.git`, branch `main`으로 추적.
- `docs/ghostty-fork.md`에 upstream 대비 cmux 전용 변경사항이 기록된다.

## 편집 지침

**읽기 전용 취급**. 이 서브모듈 내 변경은 `manaflow-ai/ghostty` 포크 저장소에 별도 PR로 반영해야 한다. 직접 수정 후 커밋하면 서브모듈 포인터만 바뀌고 upstream 동기화가 어려워진다. Ghostty 동작 조사 시 `docs/ghostty-fork.md`를 먼저 확인한다.

> **Windows 포트 주의**: 여기서 생성되는 `GhosttyKit.xcframework`는 macOS 빌드 산출물이다. cmux-win은 이 xcframework를 직접 링크하지 않으며, Windows 전용 터미널 스택(예: ConPTY 기반 구현)으로 동등 기능을 다시 설계해야 한다.

## 불확실성

- 서브모듈이 현재 Windows 환경에서 체크아웃되어 있는지, 빌드된 `GhosttyKit.xcframework`가 존재하는지 확인 불가 (macOS 전용 빌드 산출물).
- `CLAUDE.md`에 `cd cmuxd && zig build` 명령이 있으나 `cmuxd/` 디렉터리가 최상위에 없다. ghostty 서브모듈 내부 또는 별도 서브모듈로 추정된다.
