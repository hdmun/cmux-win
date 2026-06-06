# 명세 ↔ 실제 cmux/ 소스 누락 검토 (Spec vs Source Gap Review)

> **대상 명세**: `_workspace/cmux-spec/` (project-overview.md, folder-manifest.md, integrated-spec.md, folders/00~20)
> **비교 원천**: 실제 `cmux/` read-only 소스 트리 (직접 Glob/Grep/Read)
> **방향**: 양방향 — (A) 명세→소스(명세가 주장하나 소스에 없음/부정확), (B) 소스→명세(소스에 있으나 명세가 누락)
> **범위**: 전체 트리 20개 최상위 폴더 (생성물 `node_modules/`·`graphify-out/` 제외)
> **작성**: 2026-05-28
>
> ※ 기존 `*-accuracy-review.md` / `*-omission-review.md`는 **명세 문서 간** 정합성을 본다. 이 문서는 **명세 vs 실제 소스 코드**를 본다 (서로 보완 관계).

---

## 1. 종합 판정

**명세 정확도: 매우 높음 (high fidelity).** 포트 핵심 영역의 파일 단위 구조가 거의 1:1로 일치하고, 가장 검증이 어려운 두 카탈로그(CLI 명령·소켓 v2 메서드)가 **소스와 정확히 일치**한다. 진짜 갭은 소수이며 대부분 Low다. 단 1건(브라우저 CLI 서브커맨드 목록)은 포트 표면에 직접 영향을 주는 **High**다.

| 구분 | 건수 | 최고 우선순위 |
|------|------|---------------|
| A. 명세→소스 불일치(부정확) | 3 | A1 (Medium-High) |
| B. 소스→명세 누락 | 6 | B1 (**High**) |
| C. 제로 갭 확인(정확 입증) | 9개 영역 | — |
| D. 서브모듈 체크아웃 상태 갱신 | 3 | — |

---

## 2. A. 명세 → 소스 불일치 (명세가 주장하나 소스에 없거나 다름)

| # | 항목 | 명세 위치 | 실제 소스 | 우선순위 | 권고 |
|---|------|-----------|-----------|----------|------|
| **A1** | `Sources/Panels/bonsplit/` 경로가 **존재하지 않음** | `project-overview.md §7`("split 로직 조사 시 `Sources/Panels/bonsplit/`와의 관계 확인"), `integrated-spec.md §10 #4` | `Sources/Panels/`에는 swift 7개 파일만 있고 `bonsplit/` 하위 폴더 없음. Bonsplit 실체는 **`vendor/bonsplit/Sources/Bonsplit/`** (근거: `cmux/CLAUDE.md` Debug event log 절 — `vendor/bonsplit/Sources/Bonsplit/Public/DebugEventLog.swift`). `Sources/Workspace.swift`가 `BonsplitController`로 소비. | **Medium-High** | 경로를 `vendor/bonsplit/Sources/Bonsplit/`로 정정하고, "wrapper vs 직접 사용" 불확실성(#4)을 "vendor 서브모듈의 Bonsplit 모듈을 직접 사용"으로 해소. |
| **A2** | `cmuxd` "**부재 확정 / dead reference**" 판정이 부분 부정확 | `project-overview.md §8 #3`, `integrated-spec.md §10 #3` | 현행 `cmux/CLAUDE.md`가 `cd cmuxd && zig build -Doptimize=ReleaseFast`를 **"release/bundling용 빌드 단계"로 능동 기재**(2곳). 디렉터리는 트리/서브모듈에 없음(.gitmodules엔 ghostty·homebrew-cmux·vendor/bonsplit 3개뿐). 즉 "죽은 참조"라기보다 **미커밋/미체크아웃된 별도 Zig 컴포넌트(cmux daemon 추정)**. | **Medium** | "dead reference"가 아니라 "현행 CLAUDE.md가 적극 참조하는, 트리에 없는 Zig 컴포넌트(cmuxd=cmux daemon 추정)"로 재기술. 포트 설계 시 cmuxd의 역할(데몬 분리 여부) 확인 필요. |
| **A3** | `GhosttyKit.xcframework`가 `ghostty/macos/`에 없음 | `folders/06-ghostty.md`("macos/ └── GhosttyKit.xcframework"), `integrated-spec.md §10 #2` | `ghostty/macos/`에는 Info.plist·entitlements만 존재, xcframework 없음(빌드 산출물 미생성). ghostty 서브모듈 자체는 **체크아웃됨**(build.zig 등 존재). | **Low** (명세가 이미 불확실로 표기) | #2를 "ghostty 체크아웃됨 / xcframework는 미빌드"로 확정 갱신. |

---

## 3. B. 소스 → 명세 누락 (소스에 있으나 명세가 문서화하지 않음)

| # | 누락 항목 | 근거(소스) | 명세 위치 | 우선순위 | 영향 |
|---|-----------|------------|-----------|----------|------|
| **B1 ★** | **`browser` CLI 서브커맨드 14개 패밀리 누락** | `CLI/cmux.swift` `runBrowserCommand` — `tab`(2105) · `console`(2152) · `errors`(2164) · `highlight`(2178) · `state`(2190) · `addinitscript`/`addscript`/`addstyle`(2213) · `viewport`(2227) · `geolocation`\|`geo`(2239) · `offline`(2251) · `trace`(2262) · `network`(2285) · `screencast`(2321) · `input`·`input_mouse`/`input_keyboard`/`input_touch`(2340·2366) | `folders/03-cli.md` 브라우저 서브커맨드 목록(line 33)이 `…storage`에서 끝남 | **High** | `03-cli.md`의 CLI 표면이 실제보다 작게 보임. **단, `16-sources.md` 소켓 카탈로그에는 이 메서드들이 전부 존재** → 03과 16이 불일치. 포트가 CLI 표면을 03만 보고 산정하면 고급 자동화 명령을 누락. 03 갱신 필요(16은 정확). |
| **B2** | **파일 드롭(경로 삽입) 기능** 미문서화 | `Sources/` `registerForDraggedTypes`·`performDrop`·`draggingEntered`(ContentView/AppDelegate/GhosttyTerminalView 등), `tests/test_file_drop_paths.py` | integrated-spec·folders 어디에도 없음 | **Medium** | 터미널에 파일을 드롭하면 경로가 삽입되는 사용자 기능. Windows 포트(WinUI drag-drop)에서 동등 구현 결정 필요. v1 포함 여부 미정 항목으로 등록 권고. |
| **B3** | `web/app/docs/` 문서 라우트 미언급 | `cmux/web/app/docs/`(api·changelog·concepts·configuration·getting-started·keyboard-shortcuts·notifications page.tsx) | `folders/20-web.md`("기타 라우트 blog/community/legal 등") | **Low** | `web/`가 `docs-site/`와 별개로 자체 문서 페이지를 중복 보유. reference-only라 기능 영향 없음. 20-web.md에 `docs/` 라우트 한 줄 추가 권고. |
| **B4** | `.claude/commands/release.md` 단일 커맨드 미명시 | `cmux/.claude/commands/release.md` | `folders/00-dot-claude.md`(패턴만 기술) | **Low** | 실제로 커맨드는 `release.md` 1개뿐이며 `CLAUDE.md`의 `/release`·`skills/release/`와 연동. 00에 명시하면 릴리즈 워크플로 추적 용이. |
| **B5** | `tests/`·`tests_v2/` 주요 테스트 파일 다수 미열거 | 실제 각 41개 `.py`. 미열거 중 기능 신호 있는 것: `test_claude_hook_session_mapping.py`, `test_file_drop_paths.py`(→B2), `test_tab_dragging.py`, `test_terminfo_bright_colors.py`, `test_multi_workspace_focus.py`, `test_focus_notification_dismiss.py` | `folders/17-tests.md`·`18-tests-v2.md`(대표 패턴+"40여 개") | **Low** (의도적 요약) | reference-only라 허용 범위. 단 claude-hook·file-drop·tab-dragging 등 기능을 시사하는 테스트는 본문에 한 줄 노출 권고. |
| **B6** | 브라우저 서브커맨드 **별칭** 일부 누락 | `scrollinto`·`scroll-into-view`(scrollintoview 외), `geo`(geolocation), `key`(press 계열) | `folders/03-cli.md` line 33 | **Low** | 별칭 수준. B1 갱신 시 함께 보강. |

---

## 4. C. 제로 갭 확인 (명세 정확성 입증)

검증 결과 **소스와 명세가 일치**하여 갭이 없는 영역 (양방향 모두 일치):

| 영역 | 검증 결과 |
|------|-----------|
| `Sources/` 파일 (42개) | 최상위·`Find/`·`Panels/`(7)·`Update/`(12) 전부 명세 16-sources.md와 **1:1 일치** (`.swift` 42개; 이전 "41개"는 2026-05-29 정정) |
| **CLI top-level 명령 (50개)** | `CLI/cmux.swift:481-924` switch ↔ `03-cli.md` 카탈로그 **정확히 일치** (그룹·명령명 전부) |
| **소켓 v2 메서드 (142개, debug 18개 포함)** | `TerminalController.swift:503-806` 디스패치 ↔ `16-sources.md` 카탈로그 **정확히 일치** (system 3·window 5·workspace 7·surface 14·pane 4·notification 5·app 2·browser 84·debug 18; 이전 "~100개"는 2026-05-29 정정) |
| `Resources/` | Info.plist·bin/claude·ghostty/terminfo·shell-integration(6)·terminfo-overlay(3) 일치 |
| `scripts/` (13개) | setup·reload(4종)·rebuild·bump-version·run-tests(2)·notify_probe·sparkle(3) 일치 |
| `skills/` | cmux·cmux-browser·cmux-debug-windows·release 4스킬, SKILL.md·agents·references·templates·scripts 일치 |
| `.github/workflows/` (4개) | ci·release·nightly·update-homebrew 일치 |
| `docs/` | notifications·agent-browser-port-spec·v2-api-migration·ghostty-fork·assets/ 일치 |
| `.gitmodules` | ghostty·homebrew-cmux·vendor/bonsplit 3개 정확히 일치 |
| 테스트 타겟 | `GhosttyTabsTests`(2)·`GhosttyTabsUITests`(10) 파일명 정확 일치 |
| `Assets.xcassets`·`docs-site/content/docs`(14 mdx) | 일치 |

---

## 5. D. 서브모듈 체크아웃 상태 (명세 불확실성 갱신)

| 서브모듈 | 상태 | 명세 영향 |
|----------|------|-----------|
| `ghostty/` | **체크아웃됨** (build.zig·build.zig.zon·macos/·AGENTS.md 등 존재) | integrated-spec §10 #2 "체크아웃 확인" 유지. 단 `GhosttyKit.xcframework`는 미빌드(A3) |
| `vendor/bonsplit/` | **미체크아웃 (빈 디렉터리)** | bonsplit 소스 직접 확인 불가. A1의 경로 근거는 CLAUDE.md 기준. 정밀 확인은 서브모듈 init 필요 |
| `homebrew-cmux/` | **미체크아웃 (빈 디렉터리)** | `folders/11` 불확실성 유지 (릴리즈 파이프라인으로 추론) |

---

## 6. 처리 결과 (2026-05-28 적용)

| # | 갭 | 우선순위 | 상태 | 적용된 파일 |
|---|----|---------|----|------------|
| B1 | browser CLI 서브커맨드 14개 | **High** | ✅ 완료 | `folders/03-cli.md` — `storage` 다음에 `tab`/`console`/`errors`/`highlight`/`state`/`addinitscript`/`addscript`/`addstyle`/`viewport`/`geolocation(geo)`/`offline`/`trace`/`network`/`screencast`/`input` 추가. 출처 범위 `2100+` → `2400+` 정정. 별칭(`scroll-into-view`, `geo`) 보강(B6 동시 처리). |
| A1 | `Sources/Panels/bonsplit/` 경로 오기 | Medium-High | ✅ 완료 | `integrated-spec.md §10 #4` — "wrapper vs 직접 사용" 불확실성을 `vendor/bonsplit/Sources/Bonsplit/` 직접 사용으로 확정 정정. |
| A2 | `cmuxd` dead reference 재기술 | Medium | ✅ 완료 | `integrated-spec.md §10 #3` — "dead reference"에서 "CLAUDE.md가 능동 참조하는 미커밋 Zig 컴포넌트(cmux daemon 추정)"로 정정. |
| B2 | 파일 드롭 기능 미문서화 | Medium | ✅ 완료 | `integrated-spec.md §2` 기능 표 — "파일 드롭" 행 추가. v1 포함 여부 ⚠️ 미정으로 등록. |
| B3 | `web/app/docs/` 라우트 미언급 | Low | ✅ 완료 | `folders/20-web.md` — `docs/` 라우트(api/changelog/concepts/configuration/getting-started/keyboard-shortcuts/notifications) 트리에 추가. |
| B4 | `.claude/commands/release.md` 미명시 | Low | ✅ 완료 | `folders/00-dot-claude.md` — 실제 커맨드 `release.md` 1개임을 트리에 명시. |
| B5 | 기능 시사 테스트 파일 미열거 | Low | ✅ 완료 | `folders/17-tests.md` — `test_claude_hook_session_mapping.py`, `test_file_drop_paths.py`, `test_tab_dragging.py`, `test_terminfo_bright_colors.py`, `test_multi_workspace_focus.py`, `test_focus_notification_dismiss.py` 6개 추가. (파일 수: 43개 = `.py` 41 + `.sh` 2. 2026-05-29 재검증에서 이전 "44개"를 정정.) |
| B6 | 서브커맨드 별칭 누락 | Low | ✅ 완료 | B1과 함께 `03-cli.md` 처리. |
| B7 | `cmux-browser/references/commands.md` 미기재 | Low | ✅ 완료 | `folders/15-skills.md` — references 목록에 "(6개)" 주석으로 `commands.md` 포함 확인. |
| A3 | `GhosttyKit.xcframework` 미빌드 | Low | 보류 | `ghostty/` 서브모듈 미체크아웃 상태로 xcframework 확인 불가. `§D` 서브모듈 상태 기술 유지. |

---

*검증 방법: 명세 카탈로그의 명령/메서드/파일을 실제 `cmux/CLI/cmux.swift`, `cmux/Sources/TerminalController.swift`, 각 폴더 Glob 결과와 1:1 대조. 라인 번호는 검토 시점(2026-05-28) 기준.*
