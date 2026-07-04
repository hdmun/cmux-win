# 15. Scaffolding Guide

> [!IMPORTANT]
> 완전 자율 구현을 위해 M0에서 생성해야 하는 starter file과 최소 skeleton을 이 문서에서 고정한다.

## 1. target bootstrap outputs

| 경로 | 최소 역할 |
|------|-----------|
| `CMakeLists.txt` | 최상위 configure entrypoint |
| `CMakePresets.json` | `dev-x64`, `dev-arm64`, `ci-x64`, `ci-arm64` presets |
| `src/CMakeLists.txt` | 앱/라이브러리 target 집합 정의 |
| `src/app/cmux_app.vcxproj` | WinUI 3 앱 셸 vcxproj (11 §1.1 하이브리드 계약) |
| `cli/CMakeLists.txt` | `cmux.exe` target 정의 |
| `resources/app.manifest` | DPI awareness, compatibility, bootstrap manifest |
| `Directory.Packages.props` | NuGet pinning |
| `NuGet.config` | NuGet source 정책 |
| `vcpkg.json` | vcpkg manifest |
| `vcpkg-configuration.json` | baseline / overlay 설정 |

## 2. canonical target names

초기 target 이름은 아래를 사용한다.

| target | 의미 |
|--------|------|
| `cmux_app` | WinUI 3 app binary — vcxproj(`src/app/cmux_app.vcxproj`)를 msbuild로 호출하는 CMake custom target (11 §1.1) |
| `cmux_cli` | `cmux.exe` CLI |
| `cmux_core` | 공유 core/model 라이브러리 |
| `cmux_terminal` | terminal runtime 계층 |
| `cmux_ipc` | IPC/runtime 계층 |
| `cmux_tests` | test aggregate target |

## 3. directory bootstrap rule

초기 scaffold는 최소 아래 디렉터리를 만든다.

```text
src\
├─ app\
├─ core\
├─ panels\
├─ terminal\
├─ ui\
├─ ipc\
├─ notification\
├─ config\
└─ utils\
```

빈 디렉터리만 만들고 끝내지 않는다. 각 계층에는 CMake가 인식할 최소 anchor file 또는 하위 `CMakeLists.txt`가 있어야 한다.

## 4. namespace rule

초기 C++/WinRT namespace는 아래를 기본으로 사용한다.

- root namespace: `cmux`
- app/ui 계층: `cmux::app`, `cmux::ui`, `cmux::panels`
- runtime 계층: `cmux::terminal`, `cmux::ipc`, `cmux::notification`, `cmux::config`

namespace 결정이 바뀌면 `_workspace/02`, `03`, `04`, `08`, `11`, `12`를 함께 갱신한다.

## 5. bootstrap completion checklist

M0-1/M0-3가 끝났다고 판단하기 전에 아래를 충족해야 한다.

1. `cmake --preset dev-x64`
2. `cmake --build --preset dev-x64`
3. `ctest --preset dev-x64 --output-on-failure`
4. target 이름과 디렉터리 구조가 이 문서와 일치
5. manifest/resource skeleton이 `11-build-release.md`와 충돌하지 않음

## 6. anti-patterns

아래는 허용하지 않는다.

- target 이름을 세션마다 다르게 정하는 것
- stub file 없이 CMake만 통과하도록 빈 target을 만드는 것
- `_workspace` 문서에 없는 임의의 부트스트랩 경로를 추가하는 것
