# 07. Notification

> [!IMPORTANT]
> notification은 unread 상태, XAML ring, Windows toast의 세 층으로 구성한다. toast 실패가 앱 핵심 기능 실패로 번지면 안 된다.

## 1. notification model

`NotificationStore`는 아래를 관리한다.

- `notification_id`
- `workspace_id`
- optional `surface_id`
- title
- body
- created_at
- read state

## 2. unread source of truth

- unread count는 `NotificationStore`가 계산한다.
- sidebar, panel ring, notification page는 projection만 담당한다.

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

## 6. 로그와 개인정보 기준

기본 로그에는 아래만 허용한다.

- notification id
- workspace id / surface id
- action type
- error code

기본 로그에 아래는 남기지 않는다.

- notification body 원문
- 페이지 본문 / terminal 출력 전문

## 7. 보존 및 GC 기본값

- GC 주기: 10분
- read notification 만료: 24시간
- 최대 보관 개수: 200

## 8. M6 검증 기준

- unread count와 ring 상태 동기화
- toast 실패 시 앱 기능 유지
- activation payload parsing이 결정적이고 재현 가능
