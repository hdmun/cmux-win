# `docs`

## 역할 / 목적

cmux 앱의 기술 스펙 문서 모음. 개발자·에이전트가 참조하는 내부 API 설계 문서와 포크 노트를 포함한다. `docs-site/`의 공개 사용자 문서와 구별된다.

## 주요 내용

```
docs/
├── notifications.md               # 알림 API 가이드 (OSC 9/99/777, CLI 사용법, 에이전트 훅 패턴)
├── agent-browser-port-spec.md     # 브라우저 포트 스펙 (v1/v2 API 용어 정의: window/workspace/pane/surface)
├── v2-api-migration.md            # 소켓 API v1 → v2 마이그레이션 가이드
├── ghostty-fork.md                # ghostty 포크 diff 노트 (upstream 대비 변경사항)
└── assets/                        # 문서 내 이미지 에셋
```

## 저장소 상호작용 / 의존성

- `CLI/cmux.swift`와 `Sources/TerminalController.swift`의 동작 계약을 정의한다.
- `tests/` 및 `tests_v2/`의 e2e 테스트가 이 스펙을 기준으로 검증한다.
- `ghostty-fork.md`는 `ghostty/` 서브모듈 수정 시 업스트림 diff 추적 근거가 된다.
- Windows 포트(`_workspace/`)의 설계 문서들이 이 문서들을 참조한다.

## 편집 지침

**1차 소스**. IPC API, 알림 시퀀스, 브라우저 포트 동작을 변경할 때는 이 폴더의 관련 문서도 함께 갱신해야 한다. `agent-browser-port-spec.md`는 에이전트가 cmux를 이해하는 데 가장 중요한 문서이다.

## 불확실성

없음.
