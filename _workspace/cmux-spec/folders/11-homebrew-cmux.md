# `homebrew-cmux`

## 역할 / 목적

**git 서브모듈** — `manaflow-ai/homebrew-cmux`. cmux의 Homebrew Cask 정의(`Casks/cmux.rb`)를 관리한다. 사용자는 `brew install --cask manaflow-ai/cmux/cmux`로 설치한다.

## 주요 내용

서브모듈 자체는 비어 있거나(체크아웃 안 됨) `Casks/cmux.rb` 파일을 포함한다. `.gitmodules`에서 `https://github.com/manaflow-ai/homebrew-cmux.git`으로 추적.

## 저장소 상호작용 / 의존성

- `.github/workflows/update-homebrew.yml`이 릴리즈 후 이 서브모듈을 자동 갱신한다.
- `scripts/bump-version.sh`로 버전 번프 → 릴리즈 태그 → `release.yml` → `update-homebrew.yml` 순서로 연결된다.

## 편집 지침

**릴리즈 파이프라인이 자동 갱신**. 수동 편집 전 submodule 업데이트 흐름을 먼저 확인한다. 일반 개발 작업 시 무시해도 된다.

## 불확실성

서브모듈이 현재 체크아웃되어 있지 않아 내부 파일 확인 불가. 릴리즈 파이프라인으로 추론.
