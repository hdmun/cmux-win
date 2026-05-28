# `skills`

## 역할 / 목적

AI 에이전트(Claude Code 등)가 cmux 관련 작업을 수행할 때 참조하는 **에이전트 스킬 문서** 모음. 각 스킬은 에이전트가 특정 도메인(소켓 API 조작, 브라우저 자동화, 릴리즈 등)을 수행하는 방법을 정의한다.

## 주요 내용

```
skills/
├── cmux/                       # cmux 소켓 API 조작 스킬
│   ├── SKILL.md                # 스킬 진입점 및 요약
│   ├── agents/openai.yaml      # 에이전트별 사용 가이드
│   └── references/             # API 레퍼런스 문서
│       ├── handles-and-identify.md
│       ├── panes-surfaces.md
│       ├── trigger-flash-and-health.md
│       └── windows-workspaces.md
├── cmux-browser/               # 브라우저 패인 자동화 스킬
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/             # authentication / commands / proxy-support / session-management / snapshot-refs / video-recording
│   └── templates/              # authenticated-session / capture-workflow / form-automation (.sh)
├── cmux-debug-windows/         # Windows 환경 디버깅 스킬
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── scripts/debug_windows_snapshot.sh
└── release/                    # 릴리즈 절차 스킬
    ├── SKILL.md
    └── agents/openai.yaml
```

## 저장소 상호작용 / 의존성

- `docs/` 폴더의 기술 스펙(특히 `agent-browser-port-spec.md`, `v2-api-migration.md`)을 기반으로 작성된다.
- `CLI/cmux.swift`와 소켓 API v2 프로토콜을 직접 반영한다.
- `cmux-debug-windows/` 스킬은 Windows 포트(`cmux-win`) 개발 지원용이다.

## 편집 지침

**에이전트 지식 베이스**. 앱 API나 CLI 동작이 변경될 때 대응하는 스킬 문서도 함께 갱신해야 에이전트가 올바른 동작을 학습한다. 코드 로직과 직접 연동되지는 않지만 에이전트 작업 품질에 중요하다.

## 불확실성

없음.
