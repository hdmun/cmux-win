# 01. Project Structure

> [!IMPORTANT]
> 이 문서는 Windows 구현이 들어갈 실제 저장소 구조와 기존 `cmux\` 참조 코드의 관계를 고정한다.

## 1. 최상위 원칙

1. `cmux\`는 **read-only reference tree** 다.
2. Windows 구현 파일은 루트 기준 새 디렉터리에만 추가한다.
3. 새 구현과 참조 구현을 1:1 파일 매핑하려 하지 않는다.
4. 플랫폼 종속 계층과 core model을 명확히 분리한다.

## 2. 역할별 디렉터리

```text
cmux-win\
├─ CMakeLists.txt
├─ CMakePresets.json
├─ Directory.Packages.props
├─ NuGet.config
├─ vcpkg.json
├─ vcpkg-configuration.json
├─ ports\
│  └─ libvterm\
├─ src\
│  ├─ app\
│  ├─ core\
│  ├─ panels\
│  ├─ terminal\
│  ├─ ui\
│  ├─ ipc\
│  ├─ notification\
│  ├─ config\
│  └─ utils\
├─ cli\
├─ resources\
├─ tests\
├─ _workspace\
├─ cmux\      (reference only)
└─ ghostty\   (legacy/reference subtree, not a Windows implementation target)
```

## 3. 참조 트리와 새 트리의 관계

| 경로 | 역할 | 수정 정책 |
|------|------|-----------|
| `cmux\Sources\...` | UX / behavior reference | Windows 구현을 위해 직접 수정하지 않음 |
| `cmux\CLI\...` | 기존 CLI 흐름 참고 | 직접 포팅 금지, 구조만 참조 |
| `ghostty\...` | legacy/upstream reference assets | Windows 구현을 위해 직접 수정하지 않음 |
| `src\...` | Windows app 본체 | 실제 구현 위치 |
| `cli\...` | `cmux.exe` | 실제 구현 위치 |
| `ports\libvterm\` | overlay port | 버전 및 patch의 유일한 관리 위치 |

## 4. 허용되는 의존성 배치 규칙

| 유형 | 위치 | 비고 |
|------|------|------|
| vcpkg 의존성 | `vcpkg.json` | manifest mode |
| overlay ports | `ports\` | 기본 경로 |
| NuGet packages | `Directory.Packages.props` | central package management |
| installer assets | `resources\installer\` | Inno Setup 포함 |
| shell scripts | `resources\shell-integration\` | PowerShell/CMD/WSL |
| 임시 vendor copy | 금지 | 예외 시 ADR 필요 |

### vendor 사용 규칙

`vendor\`는 기본 경로가 아니다. 아래 두 조건을 모두 만족할 때만 허용한다.

1. overlay port 또는 NuGet/MSBuild restore로 해결할 수 없음
2. 별도 ADR과 빌드 재현 문서가 존재함

## 5. 플랫폼 계층 분리

| 레이어 | 예시 | 원칙 |
|--------|------|------|
| app/ui | `src\app`, `src\ui`, `src\panels` | WinUI 3 / XAML 종속 가능 |
| core model | `src\core` | UI framework에 직접 의존하지 않음 |
| runtime | `src\terminal`, `src\ipc`, `src\notification`, `src\config` | Win32 / WinRT API는 허용하되 UI와 느슨하게 연결 |
| tools | `cli\`, `tests\` | app과 별도 빌드 가능해야 함 |

## 6. 필수 파일 산출물

M0 종료 시 아래 파일이 저장소에 존재해야 한다.

- `CMakeLists.txt`
- `CMakePresets.json`
- `Directory.Packages.props`
- `NuGet.config`
- `vcpkg.json`
- `vcpkg-configuration.json`
- `ports\libvterm\...`
- `src\CMakeLists.txt`
- `cli\CMakeLists.txt`
- `resources\app.manifest`

## 7. 코드 추가 금지 구역

아래 위치에는 Windows 구현 코드를 추가하지 않는다.

- `cmux\`
- `ghostty\`
- `_workspace\`

`_workspace\`는 계획 문서 전용이다.

## 8. 문서 갱신 규칙

저장소 구조가 바뀌면 최소 아래 세 문서를 동시에 갱신한다.

- `01-project-structure.md`
- `11-build-release.md`
- `12-tasks.md`
