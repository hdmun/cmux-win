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

## 10. M6 검증 기준

- unread count와 ring 상태 동기화
- toast 실패 시 앱 기능 유지
- activation payload parsing이 결정적이고 재현 가능
- 동일 (workspace_id, surface_id) 중복 알림 억제 확인
- taskbar badge 카운트 정확성 및 99+ 캡 확인
- suppress 조건 (메인 창 포커스 + 활성 workspace + 활성 surface) 정확히 동작
