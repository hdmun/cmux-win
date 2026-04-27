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

## 6. reparenting 규칙

browser panel은 split 이동 시 recreate하지 않는다.

허용:

- XAML parent 변경
- visibility 변경

금지:

- move 중 `EnsureCoreWebView2Async()` 재실행
- detach를 dispose처럼 처리

## 7. M4 검증 기준

- overlay UI와 Z-order 충돌 없음
- CDP unavailable 시 명시적 error 반환
- workspace/split 전환 후 browsing session 유지
- omnibar focus 및 URL normalization 동작
