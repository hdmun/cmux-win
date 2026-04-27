# 04. Split Pane

> [!IMPORTANT]
> split layout은 XAML tree 안에서만 구성한다. child HWND 기반 pane tree는 v1에서 사용하지 않는다.

## 1. layout model

`BonsplitController`는 아래를 source of truth로 가진다.

- split tree
- pane order
- pane focus
- layout version

UI는 controller가 내보낸 snapshot만 반영한다.

## 2. snapshot 계약

모든 구조 변경은 `LayoutSnapshot`으로 publish 한다.

- split / close / move / merge
- active pane 변경
- workspace 전환에 따른 root pane 교체

UI는 최신 `layout_version`만 적용한다.

## 3. pane / surface ID 규칙

| 대상 | 의미 |
|------|------|
| `pane_id` | layout node identity |
| `surface_id` | panel instance identity |

pane는 layout의 좌표이고, surface는 실제 표시되는 panel instance다.

## 4. reparenting 규칙

split 조작이나 workspace 전환 시 panel instance를 재생성하지 않는다.

허용:

- container 교체
- visibility 변경
- logical parent 변경

금지:

- move만으로 terminal/browser runtime dispose
- focus 이동 중 panel recreate

## 5. focus 복원 규칙

1. split 직후 새 pane가 focus를 가짐
2. pane close 시 가장 가까운 sibling 우선
3. sibling이 없으면 parent tree의 인접 pane
4. workspace 전환 시 마지막 active pane 복원

## 6. Grid / GridSplitter 규칙

- 화면 구성은 XAML `Grid`
- resize handle은 toolkit `GridSplitter`
- splitter drag는 UI에서 처리하되 최종 ratio source of truth는 controller

## 7. 공통 panel lifecycle 연결

layout 계층은 panel lifecycle을 아래처럼만 호출한다.

- attach
- focus
- blur
- hide
- detach
- dispose

layout code는 terminal/browser-specific cleanup을 직접 실행하지 않는다.

## 8. M3 검증 기준

- split/close/move 후 `layout_version` 일관성 유지
- pane focus 복원 규칙 준수
- panel reparent 시 runtime 유지
- overlay UI가 terminal/browser panel 위에 정상 표시
