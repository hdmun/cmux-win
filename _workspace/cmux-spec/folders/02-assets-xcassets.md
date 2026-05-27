# `Assets.xcassets`

## 역할 / 목적

Xcode 이미지 에셋 카탈로그. 앱 아이콘(Debug·Production 구분) 및 기타 UI 이미지 리소스를 포함한다.

## 주요 내용

```
Assets.xcassets/
├── AppIcon-Debug.appiconset/   # Debug 빌드용 앱 아이콘 (식별 구분용)
├── AppIcon.appiconset/         # 프로덕션 앱 아이콘
└── Contents.json               # 에셋 카탈로그 메타데이터
```

Debug/Production 아이콘을 분리해 시스템에서 두 빌드가 동시에 존재할 때 시각적으로 구분 가능하다.

## 저장소 상호작용 / 의존성

- `GhosttyTabs.xcodeproj`의 빌드 설정에서 참조된다.
- `configuration = Debug` 빌드는 `AppIcon-Debug`를 사용하고, Release 빌드는 `AppIcon`을 사용한다.

## 편집 지침

**UI 아이콘·이미지 변경 시만 접근**. 코드 로직 작업과 완전히 무관하다. Xcode의 에셋 카탈로그 편집기를 통해 수정하는 것이 안전하다.

## 불확실성

없음.
