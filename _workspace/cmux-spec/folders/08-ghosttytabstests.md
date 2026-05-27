# `GhosttyTabsTests`

## 역할 / 목적

Swift 유닛 테스트 타겟. 앱 로직의 단위 검증을 담당하며 `xcodebuild … test`로 실행한다. 호스트 머신에서 직접 실행 가능한 유일한 Swift 테스트다.

## 주요 내용

```
GhosttyTabsTests/
├── CmuxWebViewKeyEquivalentTests.swift    # WKWebView 키 이벤트 동작 테스트
└── UpdatePillReleaseVisibilityTests.swift # 업데이트 UI 표시 조건 테스트
```

현재 파일 수가 적다. 커버리지가 낮은 편이며 e2e 테스트(`tests_v2/`)로 보완된다.

## 저장소 상호작용 / 의존성

- `GhosttyTabs.xcodeproj`의 유닛 테스트 타겟으로 등록된다.
- `Sources/`의 앱 코드를 직접 임포트해 테스트한다.

## 편집 지침

**테스트 코드 전용**. 앱 코드 변경 시 관련 테스트가 있다면 함께 갱신한다. 실행: `xcodebuild -project GhosttyTabs.xcodeproj -scheme cmux -configuration Debug test`.

## 불확실성

없음.
