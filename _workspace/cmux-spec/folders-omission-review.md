# folders-omission-review.md

> 검토 대상: `_workspace/cmux-spec/folder-manifest.md` + `_workspace/cmux-spec/folders/*.md`  
> 검토 기준: **누락(omission) 전용** — 사실 오류·스타일은 범위 외  
> 기준일: 2025-07-23

---

## 1. Verdict

**needs-update**

폴더 커버리지는 완전하다(21/21). 그러나 Windows 포트 에이전트에게 치명적인 주의사항 5건과 매니페스트 구조상 안내 범주 1건이 누락되어 있다.

---

## 2. Coverage Summary

| 항목 | 상태 |
|------|------|
| `cmux\` 최상위 폴더 vs 폴더 문서 | **완전** — 21/21 |
| 매니페스트 폴더 목록 vs 실제 디렉터리 | **완전** — 불일치 없음 |
| 매니페스트 분류 정의 표 | **완전** — 9개 분류 모두 기재 |
| 매니페스트 무시 대상 목록 | **완전** |
| 매니페스트 읽기 우선순위 | **부분 누락** — Windows 포트 관점 읽기 순서 없음 |
| 폴더 문서 내 Windows 포트 관련 주의사항 | **5건 누락** (아래 §4 참조) |

---

## 3. Missing Folders Table

| 폴더 | 상태 |
|------|------|
| (없음) | 모든 최상위 폴더에 문서 존재 |

---

## 4. Missing Content Coverage Table

아래 항목은 미래 에이전트가 Windows 포트 작업 중 잘못된 판단을 내릴 수 있는 **임계 누락**이다.

| # | 파일 | 누락 내용 | 영향 |
|---|------|-----------|------|
| M1 | `03-cli.md` | `CLI/cmux.swift`의 소켓 경로가 `/tmp/cmux.sock`으로 **하드코딩**되어 있음. Windows 포트에서는 Named Pipe로 교체해야 한다는 주의사항 없음 | 포트 에이전트가 소켓 경로를 그대로 이식할 위험 |
| M2 | `06-ghostty.md` | `GhosttyKit.xcframework`는 **macOS/ARM64 전용** 빌드 산출물임을 명시적으로 경고하지 않음. 불확실성 섹션에서 간접 암시만 있음 | 에이전트가 Windows에서 xcframework 링크 시도 가능 |
| M3 | `07-ghosttytabs-xcodeproj.md` | Xcode 프로젝트가 **Windows 포트와 무관**하며, Windows 빌드 경로는 CMake Presets + vcpkg임을 언급하지 않음 | 에이전트가 빌드 시스템 비교 없이 xcodeproj를 참조할 위험 |
| M4 | `13-resources.md` | `shell-integration/` 스크립트가 **zsh/bash 전용**임을 명시하지 않음. Windows 포트는 PowerShell/CMD 동등 스크립트가 필요하다는 안내 없음 | 포트 에이전트가 셸 통합을 이식하려 할 때 범위 오해 |
| M5 | `16-sources.md` | `Sources/Find/` 서브디렉터리가 트리에 등재되어 있지만 **내용 설명이 완전히 없음** (역할·포함 파일 불명) | 에이전트가 검색 기능 포팅 시 해당 폴더를 무시 또는 잘못 이해 |

아래 항목은 **보조 누락**으로, 절박하지는 않으나 완전성을 위해 기록한다.

| # | 파일 | 누락 내용 |
|---|------|-----------|
| B1 | `folder-manifest.md` | 각 폴더별 "Windows 포트 관련성" 열 없음 (직접 포팅 / Windows 동등물 필요 / macOS 전용 무시) |
| B2 | `folder-manifest.md` | 읽기 우선순위가 macOS 분석 관점만 있음 — Windows 포트 에이전트용 별도 순서 없음 |
| B3 | `03-cli.md` | IPC 프로토콜 직렬화 포맷(JSON 여부) 미기재 |
| B4 | `15-skills.md` | `cmux-debug-windows/` 스킬이 다루는 Windows 디버깅 범위 미기재 |
| B5 | `13-resources.md` | `bin/` 서브디렉터리 내용 미기재 (앱 번들에 포함되는 실행 파일 목록 불명) |

---

## 5. Optional Additions

아래는 현재 없어도 작업에 큰 지장 없지만, 포트 진행 시 자연스럽게 필요해질 항목이다.

- **`folder-manifest.md` 에 `win-relevance` 컬럼 추가**: `port-target` / `needs-win-equiv` / `macos-only` 세 값으로 분류. 에이전트 착수 전 스코핑 시간 단축 효과.
- **`16-sources.md` `Find/` 서브섹션 보완**: 인터미널 검색 오버레이의 구성 파일 목록 및 SwiftUI 컴포넌트 계층 간략 기술.
- **`06-ghostty.md` 에 "Windows 포트 대안" 절 추가**: `ghostty/` 대신 사용할 Windows 터미널 백엔드(예: WinPTY, ConPTY, Alacritty 기반) 참조 방향 기술.

---

## 6. Recommended Follow-up for the Next Agent

**우선 순위 순으로 처리한다:**

1. **M1 즉시 수정** — `03-cli.md`에 소켓 경로 `/tmp/cmux.sock`을 명시하고, Windows 포트에서 Named Pipe로 교체해야 한다는 `⚠️ Windows 포트 주의` 블록 추가.

2. **M2·M3 즉시 수정** — `06-ghostty.md`와 `07-ghosttytabs-xcodeproj.md`에 각각 macOS 전용/CMake 포트 대체 주의사항 추가.

3. **M4 즉시 수정** — `13-resources.md`에 셸 통합 스크립트가 zsh/bash 전용임을 명시하고, Windows 포트 범위(PowerShell/CMD 동등물 신규 작성 필요)를 안내.

4. **M5 수정** — `16-sources.md` `Find/` 절 채우기. `Sources/Find/` 실제 파일 목록 확인 후 보완.

5. **B1·B2 선택적 수정** — `folder-manifest.md`에 `win-relevance` 컬럼 및 Windows 포트 읽기 순서 추가. M1–M5 완료 후 진행해도 무방.

> **참고 문서**: `.rules/build-dependencies.md` (CMake/vcpkg 빌드 경로), `.rules/ipc-contract.md` (Named Pipe 규칙), `.rules/shell-integration.md` (PowerShell/CMD 환경변수)
