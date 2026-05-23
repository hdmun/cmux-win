# Logging / privacy / analytics

## analytics 정책

기본값은 반드시 false.

- 사용자가 **명시적으로 opt-in**해야만 전송
- macOS cmux처럼 RELEASE 빌드에서 자동 전송하지 않는다
- 이를 어기면 개인정보처리방침 위반이다

---

## 로그 redaction 규칙

기본 로그에 아래는 절대 남기지 않는다.

- terminal 출력 전문
- browser DOM / page HTML
- notification body 원문
- 인증 토큰, 쿠키, Authorization 헤더

기록해도 되는 것: error code, notification_id, workspace_id, surface_id, action type.

## 로그 파일 위치 및 rotation

| 항목 | 규칙 |
|------|------|
| file sink | `%LOCALAPPDATA%\cmux\logs\cmux.log` |
| rotation | `cmux.log` + 최대 5개 rolled file, 각 10 MiB 상한 |
| debug sink | Debug 빌드에서 `OutputDebugString` mirror 허용 |
