# 11. Build and Release

> [!IMPORTANT]
> 이 문서는 구현 착수 전에 고정해야 하는 **유일한 Windows 부트스트랩 경로** 를 정의한다. 다른 빌드 경로를 병행 문서화하지 않는다.

## 1. 유일한 부트스트랩 경로

v1의 공식 개발/CI 경로는 아래 하나다.

- **Visual Studio 2022**
- **CMake Presets**
- **vcpkg manifest mode**
- **NuGet central package management**
- **Windows App SDK bootstrap**

즉, "Visual Studio 수동 프로젝트" 또는 "별도 hand-written NuGet restore 흐름"은 공식 경로가 아니다.

## 2. authoritative build files

아래 파일이 버전과 restore의 단일 출처다.

| 파일 | 역할 |
|------|------|
| `CMakePresets.json` | configure/build/test entrypoint |
| `vcpkg.json` | vcpkg dependency manifest |
| `vcpkg-configuration.json` | baseline / registries / overlay 설정 |
| `Directory.Packages.props` | NuGet package pinning |
| `NuGet.config` | NuGet source 정책 |

문서에 버전 문자열을 중복해 적지 않는다. **실제 pin은 위 파일이 책임진다.**

## 3. dependency ownership

| 의존성 | 관리 방식 | authoritative location |
|--------|-----------|------------------------|
| libvterm | vcpkg overlay port | `ports\libvterm\` + `vcpkg.json` |
| nlohmann-json | vcpkg | `vcpkg.json` |
| gtest | vcpkg | `vcpkg.json` |
| Microsoft.Windows.CppWinRT | NuGet | `Directory.Packages.props` |
| Windows App SDK | NuGet | `Directory.Packages.props` |
| WebView2 SDK | NuGet | `Directory.Packages.props` |
| CommunityToolkit controls | NuGet | `Directory.Packages.props` |

## 4. vendor 금지 정책

아래는 기본적으로 금지한다.

- 임의 zip vendor copy
- 개발자 로컬 전역 설치 버전에 의존하는 빌드
- 문서에만 있고 pin file에 없는 package 버전

## 5. configure/build/test 명령

M0 이후 모든 개발자와 CI는 아래 명령만 사용한다.

```powershell
cmake --preset dev-x64
cmake --build --preset dev-x64
ctest --preset dev-x64 --output-on-failure
```

ARM64는 동일한 패턴으로 `dev-arm64` preset을 사용한다.

## 6. M0 산출물

M0-1과 M0-2가 끝나면 최소 아래가 준비되어야 한다.

- root `CMakeLists.txt`
- `CMakePresets.json` (`dev-x64`, `dev-arm64`, `ci-x64`, `ci-arm64`)
- `vcpkg.json`
- `vcpkg-configuration.json`
- `Directory.Packages.props`
- `NuGet.config`
- `ports\libvterm\`

## 7. 패키징 모델

v1 배포 경로는 아래로 고정한다.

- unpackaged desktop app
- Windows App SDK bootstrap on launch
- Inno Setup installer
- WebView2 Evergreen runtime prerequisite

MSIX는 연구/후속 단계일 수 있으나 v1 release gate는 아니다.

## 8. CI 원칙

CI는 아래만 보장한다.

- x64 / ARM64 configure
- build
- tests
- vcpkg binary caching

release signing / installer publishing은 M7 단계로 분리한다.

## 9. release 인프라 분리

아래 항목은 기능 착수 문서와 분리된 release readiness 항목이다.

- Azure Trusted Signing
- `winget`
- `scoop`
- updater / appcast
- symbol upload / crash ingestion backend

이 항목들은 M7 전용 gate로 다룬다. machine-readable release state는 `plans\milestones\m7.json`이 소유한다.

## 10. 실패 정책

- restore 실패를 숨기지 않는다
- bootstrap prerequisite 누락 시 즉시 fail
- 부분 설치 상태를 성공처럼 취급하지 않는다

## 11. M0 / M7 검증 기준

### M0

- 새 환경에서 문서 한 곳만 보고 configure/build/test 가능
- dependency pinning 위치가 중복 없이 명확함
- libvterm overlay port 경로가 고정됨

### M7

- signing 경로가 CI에서 재현 가능
- installer가 WinAppSDK/WebView2 prerequisite를 검증
- release artifact와 symbol upload가 분리되어 관리됨
- `plans\milestones\m7.json`의 task 상태와 acceptance가 release backlog와 모순되지 않음
