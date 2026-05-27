# `vendor`

## 역할 / 목적

외부 git 서브모듈의 관리 루트. 현재 `bonsplit` 하나만 포함한다.

## 주요 내용

```
vendor/
└── bonsplit/     # git 서브모듈: manaflow-ai/bonsplit — 스플릿 패인 레이아웃 엔진
```

`bonsplit`은 cmux의 수평/수직 패인 분할 레이아웃 알고리즘을 제공하는 전용 라이브러리다. `Workspace.swift`에서 `BonsplitController`로 사용된다.

## 저장소 상호작용 / 의존성

- `.gitmodules`에서 `https://github.com/manaflow-ai/bonsplit.git`으로 추적.
- `Sources/Workspace.swift`가 `BonsplitController`를 통해 이 라이브러리를 소비한다.
- `GhosttyTabs.xcodeproj`가 이 서브모듈의 소스를 링크하거나 프레임워크로 빌드한다.
- `scripts/setup.sh`가 서브모듈 초기화를 담당한다.

## 편집 지침

**직접 수정 최소화**. 스플릿 레이아웃 버그·기능 추가는 `manaflow-ai/bonsplit` 저장소에 별도 PR로 반영한 뒤 서브모듈 포인터를 업데이트한다. 스플릿 동작 조사 시 `Sources/Workspace.swift`와 이 서브모듈 양쪽을 함께 확인한다.

## 불확실성

`Sources/` 내에서 bonsplit을 직접 사용하는 계층(래퍼 vs 직접 import)이 명확히 문서화되어 있지 않다. 수정 전 코드를 직접 확인한다.
