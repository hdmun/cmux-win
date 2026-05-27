# `scripts`

## 역할 / 목적

빌드·개발·테스트·릴리즈 운영을 위한 Shell 스크립트 모음. 로컬 개발 루프에서 가장 빈번하게 사용하는 스크립트들이 여기에 있다.

## 주요 내용

```
scripts/
├── setup.sh                        # 최초 환경 설정: 서브모듈 초기화 + GhosttyKit 빌드
├── reload.sh                       # Debug 앱 종료 후 재시작 (--tag 필수)
├── reload2.sh                      # Debug + Release 모두 재시작
├── reloadp.sh                      # Release 앱 재시작
├── reloads.sh                      # 스테이징 빌드 재시작 ("cmux STAGING")
├── rebuild.sh                      # 전체 재빌드 보조
├── bump-version.sh                 # 버전 번프 (MARKETING_VERSION, BUILD_NUMBER) + CHANGELOG 갱신
├── run-tests-v1.sh                 # Python e2e 테스트 v1 실행 (VM 필요)
├── run-tests-v2.sh                 # Python e2e 테스트 v2 실행 (VM 필요)
├── notify_probe.sh                 # 알림 OSC 시퀀스 수동 발송 유틸
├── sparkle_generate_keys.sh        # Sparkle 서명 키 생성
├── sparkle_generate_appcast.sh     # Sparkle appcast XML 생성
└── derive_sparkle_public_key.swift # Sparkle 공개 키 추출 Swift 유틸
```

## 저장소 상호작용 / 의존성

- `setup.sh`는 `ghostty/` 서브모듈과 `GhosttyKit.xcframework` 빌드에 의존한다.
- `bump-version.sh`는 `GhosttyTabs.xcodeproj`의 버전 번호와 `docs-site/content/docs/changelog.mdx`를 갱신한다.
- `run-tests-*.sh`는 `tests/` 및 `tests_v2/`의 Python 테스트를 VM 환경에서 실행한다.
- Sparkle 스크립트들은 `.github/workflows/release.yml`과 연동된다.

## 편집 지침

**개발 워크플로의 핵심**. `CLAUDE.md`를 먼저 읽어 각 스크립트의 정확한 사용법과 옵션을 숙지한다. `reload.sh`는 항상 `--tag` 옵션과 함께 사용해야 번들 ID·소켓이 격리된다.

## 불확실성

없음.
