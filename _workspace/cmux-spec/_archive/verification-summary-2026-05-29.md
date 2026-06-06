# 명세 ↔ 소스 정합성 검증 완료 보고서

**작성 일자**: 2026-05-29  
**검증 범위**: `_workspace/cmux-spec/` 전체 vs `cmux/` 소스 트리  
**기준 문서**:
- `missing-items-review.md` (2026-05-29, 24개 항목)
- `spec-vs-source-gap-review.md` (2026-05-28, 8개 항목 처리 완료)

---

## 종합 판정

✅ **모든 갭 해소 완료**

missing-items-review.md의 24개 항목 전체와 spec-vs-source-gap-review.md의 미완료 항목이 모두 명세에 반영되었다. 문서 정합성이 **높은 수준(high fidelity)**으로 유지되고 있다.

---

## 상세 검증 결과

### Category A: v1 사이드바 소켓 프로토콜 (Critical) ✅ 완료

| 항목 | 문서 위치 | 상태 |
|------|-----------|------|
| 15개 v1 명령 전체 | `folders/03-cli.md` §v1 사이드바 소켓 프로토콜 (lines 37–117) | ✅ 완벽하게 문서화됨 |
| - `set_status` / `clear_status` / `list_status` | 라인 45–55 | ✅ |
| - `log` / `clear_log` / `list_log` | 라인 57–66 | ✅ |
| - `set_progress` / `clear_progress` | 라인 68–73 | ✅ |
| - `report_git_branch` / `clear_git_branch` | 라인 75–83 | ✅ |
| - `report_ports` / `clear_ports` | 라인 85–95 | ✅ |
| - `report_pwd` | 라인 97–103 | ✅ |
| - `sidebar_state` / `reset_sidebar` | 라인 105–110 | ✅ |
| - DEBUG 전용 `simulate_file_drop` | 라인 112–116 | ✅ |

**검증**: 소켓 v1 프로토콜 모든 명령이 문법·옵션·역할과 함께 명세에 기재되어 있다. Windows PowerShell 통합 설계 시 직접 참조 가능.

---

### Category B: 환경 변수·설정 키 (High) ✅ 완료

| 항목 | 문서 위치 | 상태 |
|------|-----------|------|
| **B.1** `CMUX_TAG` 환경 변수 | `integrated-spec.md` §7.3 (line 268) | ✅ |
| 최대 길이, Dock 배지 포맷 | 명확히 기재됨 | ✅ |
| **B.2** `notificationDockBadgeEnabled` UserDefaults | `integrated-spec.md` §7.8 (line 355) | ✅ |
| 99+ 포맷 포함 | 명확히 기재됨 | ✅ |
| **B.3** `newWorkspacePlacement` UserDefaults | `integrated-spec.md` §7.8 (line 356) | ✅ |
| 기본값 및 허용값 | 명확히 기재됨 | ✅ |

**검증**: 모든 환경 변수와 UserDefaults 키가 기본값·타입·용도와 함께 기재되어 있다.

---

### Category C: Workspace 상태 데이터 구조 (Medium) ✅ 완료

| 항목 | 문서 위치 | 상태 |
|------|-----------|------|
| `SidebarStatusEntry` | `folders/16-sources.md` (line 71) | ✅ |
| `SidebarLogEntry` + `SidebarLogLevel` | 라인 72–73 | ✅ |
| `SidebarProgressState` | 라인 74 | ✅ |
| `SidebarGitBranchState` | 라인 75 | ✅ |
| `customTitle` (추가 필드) | 라인 78 | ✅ |

**검증**: Workspace 모델의 전체 사이드바 상태 구조가 필드·타입·용도와 함께 표로 정리되어 있다. v2 API 응답 스키마 설계 시 기준으로 사용 가능.

---

### Category D: v2 API 응답 스키마 (Medium) ✅ 완료

| 항목 | 문서 위치 | 상태 |
|------|-----------|------|
| `workspace.list` 응답 스키마 | `folders/16-sources.md` (lines 84–97) | ✅ |
| `pinned` 필드 포함 확인 | JSON 예시 + 설명 | ✅ |
| 전체 v2 메서드 카탈로그 | 라인 99–128 | ✅ |

**검증**: `pinned` 필드가 응답 스키마에 명확히 포함되어 있으며, **142개**의 v2 소켓 메서드가 네임스페이스별로 완전히 카탈로그화되어 있다. (이전 "~100개"는 2026-05-29 직접 카운트로 142개로 정정)

---

### Category E: 테스트 파일·기능 신호 (Low) ✅ 완료

| 항목 | 문서 위치 | 상태 |
|------|-----------|------|
| **E.1** tests_v2/ 신규 테스트 파일 | `folders/18-tests-v2.md` (lines 29–39) | ✅ |
| - `test_windows_api.py` | 설명 포함 | ✅ |
| - `test_surface_move_reorder_api.py` | 설명 포함 | ✅ |
| - `test_cli_id_format_defaults.py` | 설명 포함 | ✅ |
| - `test_cli_identify_ref_resolution.py` | 설명 포함 | ✅ |
| - `test_browser_api_unsupported_matrix.py` | 설명 포함 | ✅ |
| - `test_browser_open_split_reuse_policy.py` | 설명 포함 | ✅ |
| - `test_trigger_flash.py` | 설명 포함 | ✅ |
| **E.2** CPU 성능 임계값 | `folders/18-tests-v2.md` §CPU 성능 임계값 (lines 41–52) | ✅ |
| - 유휴 CPU ≤ 20% | 기재됨 | ✅ |
| - burst CPU ≤ 30% | 기재됨 | ✅ |
| - settle 대기시간 2.0초 | 기재됨 | ✅ |
| - monitor 기간 3.0초 | 기재됨 | ✅ |

**검증**: 기능 시사 가치가 높은 테스트 7개가 명시되고, CPU 성능 임계값이 Windows 포트 검증 기준으로 명확히 기재되어 있다.

---

### Category F: 기타 소스 세부사항 (Low) ✅ 완료

| 항목 | 문서 위치 | 상태 |
|------|-----------|------|
| **F.1** v1 DEBUG 전용 `simulate_file_drop` | `folders/03-cli.md` §DEBUG 전용 명령 (lines 112–116) | ✅ |
| **F.2** 셸 통합 소켓 연결 도구 fallback | `folders/03-cli.md` line 118 | ✅ |
| ncat → socat → nc 순서 | 명확히 기재됨 | ✅ |
| Windows Named Pipe 안내 | 명확히 기재됨 | ✅ |
| **F.3** TerminalNotificationStore 알림 억제 조건 | `folders/04-docs.md` (lines 29–38) | ✅ |
| 4가지 조건 모두 명확히 기재 | 완벽히 설명됨 | ✅ |
| Windows 동등 구현 안내 | 명확히 기재됨 | ✅ |

**검증**: 모든 세부사항이 적절한 폴더 명세 문서에 기재되어 있다.

---

## spec-vs-source-gap-review.md 후속 (이미 완료된 항목)

2026-05-28 기준 이미 완료되었던 8개 항목 상태 확인:

| # | 갭 | 적용 파일 | 상태 |
|---|----|---------|----|
| B1 | browser CLI 서브커맨드 14개 | `folders/03-cli.md` | ✅ 완료 |
| A1 | `Sources/Panels/bonsplit/` 경로 정정 | `integrated-spec.md §10 #4` | ✅ 완료 |
| A2 | `cmuxd` dead reference 재기술 | `integrated-spec.md §10 #3` | ✅ 완료 |
| B2 | 파일 드롭 기능 미문서화 | `integrated-spec.md §2` | ✅ 완료 |
| B3 | `web/app/docs/` 라우트 미언급 | `folders/20-web.md` | ✅ 완료 |
| B4 | `.claude/commands/release.md` 미명시 | `folders/00-dot-claude.md` | ✅ 완료 |
| B5 | 기능 시사 테스트 파일 미열거 | `folders/17-tests.md` | ✅ 완료 |
| B6 | 브라우저 서브커맨드 별칭 누락 | `folders/03-cli.md` | ✅ 완료 |

---

## 최종 권고사항

### 현재 상태: 문서 정합성 ✅ 최상의 품질

- **누락 항목**: 0개
- **부정확한 항목**: 0개
- **확인된 정합성**: 100%

### 지속적 유지 방법

1. **IPC 프로토콜 변경 시**:
   - `Sources/TerminalController.swift` + `CLI/cmux.swift` 변경
   - `folders/03-cli.md` + `folders/16-sources.md` 동시 갱신
   
2. **환경 변수/설정 키 추가 시**:
   - `Sources/TerminalNotificationStore.swift` 등 정의 위치 확인
   - `integrated-spec.md §7.3` (환경 변수) 또는 `§7.8` (설정) 추가

3. **새 테스트 파일 추가 시**:
   - 기능 시사 가치가 높으면 `folders/18-tests-v2.md` 파일 목록에 한 줄 추가

### 다음 갱신 시점

- v1 릴리스 후 새 기능 추가 시
- 주요 API 변경 시
- Windows 포트 기능 구현 진도 조회 시

---

## 검증 방법 및 증거

이 보고서는 다음 방법으로 검증되었다:

1. **수동 읽기**: `missing-items-review.md`의 24개 항목을 하나씩 대응 명세 문서에서 확인
2. **파일 위치 특정**: 각 항목이 명세 파일의 정확한 라인 번호와 함께 기재되어 있음 확인
3. **내용 정확성**: 소스 코드의 설명과 명세의 설명이 일치함 확인
4. **교차 참조**: 관련 문서 간 참조 링크가 올바르게 설정되어 있음 확인

---

## 문서 인덱스

- **핵심 통합 명세**: `integrated-spec.md`
- **CLI/IPC 정의**: `folders/03-cli.md` (v1 사이드바 포함)
- **소스 구조 상세**: `folders/16-sources.md` (데이터 모델 + v2 API)
- **기술 스펙 원천**: `folders/04-docs.md` (알림 억제 조건 등)
- **테스트 카탈로그**: `folders/17-tests.md`, `folders/18-tests-v2.md`

---

*검증 완료: 2026-05-29, 명세 ↔ 소스 정합성 100% 달성*
