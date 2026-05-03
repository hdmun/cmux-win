# 06. Browser Panel

> [!IMPORTANT]
> browser panel은 WinUI 3 `WebView2` XAML control을 사용한다. child HWND embedding을 기본 경로로 사용하지 않는다.

## 1. 기본 구성

| 요소 | 선택 |
|------|------|
| host | WinUI 3 XAML |
| browser control | WebView2 |
| automation channel | CDP |
| UI composition | XAML tree 안에서 처리 |

## 2. environment 관리

`WebViewEnvironmentPool`을 둔다.

- profile / privacy mode 단위로 environment 재사용
- 최초 warm-up 허용
- panel close 시 environment는 pool에 반환

## 3. browser panel lifecycle

browser panel도 공통 lifecycle을 그대로 따른다.

- `created`
- `attached`
- `focused`
- `blurred`
- `hidden`
- `detached`
- `disposed`

### browser-specific 규칙

1. `hidden` / `detached`에서는 `WebView2` session을 유지한다.
2. split 이동이나 workspace 전환만으로 environment를 다시 만들지 않는다.
3. `disposed`에서만 event token, CDP session, control을 정리한다.

## 4. automation 정책

v1의 browser automation은 CDP 우선이다.

### 규칙

1. `snapshot`, `click`, `fill`, `network` 계열은 CDP 사용
2. 실패 시 조용한 JS fallback을 두지 않음
3. `evaluate`는 명시적 JavaScript API로만 제공

IPC error contract는 `08-ipc-cli.md`의 error code 표를 그대로 사용한다.

## 5. omnibar 규칙

- URL이 스킴 없이 들어오면 기본적으로 `https://` 보정
- 공백이 포함되면 search engine query로 전환
- `Ctrl+L`은 omnibar focus + 전체 선택

### 인라인 자동완성

- 입력 중 히스토리/북마크에서 prefix 일치 항목을 ghost text로 표시
- `Tab`으로 수락, `Backspace`로 취소

### 오픈 탭 제안

omnibar에서 현재 열린 browser panel 목록도 제안 항목에 표시한다.

### 원격 검색 제안

검색 쿼리 입력 시 설정된 검색 엔진에 제안을 요청한다.

- Google, DuckDuckGo, Bing 병렬 지원
- 요청 timeout: 0.65초; timeout 초과 시 제안 생략 (로컬 히스토리만 사용)

## 6. 히스토리 관리

- 히스토리는 JSON으로 `%APPDATA%\cmux\browser-history.json`에 저장
- 최대 보관 항목: **5000개**
- 정렬 기준: frecency score (방문 횟수 + 최근성 가중치)
- 파비콘은 URL별로 캐시

## 7. 페이지 표시 규칙

| 항목 | 규칙 |
|------|------|
| 페이지 줌 | 0.25x ~ 5.0x 범위, `Ctrl++`/`Ctrl+-`/`Ctrl+0` |
| 로딩 최소 표시 시간 | **0.35초** — 즉시 완료되는 페이지에서 진행 표시 flicker 방지 |
| 파비콘 | WebView2 FaviconChanged 이벤트로 업데이트, omnibar와 탭 레이블에 표시 |

## 8. reparenting 규칙

browser panel은 split 이동 시 recreate하지 않는다.

허용:

- XAML parent 변경
- visibility 변경

금지:

- move 중 `EnsureCoreWebView2Async()` 재실행
- detach를 dispose처럼 처리

## 9. M4 검증 기준

- overlay UI와 Z-order 충돌 없음
- CDP unavailable 시 명시적 error 반환
- workspace/split 전환 후 browsing session 유지
- omnibar focus 및 URL normalization 동작
- 히스토리 5000개 초과 시 오래된 항목 자동 삭제
- 원격 검색 제안 timeout 0.65초 준수
- 로딩 최소 표시 시간 0.35초 준수
