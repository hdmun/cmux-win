# `Resources`

## 역할 / 목적

macOS 앱 번들에 포함되는 런타임 리소스 파일 모음. 셸 통합 스크립트, terminfo 데이터, 번들 메타데이터가 포함된다.

## 주요 내용

```
Resources/
├── Info.plist                      # 앱 번들 메타데이터 (버전, 번들 ID, 권한 등)
├── bin/
│   └── claude                      # Claude Code 래퍼 스크립트 (cmux CLI 아님)
├── ghostty/
│   └── terminfo/78/xterm-ghostty   # 번들 terminfo
├── shell-integration/              # 셸 통합 스크립트
│   ├── cmux-zsh-integration.zsh    # Zsh 통합 (CWD/git 자동 보고)
│   ├── cmux-bash-integration.bash  # Bash 통합
│   ├── .zshenv / .zprofile         # Ghostty zdotdir 래퍼
│   └── .zlogin / .zshrc            # Ghostty zdotdir 래퍼
└── terminfo-overlay/
    ├── 67/ghostty                  # "ghostty" 터미널 타입 정의
    ├── 78/xterm-ghostty            # "xterm-ghostty" 터미널 타입 정의
    └── README.md
```

> **명세 정정**: `bin/`의 실제 내용은 cmux CLI 복사본이 아니라 **`bin/claude` = Claude Code 래퍼 스크립트**다. 셸 통합이 이 래퍼를 PATH 앞에 주입하여, cmux 터미널 내부(`CMUX_SURFACE_ID` 설정 시)에서 `claude` 실행 시 `--session-id`/`--settings` 플래그를 추가하고 실제 claude를 exec한다. Claude Code 통합 기능 상세는 [integrated-spec.md](../integrated-spec.md) §2를 참조한다.
> **Windows 포트 주의**: ConPTY 환경에서 `terminfo-overlay/`(xterm-ghostty 등)는 일반적으로 불필요하다. Windows 터미널 타입 처리 방침을 별도 결정해야 한다.

## 저장소 상호작용 / 의존성

- `GhosttyTabs.xcodeproj`의 빌드 단계에서 앱 번들로 복사된다.
- `Sources/`의 셸 통합 로직이 이 스크립트들을 실행 중에 참조한다.
- `tests/test_shell_zdotdir_*.py` 등 e2e 테스트가 셸 통합 동작을 검증한다.
- `docs/` 및 `docs-site/content/docs/environment-variables.mdx`에서 셸 통합 환경변수가 문서화된다.

> **Windows 포트 주의**: `shell-integration/`의 현재 스크립트는 zsh/bash 계열 셸 기준이다. cmux-win에서는 이 자산을 직접 재사용하지 않고 PowerShell/CMD(필요 시 WSL 포함)용 동등 스크립트와 환경 주입 규칙을 새로 정의해야 한다.

## 편집 지침

**셸 통합 변경 시 1차 수정 대상**. `cmux-zsh-integration.zsh` 등의 스크립트는 사용자의 셸 환경에 직접 영향을 미친다. 변경 시 반드시 `tests/test_shell_*.py` 테스트를 함께 실행해 회귀를 확인한다. `bin/` 하위 실행 파일과 `shell-integration/` 스크립트는 배포 번들에 직접 들어가는 자산이므로 경로 변경 시 번들 복사 단계도 함께 점검한다.

## 불확실성

없음.
