# `GhosttyTabs.xcodeproj`

## 역할 / 목적

cmux macOS 앱의 **주 빌드 경로**인 Xcode 프로젝트 정의. 앱 타겟(`cmux`), CLI 타겟, 테스트 타겟(유닛·UI), 빌드 설정, 코드 사이닝, 스킴, 의존성 링킹이 모두 여기에 정의된다.

## 주요 내용

```
GhosttyTabs.xcodeproj/
├── project.pbxproj           # 프로젝트 전체 정의 (소스 파일 목록, 빌드 설정, 타겟, 의존성)
├── project.xcworkspace/      # Xcode 워크스페이스 래퍼
└── xcshareddata/             # 공유 스킴 및 빌드 설정
```

주요 빌드 명령:
```bash
xcodebuild -project GhosttyTabs.xcodeproj -scheme cmux -configuration Debug build
```

## 저장소 상호작용 / 의존성

- `Sources/`, `CLI/`, `GhosttyTabsTests/`, `GhosttyTabsUITests/`의 모든 Swift 소스를 타겟별로 참조한다.
- `Assets.xcassets`, `Resources/`, `cmux.entitlements`, `cmux-Bridging-Header.h`를 빌드 입력으로 사용한다.
- `ghostty/` 서브모듈에서 빌드된 `GhosttyKit.xcframework`를 링크한다.
- `Package.swift`(SwiftPM)는 보조·레거시 경로이며 주 빌드는 이 Xcode 프로젝트다.

## 편집 지침

**Xcode를 통해서만 수정**. `project.pbxproj`를 텍스트 편집기로 직접 수정하면 병합 충돌이 발생하기 쉽다. 새 소스 파일 추가·타겟 설정 변경은 Xcode UI를 사용한다. `.xcodeproj` 내부를 직접 탐색하는 에이전트 작업은 최소화한다.

> **Windows 포트 주의**: 이 프로젝트는 macOS 앱의 주 빌드 경로일 뿐이다. cmux-win은 CMake Presets + vcpkg 경로를 사용하므로, Windows 구현 시 `.xcodeproj`를 빌드 입력으로 삼지 말고 기능 대응 관계만 참고한다.

## 불확실성

없음.
