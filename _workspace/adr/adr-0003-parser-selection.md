# ADR-0003: VT Parser Selection

- Status: accepted
- Related docs: `_workspace/03-terminal-engine.md`, `_workspace/11-build-release.md`
- Related tasks: m0-4, m2-2

## Context

터미널 emulator는 VT 시퀀스(ECMA-48, xterm extension)를 해석하는 파서가 필요하다. 주요 옵션은 다음과 같다.

| 옵션 | 언어 | 라이선스 | Windows vcpkg | 비고 |
|------|------|----------|---------------|------|
| **libvterm** | C | MIT | overlay port 가능 | VimR, Neovim, Ghostty 등에서 사용 |
| VTObjectModel (Windows Terminal) | C++ | MIT | 비공식 포트 없음 | Windows Terminal 내부 라이브러리, 별도 배포 없음 |
| xterm.js | JavaScript | MIT | 해당 없음 | Electron/browser 환경 전용 |
| Custom parser | — | — | — | 구현/유지보수 비용 큼 |

**검토 제외 이유**:
- VTObjectModel: Windows Terminal과 빌드 시스템이 강하게 결합되어 있어 분리 추출 비용이 과함
- xterm.js: 브라우저/Node.js 런타임 필요, native C++ 환경에서 직접 호출 불가
- Custom parser: v1 스코프를 초과, 이후 ADR로 재검토 가능

## Decision

**libvterm**을 VT 파서로 선택한다.

### 소스 위치 및 빌드 방식

- authoritative source: `ports/libvterm/` (vcpkg overlay port)
- `vcpkg-configuration.json`의 `overlay-ports`에 `"./ports"` 경로를 등록한다.
- `vendor/libvterm` 등 별도 복사를 금지한다. 패치가 필요하면 overlay port 내에 포함한다.

### 래퍼 계층

- C++ 래퍼 클래스 `VtermWrapper`를 `src/terminal/engine/vterm_wrapper.h`에 정의한다.
- libvterm C API를 직접 호출하는 코드는 이 래퍼 이외의 위치에 두지 않는다.
- `VtermWrapper`의 책임:
  - libvterm 인스턴스 생명주기 관리 (`vterm_new` / `vterm_free`)
  - screen callback 등록 (`vterm_screen_set_callbacks`)
  - `TerminalBuffer` 갱신 (cell/color/cursor 상태)

### v1 제약

v1에서는 custom VT parser를 작성하지 않는다. libvterm이 처리하지 못하는 시퀀스는 무시한다.

## Consequences

- libvterm의 C 헤더가 CMake target에서 public include가 되지 않도록 `VtermWrapper`로 경계를 만든다.
- libvterm 업그레이드는 `ports/libvterm/portfile.cmake`의 `REF`와 `SHA512`만 수정한다.
- 장기적으로 VTObjectModel이나 자체 파서로 교체할 경우, `VtermWrapper` 인터페이스만 재구현하면 된다.

## Verification impact

- M2 수락 기준: `vcpkg install` 후 libvterm overlay port가 정상 빌드됨
- M2 수락 기준: `VtermWrapper`가 기본 VT100 시퀀스(색상, 커서 이동, 지우기)를 `TerminalBuffer`에 올바르게 반영
- M2 수락 기준: libvterm 소스가 `ports/libvterm/` 이외 경로에 복사되지 않음
