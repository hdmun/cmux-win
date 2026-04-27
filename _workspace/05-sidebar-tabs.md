# 05. Sidebar and Workspace Tabs

> [!IMPORTANT]
> sidebar는 UI가 아니라 상태 모델의 투영이다. active workspace와 unread 상태의 source of truth는 core model이 가진다.

## 1. workspace model

workspace는 최소 아래 속성을 가진다.

- `workspace_id`
- title
- working directory summary
- branch summary
- unread count
- active flag

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

## 5. 접근성 기준

workspace item은 최소 아래 정보를 UIA에 노출한다.

- title
- active 여부
- unread count
- branch / directory summary

## 6. M3 검증 기준

- active workspace source of truth가 `TabManager`에 고정됨
- batch update가 전체 list rebuild 없이 동작
- close 후 selection 규칙이 일관되게 적용됨
