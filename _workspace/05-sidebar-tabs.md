# 05. Sidebar and Workspace Tabs

> [!IMPORTANT]
> sidebar는 UI가 아니라 상태 모델의 투영이다. active workspace와 unread 상태의 source of truth는 core model이 가진다.

## 1. workspace model

workspace는 최소 아래 속성을 가진다.

- `workspace_id`
- title
- working directory summary
- branch summary (branch name + dirty flag)
- unread count
- active flag

### IPC 경유 sidebar 메타데이터

IPC를 통해 workspace에 추가로 전달되는 rich 메타데이터다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `status_entries` | `map<string, SidebarStatusEntry>` | key-value 상태 항목 (AI agent 상태 등) |
| `log_entries` | `SidebarLogEntry[]` | 로그 스트림 (최신 N개 유지) |
| `progress` | `SidebarProgressState?` | 진행률 바 (null이면 숨김) |
| `git_branch` | `SidebarGitBranchState?` | branch name + isDirty |
| `listening_ports` | `int[]` | shell이 listen 중인 포트 목록 |

이 필드들은 shell auto-report 또는 claude-hook 명령을 통해 갱신된다. UI는 projection만 담당한다.

## 2. ID 및 선택 규칙

- `workspace_id` 형식은 `workspace:<uuid>`
- active workspace는 `TabManager`가 유일하게 보유
- `ListView.SelectedItem`은 결과를 반영할 뿐 source of truth가 아님

### `TabManager` 최소 public interface

```cpp
class TabManager {
public:
    std::vector<WorkspaceState> ListWorkspaces() const;
    WorkspaceId GetActiveWorkspaceId() const;
    std::optional<WorkspaceState> GetWorkspace(WorkspaceId workspace_id) const;

    WorkspaceId CreateWorkspace(NewWorkspaceOptions const& options);
    bool ActivateWorkspace(WorkspaceId workspace_id);
    CloseWorkspaceResult CloseWorkspace(WorkspaceId workspace_id);

    void ApplyWorkspaceMetadata(WorkspaceId workspace_id, WorkspaceMetadataUpdate const& update);
    void SetUnreadCount(WorkspaceId workspace_id, uint32_t unread_count);
};
```

> **구현 참고**: `SetUnreadCount`는 TabManager 외부에서 접근하는 단일 진입점이다. 내부적으로는 `NotificationStore`가 unread 상태의 source of truth를 보유하며, TabManager는 sidebar projection에 필요한 카운트를 전달받는 라우팅 역할을 한다.
```

이 스케치는 sidebar selection, workspace lifecycle, IPC routing이 같은 최소 contract를 공유하도록 하기 위한 것이다.

## 3. sidebar update batching

메타데이터 업데이트는 batch 적용한다.

- 기본 batch window: 100ms
- 최대 UI 반영 지연: 250ms
- unread / active 상태는 일반 메타데이터보다 우선

## 4. workspace lifecycle

1. create
2. activate
3. deactivate
4. close-requested
5. closed

### close 선택 규칙

workspace close 후 다음 active 선택은 아래 순서를 따른다.

1. 왼쪽 인접 항목
2. 오른쪽 인접 항목
3. 남은 항목이 없으면 window 종료 경로

> **참고**: macOS cmux는 오른쪽 우선(`min(index, count-1)`) 방식을 사용하지만, Windows 포트는 왼쪽 우선을 명시적 설계 결정으로 채택한다.

## 5. v1 범위 결정

아래 기능은 macOS cmux에 구현되어 있으나 v1 Windows 포트에서는 **의도적으로 제외**한다. 향후 milestone에서 추가할 수 있다.

| 기능 | 사유 |
|------|------|
| 탭 히스토리 back/forward (max 50) | v1 MVP 범위 초과 |
| 워크스페이스 핀 고정 (`isPinned`) | v1 MVP 범위 초과 |
| 새 탭 삽입 위치 설정 (top/afterCurrent/end) | v1 MVP 범위 초과 |
| 창 간 workspace/surface detach·attach | v1 MVP 범위 초과 |
| Cmd+숫자(1~9) workspace 단축키 | v1 MVP 범위 초과 |

## 6. 접근성 기준

workspace item은 최소 아래 정보를 UIA에 노출한다.

- title
- active 여부
- unread count
- branch / directory summary

## 7. M3 검증 기준

- active workspace source of truth가 `TabManager`에 고정됨
- batch update가 전체 list rebuild 없이 동작
- close 후 selection 규칙이 일관되게 적용됨
