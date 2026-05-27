# Integrated Spec Omission Review

> **대상**: `_workspace/cmux-spec/integrated-spec.md`  
> **비교 원천**: `project-overview.md`, `folder-manifest.md`, `folders/*.md` (21개)  
> **작성**: 2026-06 (에이전트 자동 생성)

---

## 1. Verdict

**pass** — 통합 스펙은 충분히 완성도 있으며, Windows 포트 에이전트가 작업을 시작하기에 필요한 모든 핵심 개념을 포함한다. 이하 열거된 항목은 누락이 에이전트를 오도할 수 있는 경우에만 "필수 보완"으로 분류하며, 나머지는 선택적 강화로 처리한다.

---

## 2. Coverage Summary

| 항목 | 커버 여부 | 비고 |
|------|-----------|------|
| 전체 폴더 매트릭스 (21개) | ✅ §3 | `win-relevance` 포함 |
| macOS 아키텍처 다이어그램 | ✅ §2 | 계층·객체 관계 |
| Windows 포트 스택 매핑 | ✅ §2 표 | macOS↔Windows 계층 대응 |
| 빌드 플로우 (macOS+Windows) | ✅ §4 | cmake preset, vcpkg, NuGet |
| 테스트 종류·실행 규칙 | ✅ §4.3 | VM 강제, v1/v2 구분 |
| 릴리즈 파이프라인 (macOS 참조) | ✅ §4.4 | Sparkle, Homebrew |
| 포팅 핵심 주의사항 7개 | ✅ §7 | IPC, 빌드, 셸, 터미널, UI, 업데이트, Intentional Divergences |
| 대표 필독 파일 맵 | ✅ §8 | 루트 파일 + 소스 파일 |
| 저가치·회피 영역 | ✅ §6 | 무시 대상 명시 |
| 미결 불확실성 | ✅ §10 | 8개 항목 |
| v1 제외 항목 목록 | ✅ 부록 | 12개 명시 |
| IPC 프로토콜 세부 (Named Pipe 규격) | ✅ §7.1 | mode·payload·ACL 포함 |
| ConPTY 주의사항 | ✅ §7.4 | passthrough 판정·스레딩·frame handoff |
| reattach_token 패턴 | ✅ §7.4 | split 이동 시 panel 재생성 금지 |
| 셸 통합 환경변수 차이표 | ✅ §7.3 | |
| Intentional Divergences 표 | ✅ §7.5 | 탭 닫기 방향, telemetry 등 |

---

## 3. Missing Coverage Table

아래 항목은 소스 문서에 존재하지만 통합 스펙에서 누락되었다. **Priority** 열은 포트 에이전트에게 미치는 영향도 기준이다.

| # | 누락 항목 | 원천 문서 | Priority | 영향 |
|---|-----------|-----------|----------|------|
| M1 | `skills/cmux-debug-windows/` 스킬 미언급 | `15-skills.md` | **Medium** | Windows 포트 디버깅 전용 스킬이지만 §5(우선순위 읽기 순서)와 §9(폴더 요약)에서 전혀 언급되지 않음. 에이전트가 이 스킬의 존재를 모를 수 있음. |
| M2 | `scripts/notify_probe.sh` 누락 | `14-scripts.md` | Low | 알림 OSC 수동 발송 디버그 유틸. 기능 범위에 영향 없으나 알림 디버깅 워크플로 문서화 누락. |
| M3 | `scripts/reloads.sh` (스테이징 빌드) 누락 | `14-scripts.md` | Low | 스테이징 빌드 전용 reload 스크립트. §4.1의 빌드 명령 표에서 생략됨. 에이전트가 스테이징 환경을 인지하지 못할 수 있음. |
| M4 | `CONTRIBUTING.md`, `LICENSE`, `THIRD_PARTY_LICENSES.md` 누락 | `project-overview.md §5` | Low | project-overview.md §5 "문서·배포·지원 자산" 표에서 명시되지만 통합 스펙 §8 루트 파일 표에 없음. AGPL 의무 사항 확인용. |
| M5 | `Package.swift`, `bun.lock` 루트 파일 표 누락 | `project-overview.md §2` | Low | project-overview.md §2 주요 파일 표에 있으나 통합 스펙 §8 루트 파일 표에서 생략됨. 빌드 경로 이해에 보조적. |
| M6 | `Resources/` 하위 디렉터리 구조 누락 | `13-resources.md` | Low | `bin/`, `ghostty/`, `terminfo-overlay/` 하위 디렉터리가 통합 스펙에서 단순히 "셸 통합 스크립트, terminfo, Info.plist"로만 언급됨. `terminfo-overlay/xterm-ghostty` 항목이 Windows 에이전트에게 불필요한지 명시 필요. |
| M7 | `reload.sh --tag` 격리 효과 설명 누락 | `project-overview.md §4`, `14-scripts.md` | Low | project-overview.md에서 "번들 ID·소켓·DerivedData가 격리되어 병렬 실행 가능"이라고 명시되어 있으나 통합 스펙 §4.1 빌드 플로우에서 생략됨. macOS 개발 가이드 용도이므로 Windows 포트에는 직접 영향 없음. |
| M8 | `docs/ghostty-fork.md` 읽기 우선순위 미분류 | `04-docs.md`, `06-ghostty.md` | Low | `docs/ghostty-fork.md`는 §8 필독 파일 맵에 나열되지 않음. ghostty 서브모듈 upstream 대비 변경사항 파악 시 필요한 1차 참조 문서. |

---

## 4. Optional Additions

현재 통합 스펙에 없지만 향후 에이전트 품질을 높일 수 있는 선택적 강화 사항:

1. **§5 읽기 순서에 `skills/cmux-debug-windows/` 추가** (순위 11번으로)  
   Windows 포트 디버깅 시 참조 스킬 문서로 명시.

2. **§9 폴더 압축 요약 `skills/` 항목 세분화**  
   현재 "cmux-win 스킬 문서 별도 작성"으로만 기술됨. `cmux-debug-windows/` 스킬이 이미 존재함을 명기.

3. **§8 루트 파일 표에 `CONTRIBUTING.md` 행 추가**  
   AGPL 기여 규칙 + 서브모듈 수정 절차 확인용 참조 파일로.

4. **§4.1 macOS 빌드 플로우에 `reloads.sh` 각주 추가**  
   스테이징 빌드 환경의 존재를 macOS 참조 문서로서 명기.

5. **§7 포팅 주의사항에 `terminfo-overlay` 처리 명시**  
   `Resources/terminfo-overlay/xterm-ghostty`는 Windows에서 ConPTY 사용 시 불필요함을 명시 (현재 §6 저가치 영역 표의 `Resources/` 설명에서 이 점이 불명확).

---

## 5. Recommended Follow-up for Next Agent

다음 에이전트가 통합 스펙을 기반으로 작업할 때 권장하는 후속 조치:

1. **M1 즉시 보완**: 통합 스펙 §5 읽기 순서 및 §9 `skills/` 행에 `cmux-debug-windows/` 스킬 언급 추가. 단 1줄 수정이므로 비용 낮음.

2. **§10 불확실성 #7, #8 해소**: parity gap 12개와 partial 항목 9개에 대해 `plans/milestones/`에 task가 있는지 재확인 후 없으면 milestone JSON에 등록.

3. **통합 스펙 §10 불확실성 #3 (`cmuxd/`) 해소**: `ghostty/` 서브모듈 체크아웃 후 `find . -name 'cmuxd' -type d` 1회 실행으로 확인 가능. 이후 §10에서 해당 항목 제거.

4. **M6 `Resources/terminfo-overlay` 포팅 여부 결정**: ConPTY 환경에서 custom terminfo가 필요한지 확인 후 §7 또는 §6에 명시.

5. **이 리뷰 파일은 다음 스펙 갱신 시 체크리스트로 사용**할 수 있다. 보완이 완료된 항목은 해당 행에 `[done]` 표기 후 §10 불확실성에서 제거할 것.
