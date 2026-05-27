# `GhosttyTabsUITests`

## 역할 / 목적

Swift XCTest 기반 UI 테스트 타겟. 실제 macOS 앱을 구동해 사용자 상호작용(키보드 단축키, 사이드바 조작, 알림, 업데이트 UI 등)을 자동화 검증한다. **반드시 UTM 가상머신(`ssh cmux-vm`)에서만 실행**해야 한다.

## 주요 내용

```
GhosttyTabsUITests/
├── AutomationSocketUITests.swift              # 소켓 API 자동화 테스트
├── BrowserOmnibarSuggestionsUITests.swift     # 브라우저 주소창 자동완성
├── BrowserPaneNavigationKeybindUITests.swift  # 브라우저 패인 키바인드
├── CloseWorkspaceCmdDUITests.swift            # Cmd+D 워크스페이스 닫기
├── CloseWorkspaceConfirmDialogUITests.swift   # 워크스페이스 닫기 확인 다이얼로그
├── JumpToUnreadUITests.swift                  # Cmd+Shift+U 미읽음 점프
├── MenuKeyEquivalentRoutingUITests.swift      # 메뉴 키 라우팅
├── MultiWindowNotificationsUITests.swift      # 다중 창 알림 동작
├── SidebarResizeUITests.swift                 # 사이드바 크기 조정
└── UpdatePillUITests.swift                    # 업데이트 알림 UI
```

## 저장소 상호작용 / 의존성

- `GhosttyTabs.xcodeproj`의 UI 테스트 타겟으로 등록된다.
- `Sources/UITestRecorder.swift`가 앱 번들 내 테스트 훅을 제공한다.
- Python e2e 테스트(`tests_v2/`)와 검증 범위가 일부 중복된다.

## 편집 지침

**테스트 코드 전용**. 실행 시 반드시 `ssh cmux-vm`을 통해 UTM 가상머신에서 수행한다. 호스트 머신에서 직접 실행하지 않는다. 앱 UI 변경 시 관련 테스트 업데이트가 필요할 수 있다.

## 불확실성

없음.
