# `tests_v2`

## 역할 / 목적

소켓 API **v2** 기반 Python e2e 테스트 스위트. `tests/`의 v1 테스트를 대체·확장하는 현행 e2e 테스트다. **반드시 UTM 가상머신(`ssh cmux-vm`)에서 실행**해야 한다.

## 주요 내용

```
tests_v2/
├── cmux.py                              # e2e 테스트 공통 헬퍼 라이브러리 (v2 API)
├── test_browser_api_p0.py               # 브라우저 API P0 핵심 기능 테스트
├── test_browser_api_comprehensive.py    # 브라우저 API 종합 테스트
├── test_browser_api_extended_families.py # 브라우저 API 확장 패밀리
├── test_browser_api_unsupported_matrix.py # 브라우저 미지원 케이스 매트릭스
├── test_browser_cli_agent_port.py       # 브라우저 CLI agent-port 테스트
├── test_cli_id_format_defaults.py       # CLI ID 포맷 기본값 테스트
├── test_cli_identify_ref_resolution.py  # CLI ref 해석 테스트
├── test_surface_move_reorder_api.py     # surface 이동·재정렬 API 테스트
├── test_windows_api.py                  # windows API 테스트
├── test_trigger_flash.py                # flash 트리거 테스트
├── test_nested_split_*.py               # 중첩 스플릿 테스트 (다수)
├── test_notifications.py                # 알림 테스트
├── test_visual_*.py                     # 시각적 렌더링 테스트
└── ...                                  # 기타 40여 개 파일
```

## 저장소 상호작용 / 의존성

- `CLI/cmux.swift`의 v2 소켓 API와 직접 통신한다.
- `Sources/TerminalController.swift`의 v2 프로토콜 구현을 검증한다.
- `docs/v2-api-migration.md`가 v2 API 계약을 정의한다.
- `scripts/run-tests-v2.sh`로 전체 스위트를 실행한다.

## 편집 지침

**현행 e2e 테스트 — 신규 테스트의 기준 위치**. 앱 기능 추가·변경 시 이 폴더에 테스트를 작성한다. 반드시 VM에서 실행: `ssh cmux-vm`, `./scripts/run-tests-v2.sh`.

## 불확실성

없음.
