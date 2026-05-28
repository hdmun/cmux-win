# `.claude`

## 역할 / 목적

Claude Code 에이전트 전용 설정 디렉터리. Claude Code CLI가 자동으로 읽는 커스텀 슬래시 커맨드 정의를 담는다.

## 주요 내용

```
.claude/
└── commands/
    └── release.md   # /release 슬래시 커맨드 — 릴리즈 워크플로 (changelog 갱신, bump-version, tag, push)
```

`commands/` 하위에 Markdown 파일로 커스텀 커맨드를 정의한다. 현재 커맨드는 `release.md` 1개다. Claude Code는 이 디렉터리를 프로젝트 범위 커맨드로 자동 인식하며, `skills/release/`와 연동하여 동작한다.

## 저장소 상호작용 / 의존성

- 코드 로직과 무관하다. 앱 빌드·테스트·배포에 전혀 영향을 주지 않는다.
- 에이전트 작업 효율화를 위한 단축 워크플로를 정의하는 용도로만 쓰인다.

## 편집 지침

**에이전트 설정 전용**. 앱 소스 변경 작업 시 이 폴더는 완전히 무시해도 된다. 새 Claude Code 커맨드를 추가하거나 기존 커맨드를 수정할 때만 접근한다.

## 불확실성

없음.
