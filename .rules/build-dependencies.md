# 빌드 & 의존성

## 공식 빌드 경로

v1의 공식 개발/CI 빌드 경로는 아래 하나로 고정한다.

- **Visual Studio 2022**
- **CMake Presets**
- **vcpkg manifest mode**
- **NuGet central package management**
- **Windows App SDK bootstrap**

### 표준 명령

```powershell
cmake --preset dev-x64
cmake --build --preset dev-x64
ctest --preset dev-x64 --output-on-failure

cmake --preset dev-arm64
cmake --build --preset dev-arm64
ctest --preset dev-arm64 --output-on-failure
```

"Visual Studio 수동 프로젝트"나 별도 NuGet restore 흐름은 공식 경로가 아니다.

---

## 의존성 pinning 규칙

버전과 restore의 단일 출처 파일은 아래다. **문서에 버전 문자열을 중복해 적지 않는다.**

| 파일 | 역할 |
|------|------|
| `CMakePresets.json` | configure/build/test 진입점 |
| `vcpkg.json` | vcpkg 의존성 manifest |
| `vcpkg-configuration.json` | baseline / registries / overlay 설정 |
| `Directory.Packages.props` | NuGet 패키지 pinning |
| `NuGet.config` | NuGet 소스 정책 |

### 의존성 소유권

| 의존성 | 관리 방식 | authoritative 위치 |
|--------|-----------|---------------------|
| libvterm | vcpkg overlay port | `ports\libvterm\` + `vcpkg.json` |
| nlohmann-json | vcpkg | `vcpkg.json` |
| gtest | vcpkg | `vcpkg.json` |
| Microsoft.Windows.CppWinRT | NuGet | `Directory.Packages.props` |
| Windows App SDK | NuGet | `Directory.Packages.props` |
| WebView2 SDK | NuGet | `Directory.Packages.props` |
| CommunityToolkit controls | NuGet | `Directory.Packages.props` |

### vendor 금지 정책

- 임시 zip vendor copy 금지
- `vendor\libvterm` 같은 별도 복사 금지 — libvterm은 반드시 `ports\libvterm\`만 사용
- 로컬 전역 설치 버전에 의존하는 빌드 금지
- pin 파일에 없는 패키지 버전 참조 금지
- 예외가 필요하면 ADR과 빌드 재현 문서를 먼저 작성