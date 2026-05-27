# `.github`

## 역할 / 목적

GitHub Actions CI/CD 자동화 워크플로 정의 모음. PR 검증, 릴리즈 빌드·공증·배포, 나이틀리 빌드, Homebrew 카스크 자동 갱신을 담당한다.

## 주요 내용

```
.github/
└── workflows/
    ├── ci.yml               # PR CI: 빌드 + 유닛 테스트
    ├── release.yml          # 릴리즈 빌드 → Apple 공증 → DMG → GitHub Release 첨부
    ├── nightly.yml          # 나이틀리 빌드 (새 커밋 감지 기반)
    └── update-homebrew.yml  # 릴리즈 후 Homebrew 카스크 자동 갱신
```

`skills/release/` 폴더의 `SKILL.md`가 릴리즈 에이전트 스킬 문서로 워크플로와 맞물린다.

## 저장소 상호작용 / 의존성

- `release.yml`은 `scripts/bump-version.sh`로 생성된 태그를 트리거로 실행된다.
- `update-homebrew.yml`은 `homebrew-cmux` 서브모듈 저장소(https://github.com/manaflow-ai/homebrew-cmux)를 자동 갱신한다.
- Sparkle appcast 업데이트는 `scripts/sparkle_generate_appcast.sh`와 연동된다.

## 편집 지침

**자동화 전용**. 릴리즈 파이프라인·CI 설정 변경 시만 수정한다. 일반 앱 코드 작업 시 무시해도 된다.

## 불확실성

없음.
