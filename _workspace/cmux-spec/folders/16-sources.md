# `Sources`

## 역할 / 목적

**cmux macOS 앱의 핵심 Swift 소스 트리**. SwiftUI + AppKit 어댑터 계층, GhosttyKit 통합, IPC 서버, 탭/워크스페이스 상태 관리, 브라우저 패인, 알림 시스템, 자동 업데이트, 검색 오버레이가 모두 여기에 있다.

## 주요 내용

```
Sources/
├── cmuxApp.swift                  # @main 진입점 (SwiftUI App lifecycle)
├── AppDelegate.swift              # NSApplication delegate: Finder 통합, 서비스 라우팅, 키 이벤트
├── TabManager.swift               # 윈도우 전체 워크스페이스 상태 소유 (CRUD, 선택, 순서)
├── Workspace.swift                # 탭 단위 모델 (BonsplitController + Panel 배열)
├── TerminalController.swift       # Unix 소켓 IPC 서버 (v1/v2 프로토콜 파싱·디스패치)
├── TerminalNotificationStore.swift# OSC 시퀀스 파싱, 알림 상태·읽음 관리
├── GhosttyTerminalView.swift      # Ghostty C API ↔ SwiftUI 브리지
├── GhosttyConfig.swift            # Ghostty 설정 로딩·환경 변수 주입
├── ContentView.swift              # 최상위 UI 레이아웃 (사이드바 + 콘텐츠 영역)
├── WorkspaceContentView.swift     # 워크스페이스 콘텐츠 렌더링
├── PostHogAnalytics.swift         # 운영 분석 이벤트 전송 (opt-in, 프라이버시 경계)
├── SidebarSelectionState.swift    # 사이드바 선택 상태 ObservableObject
├── SocketControlSettings.swift    # 소켓 IPC 설정
├── KeyboardShortcutSettings.swift # 키보드 단축키 설정 모델
├── NotificationsPage.swift        # 알림 패널 UI
├── TerminalView.swift             # 터미널 뷰 컨테이너
├── UITestRecorder.swift           # UI 테스트용 자동화 훅 (앱 번들 포함)
├── WindowAccessor.swift           # NSWindow 접근 SwiftUI 브리지
├── WindowDecorationsController.swift # 창 데코레이션 제어
├── WindowDragHandleView.swift     # 드래그 핸들 뷰
├── WindowToolbarController.swift  # 툴바 제어
├── Backport.swift                 # SwiftUI/AppKit backport 유틸
│
├── Panels/                        # 패인 타입 구현
│   ├── Panel.swift                # Panel 프로토콜 정의
│   ├── PanelContentView.swift     # 패인 타입별 콘텐츠 라우터
│   ├── TerminalPanel.swift        # 터미널 패인 모델
│   ├── TerminalPanelView.swift    # 터미널 패인 SwiftUI 뷰
│   ├── BrowserPanel.swift         # 브라우저 패인 모델 (WKWebView)
│   ├── BrowserPanelView.swift     # 브라우저 패인 UI (주소창, 내비게이션)
│   ├── CmuxWebView.swift          # WKWebView 래퍼 (포커스·단축키 보존)
│   └── SurfaceSearchOverlay.swift # 인터미널 검색 오버레이
│
├── Find/                          # 검색 오버레이 전용 하위 모듈
│   └── SurfaceSearchOverlay.swift # 패널 위 플로팅 검색 UI, 매치 카운터/이동/닫기 처리
│
└── Update/                        # Sparkle 자동 업데이트 서브시스템
    ├── UpdateController.swift
    ├── UpdateViewModel.swift
    ├── UpdateDriver.swift
    ├── UpdateBadge.swift
    ├── UpdatePill.swift
    └── ...
```

## 저장소 상호작용 / 의존성

- `CLI/cmux.swift`와 Unix 소켓 IPC 프로토콜(v1/v2)을 공유한다. `TerminalController.swift`가 서버 측 구현이다.
- `vendor/bonsplit/`(서브모듈)의 레이아웃 엔진을 `Workspace.swift`에서 `BonsplitController`로 사용한다.
- `GhosttyKit.xcframework`를 `GhosttyTerminalView.swift`에서 직접 사용한다.
- `Resources/shell-integration/`의 스크립트들을 실행 중에 참조한다.
- `tests_v2/`의 Python e2e 테스트가 이 코드의 동작을 소켓 API를 통해 검증한다.
- `docs/`의 기술 스펙 문서들이 이 코드의 계약을 정의한다.

> **Windows 포트 주의**: `Sources/`는 가장 중요한 참조 입력이지만, 여기의 AppKit/SwiftUI 구현을 그대로 옮기지는 않는다. 특히 `Find/`, `Panels/`, 창 장식, Ghostty 연동은 Windows 전용 UI/터미널 스택으로 동등 기능을 다시 설계해야 한다.

## 편집 지침

**1차 소스 — 가장 중요한 폴더**. IPC 프로토콜 변경은 `TerminalController.swift` + `CLI/cmux.swift`를 함께 수정한다. `PostHogAnalytics.swift`는 프라이버시 민감 코드이므로 의도하지 않은 수정을 피한다. `UITestRecorder.swift`는 테스트 훅이지만 앱 소스에 포함되므로 주의한다.

## 불확실성

- `vendor/bonsplit/`과 `Sources/` 내 Bonsplit 사용 계층의 정확한 관계(래퍼 vs 직접 사용)는 split 로직 수정 전 별도 확인이 필요하다.
