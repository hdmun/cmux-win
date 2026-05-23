# 저장소 역할 경계 & 밀스톤

## 저장소 역할 경계

| 경로 | 역할 | 수정 정책 |
|------|------|-----------|
| `cmux\` | macOS Swift 참조 구현 — 기능 동작 방식의 정답 레퍼런스 (read-only reference tree) | **절대 수정 금지** |
| `ghostty\` | 공유 업스트림 자산 (config schema, color theme 등) — cmux 상위 프로젝트 참조 | **절대 수정 금지** |
| `_workspace\` | 계획 및 설계 문서 전용 (예: .md, .svg, .png, .drawio) | 코드 파일(.cpp, .cs, .h 등) 추가 금지; 문서/다이어그램 자산만 허용 |
| `plans\` | committed machine-readable task/state JSON | 코드 파일 추가 금지; JSON/README/schema만 허용 |
| `src\` | Windows 앱 본체 | 실제 구현 위치 |
| `cli\` | `cmux.exe` CLI | 실제 구현 위치 |
| `resources\` | 매니페스트, 인스톨러, shell 스크립트 | 실제 구현 위치 |
| `tests\` | 테스트 코드 | 실제 구현 위치 |
| `ports\` | vcpkg overlay ports (libvterm 등) | 실제 구현 위치 |

**핵심 원칙**: Windows 구현 코드는 `cmux\`, `ghostty\`, `_workspace\`, `plans\` 네 경로에 절대 추가하지 않는다.

---

## 밀스톤 순서와 착수 조건

```
M0 (bootstrap + 규약 고정)
  └─ M1 (WinUI app / main window)
       └─ M2 (terminal core / renderer / IME / UIA)
            └─ M3 (split / sidebar / IPC foundation)
                 ├─ M4 (browser panel)
                 │    └─ M5 (CLI / automation / crash pipeline)
                 │              └─ M6 (settings / notifications / shell integration)
                 └─ M7 (release pipeline) — 별도 gate
```

| Milestone | 착수 조건 |
|-----------|-----------|
| M0 | 없음 |
| M1 | M0 완료 |
| M2 | M0, M1 완료 |
| M3 | M1, M2 완료 |
| M4 | M1, M3 완료 |
| M5 | M3, M4 완료 |
| M6 | M3, M5 완료 |
| M7 | 기능 범위 잠금 및 release-only backlog 분리 완료 (M1~M6 모든 검증 기준 통과; 미구현 기능 backlog를 release-only 브랜치로 분리 완료) |

착수 조건을 충족하지 않은 milestone 작업을 먼저 진행하지 않는다.