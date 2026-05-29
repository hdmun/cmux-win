# `tests`

## 역할 / 목적

소켓 API **v1** 기반 Python e2e 테스트 스위트. 실제 cmux 앱을 실행하고 소켓을 통해 조작해 동작을 검증한다. **반드시 UTM 가상머신(`ssh cmux-vm`)에서 실행**해야 한다.

## 주요 내용

```
tests/
├── cmux.py                              # e2e 테스트 공통 헬퍼 라이브러리 (v1 API)
├── test_notifications.py                # 알림 OSC 시퀀스 테스트
├── test_browser_*.py                    # 브라우저 패인 동작 테스트 (다수)
├── test_nested_split_*.py               # 중첩 스플릿 레이아웃 테스트 (다수)
├── test_shell_zdotdir_*.py              # 셸 통합 zdotdir 회귀 테스트
├── test_sidebar_*.py                    # 사이드바 CWD/git/포트 표시 테스트
├── test_visual_*.py                     # 시각적 렌더링 스크린샷 테스트
├── test_ctrl_*.py                       # Ctrl 키·시그널 테스트
├── test_claude_hook_session_mapping.py  # Claude 훅 세션 매핑 검증
├── test_file_drop_paths.py              # 파일 드롭 경로 삽입 기능 검증
├── test_tab_dragging.py                 # 탭 드래그 UX 검증
├── test_terminfo_bright_colors.py       # terminfo 밝은 색상 처리 검증
├── test_multi_workspace_focus.py        # 멀티 워크스페이스 포커스 검증
├── test_focus_notification_dismiss.py   # 포커스 시 알림 자동 닫힘 검증
└── test_lint_swiftui_patterns.py        # SwiftUI 패턴 린트 검사
```

총 43개 파일 — Python 41개(`cmux.py` 헬퍼 포함) + Shell 스크립트 2개(`test_app_keystrokes.sh`, `test_ctrl_signals.sh`). `scripts/run-tests-v1.sh`로 전체 스위트를 실행한다.

## 저장소 상호작용 / 의존성

- `CLI/cmux.swift`의 v1 소켓 API와 직접 통신한다.
- `Sources/TerminalController.swift`의 v1 프로토콜 구현을 검증한다.
- `tests_v2/`와 일부 테스트 파일이 중복된다 (v2 마이그레이션 중).

## 편집 지침

**레거시 v1 테스트**. 신규 기능 테스트는 `tests_v2/`에 작성한다. v1 전용 동작 회귀 확인 시에만 여기를 참조한다. VM에서만 실행한다: `ssh cmux-vm`, `./scripts/run-tests-v1.sh`.

## 불확실성

v1 소켓 API 폐기 일정이 미정이므로 이 테스트 스위트의 유지 기간도 불명확하다.
