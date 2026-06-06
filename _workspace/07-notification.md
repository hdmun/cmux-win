# 07. Notification

> [!IMPORTANT]
> notification은 unread 상태, XAML ring, Windows toast의 세 층으로 구성한다. toast 실패가 앱 핵심 기능 실패로 번지면 안 된다.

## 1. notification model

`NotificationStore`는 아래를 관리한다.

- `notification_id`
- `workspace_id`
- optional `surface_id`
- title
- **subtitle** (optional — toast의 subtitle 라인으로 매핑)
- body
- created_at
- read state

## 2. unread source of truth

- unread count는 `NotificationStore`가 계산한다.
- sidebar, panel ring, notification page는 projection만 담당한다.

### NotificationStore 최소 public interface

```cpp
NotificationId AddNotification(NewNotificationOptions const& opts);
void MarkRead(NotificationId id);
void MarkUnread(NotificationId id);
void ClearNotifications(WorkspaceId workspace_id, std::optional<SurfaceId> surface_id = std::nullopt);
uint32_t GetUnreadCount(WorkspaceId workspace_id) const;
```

### 중복 알림 억제 규칙

동일한 `(workspace_id, surface_id)` 조합으로 새 알림이 추가될 때, 해당 조합의 기존 알림을 먼저 제거한 후 새 알림을 추가한다. 이는 같은 panel의 이전 알림이 쌓이는 것을 방지한다.

## 3. toast 정책

v1의 toast action은 모두 **foreground activation** 으로 고정한다.

배경 COM activation path는 채택하지 않는다.

## 4. payload 규칙

toast payload는 최소 아래 값만 포함한다.

- `notification_id`
- `workspace_id`
- optional `surface_id`
- `action`

## 5. 실패 시 degrade 규칙

- AppNotification 등록 실패: toast만 disable, in-app notifications는 유지
- toast show 실패: 로그 기록 후 계속 진행
- OS 알림 권한 거부 시: Windows 설정 > 알림 페이지로 안내하는 UI를 표시하고 in-app 알림은 유지

## 6. 로그와 개인정보 기준

기본 로그에는 아래만 허용한다.

- notification id
- workspace id / surface id
- action type
- error code

기본 로그에 아래는 남기지 않는다.

- notification body 원문
- 페이지 본문 / terminal 출력 전문

## 7. suppression 규칙

알림 추가 시 아래 조건을 모두 만족하면 in-app 알림을 생성하지 않는다 (suppress).

1. 앱이 **cmux 메인 창 기준으로** 포커스된 상태 (Settings, About 같은 보조 창은 포커스로 간주하지 않음)
2. 해당 workspace가 활성 workspace
3. 해당 surface가 현재 포커스된 surface

이 세 조건 중 하나라도 만족하지 않으면 알림을 생성한다.

`notifications.suppress_when_focused = false`로 설정하면 조건 충족 시에도 항상 알림을 생성한다.

## 8. taskbar badge

unread 알림이 있을 때 taskbar icon에 badge를 표시한다.

| 조건 | 표시 |
|------|------|
| unread > 0 | unread 개수 |
| unread > 99 | `"99+"` |
| `CMUX_TAG` 환경변수 설정 시 | `"<tag>:<count>"` 또는 `"<tag>"` (count=0) |
| unread = 0 | badge 제거 |

Badge 표시는 `BadgeNotification` 또는 taskbar overlay icon으로 구현한다.

## 9. 보존 및 GC 기본값

- GC 주기: 10분
- read notification 만료: 24시간
- 최대 보관 개수: 200

## 10. Notifications page

> macOS `NotificationsPage` 대응. `NotificationStore`(§1)를 투영하는 WinUI 3 page/list view다. 별도 source of truth를 두지 않고 store만 projection한다.

### 10.1 구성

- WinUI 3 page 안의 `ListView`로 알림 항목을 최신순(`created_at` 내림차순)으로 표시한다.
- 항목별 표시 필드:

| 필드 | 출처 | 표시 |
|------|------|------|
| read 상태 | `NotificationStore` | unread는 강조(굵게/점 표시) |
| title | `title` | 1차 라인 |
| subtitle | `subtitle` (optional) | 2차 라인 |
| body | `body` | 본문 (truncate 가능) |
| 시각 | `created_at` | 상대 시간 표기 |
| 출처 | `workspace_id` / optional `surface_id` | workspace/surface 라벨 |

### 10.2 상호작용

| 동작 | 효과 |
|------|------|
| 항목 클릭(jump-to-source) | `MarkRead(id)` 후 해당 `workspace_id`(있으면 `surface_id`)를 activate/focus |
| 항목별 clear | `ClearNotifications(workspace_id, surface_id)` 경로로 제거 |
| 전체 clear | 현재 표시 범위의 알림 제거 (store API 경유) |
| read/unread 토글 | `MarkRead` / `MarkUnread` |

- read 처리, unread count 계산은 모두 `NotificationStore`(§2)가 source of truth다. page는 store 변경을 구독해 projection만 갱신한다.
- jump-to-source의 workspace/surface activate는 `TabManager`/`BonsplitController` 경로를 사용한다 (page가 직접 layout을 조작하지 않음).

### 10.3 수락 hook

- store에 알림 추가 시 page list가 최신순으로 갱신된다.
- unread 항목이 시각적으로 구분되고, 클릭 시 `MarkRead` 후 해당 surface로 jump한다.
- clear 동작이 store에서 제거되고 unread count가 즉시 재계산된다.

## 11. Titlebar notifications popover

> macOS `showNotificationsPopover()` / `NSPopover` 대응. titlebar에 anchored된 flyout으로 최근 알림과 unread 상태를 보여준다.

### 11.1 트리거와 앵커

- open trigger는 titlebar의 notifications 버튼(`_workspace/02-core-app.md`의 titlebar controls)이다. `show_notifications` shortcut action으로도 열 수 있다 (키 매핑은 09 소유).
- flyout은 해당 titlebar 버튼에 anchored된다 (`AppWindowTitleBar` 영역, WinUI `Flyout`/`Popup`).

### 11.2 내용과 상태

- 최근 알림 N개(기본 최신 10개)를 최신순으로 표시한다 (`NotificationStore` projection).
- header에 unread count를 표시한다 (§2 store 계산값, taskbar badge §8과 동일 source).
- "모두 보기" 액션은 Notifications page(§10)로 이동한다.
- popover가 열려 있는 동안 표시된 알림을 read 처리할지는 항목 클릭(jump-to-source) 시에만 `MarkRead`한다. 단순 open만으로는 read 처리하지 않는다.

### 11.3 포커스 복귀

- popover 닫힘(dismiss: light-dismiss/Escape/외부 클릭) 시 포커스를 직전 활성 surface(또는 titlebar 버튼)로 복귀한다.
- popover는 보조 창이 아니므로 §7 suppression의 "메인 창 포커스" 판정에 영향을 주지 않는다.

### 11.4 수락 hook

- titlebar notifications 버튼/`show_notifications` shortcut으로 flyout이 버튼에 anchored되어 열린다.
- header unread count가 store 값과 일치한다.
- 항목 클릭 시 `MarkRead` 후 해당 surface로 jump하고 flyout이 닫힌다.
- dismiss 시 포커스가 직전 surface로 복귀한다.

## 12. M6 검증 기준

- unread count와 ring 상태 동기화
- toast 실패 시 앱 기능 유지
- activation payload parsing이 결정적이고 재현 가능
- 동일 (workspace_id, surface_id) 중복 알림 억제 확인
- taskbar badge 카운트 정확성 및 99+ 캡 확인
- suppress 조건 (메인 창 포커스 + 활성 workspace + 활성 surface) 정확히 동작
- notifications page projection 및 jump-to-source/clear 동작 (§10.3)
- titlebar notifications popover open/dismiss 및 포커스 복귀 동작 (§11.4)
