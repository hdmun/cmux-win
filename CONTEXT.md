# cmux-win

cmux-win is the Windows product context for arranging terminal and browser work inside windows, workspaces, panes, and surfaces. This glossary fixes the canonical user-facing nouns used across `_workspace`, ADRs, and protocol documentation without taking over task-state or execution authority.

## Language

### UI structure

**Window**:
A top-level application frame. A **Window** contains one or more **Workspaces** and exposes the app chrome.
_Avoid_: app instance, host

**Workspace**:
A user-visible working context inside a **Window**. A **Workspace** owns a pane layout and the surfaces shown inside it.
_Avoid_: tab, project, session

**Pane**:
A leaf region in a **Workspace** layout. A **Pane** hosts exactly one **Surface** at a time.
_Avoid_: panel, split slot, cell

**Surface**:
The content attached to a **Pane**. In v1, a **Surface** is either a **Terminal Panel** or a **Browser Panel**.
_Avoid_: view, widget

**Terminal Panel**:
A **Surface** that presents an interactive terminal.
_Avoid_: console, shell tab

**Browser Panel**:
A **Surface** that presents web content inside the app.
_Avoid_: webview, browser tab

### App signals

**Notification**:
A user-visible event entry the app may show in-app and, when available, as a Windows toast.
_Avoid_: alert, message

## Flagged ambiguities

- **Pane vs Panel**: Use **Pane** for the layout slot and **Panel** for the concrete kind of content inside that slot. "split pane" is canonical; "terminal pane" is not.
- **Surface vs Panel**: Use **Surface** for the abstract occupant of a **Pane**. Use **Terminal Panel** or **Browser Panel** when naming the concrete type.
- **Workspace vs Window**: A **Window** is the top-level frame. A **Workspace** is the working context inside that frame.

## Example dialogue

**Dev**: "When the user splits the workspace, do we create two panels?"

**Domain expert**: "We create two **Panes** in the **Workspace**. Each **Pane** then hosts one **Surface**."

**Dev**: "So if one side shows a terminal and the other shows a web page, those are two surfaces?"

**Domain expert**: "Yes. More specifically, a **Terminal Panel** in one pane and a **Browser Panel** in the other."

**Dev**: "And a toast for a background task is a pane event?"

**Domain expert**: "No. That is a **Notification**, not a **Pane** or **Surface**."
