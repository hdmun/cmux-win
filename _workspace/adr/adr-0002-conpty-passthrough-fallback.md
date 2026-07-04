# ADR-0002: ConPTY Passthrough Detection and Fallback Policy

- Status: accepted (2026-07-04 amended: v1 지원 floor Win11 22H2+ 상향 반영)
- Related docs: `_workspace/03-terminal-engine.md`, `_workspace/00-overview.md`
- Related tasks: m0-4, m2-1

## Context

ConPTY는 두 가지 모드로 동작할 수 있다.

- **standard**: 호환성 우선의 기본 ConPTY 경로
- **passthrough**: Win11 22H2+ (build ≥ 22621)에서 지원되는 성능 최적화 경로로, 복잡한 VT 시퀀스를 raw stream으로 전달한다.

> 2026-07-04 개정: v1 지원 floor가 Windows 11 22H2+로 상향되어 (00 §4) OS build gate는 항상 충족된다. 따라서 **passthrough가 기본 경로**이고, standard는 초기화 실패 폴백과 `CMUX_CONPTY_MODE` override 경로로만 남는다. gate 판정 자체는 방어적 확인 + 진단 로그 목적으로 유지한다.

passthrough 초기화 실패를 에러로 처리하면 다음 문제가 생긴다.

- 사용자에게 불필요한 오류 UI 노출
- 세션 도중 모드 전환 시도 → ConPTY 상태 불일치
- 탐지 로직 중복 → 불일치 위험

## Decision

ConPTY 모드 탐지와 fallback 정책을 아래와 같이 고정한다.

### 탐지 규칙

1. 탐지는 **세션 start 시점에 1회만** 수행한다.
2. 탐지 순서:
   1. `VerifyVersionInfo` / `IsWindowsVersionOrGreater`로 OS build gate를 확인하고 결과를 로그에 남긴다 (지원 floor상 항상 충족 — 방어적 확인).
   2. passthrough 초기화를 기본으로 시도한다.
   3. `CreatePseudoConsole` passthrough 초기화가 실패하면 즉시 `standard`로 고정한다.
3. 결정된 모드는 세션 수명 동안 **재상향(upgrade)하지 않는다**.

### fallback 규칙

- passthrough 미지원은 **에러가 아니라 정상 fallback**이다.
- fallback 발생 시 로그 레벨 `INFO`로 기록한다. `WARN` 이상을 사용하지 않는다.
- 사용자에게 팝업/배너/토스트 등 UI를 띄우지 않는다.

### 모드 노출

- 현재 모드(`standard` / `passthrough`)는 IPC `session_info` 응답의 `pty_mode` 필드로 노출한다.
- 진단 목적 외에 애플리케이션 로직이 모드를 분기하지 않는다.

## Consequences

- `ConPtySessionManager` 또는 이에 상당하는 클래스가 탐지 결과를 **싱글턴 또는 세션 컨텍스트 필드**로 캐시한다.
- 테스트 환경에서 모드를 강제(override)할 수 있도록 `CMUX_CONPTY_MODE` 환경 변수를 지원한다 (`standard` 또는 `passthrough`).
  - 이 변수는 테스트 전용이며, production build에서도 기술적으로 동작하지만 문서화된 지원 경로가 아니다.

## Verification impact

- M2 수락 기준: 기본 경로에서 passthrough 초기화 성공 + gate 판정 로그 존재
- M2 수락 기준: passthrough 초기화 실패 시 오류 UI 없이 standard 모드로 폴백 (INFO 로그)
- M2 수락 기준: `CMUX_CONPTY_MODE=standard` 오버라이드 시 gate 무시하고 standard 동작
