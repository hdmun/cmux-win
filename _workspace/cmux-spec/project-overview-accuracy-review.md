# project-overview.md — Factual Accuracy Review

> Reviewer: Copilot (automated)  
> Review date: 2025-07  
> Source: `_workspace/cmux-spec/project-overview.md`  
> Evidence base: `cmux/` directory (read-only), key source files, `.gitmodules`, `CLAUDE.md`, `Package.swift`, `cmuxApp.swift`, `AppDelegate.swift`, `TerminalController.swift`, `Workspace.swift`, `Panels/Panel.swift`

---

## 1. Verdict

**needs-update**

Three factual inaccuracies were found: the app's UI framework is misidentified (AppKit vs SwiftUI), the stated entry-point file is wrong, and `vendor/bonsplit/` is incorrectly classified as a vendored library rather than a git submodule.

---

## 2. Verified Claims

| Claim | Evidence |
|-------|----------|
| Main build path is `GhosttyTabs.xcodeproj`, scheme `cmux` | `CLAUDE.md` xcodebuild command |
| `Package.swift` declares SwiftTerm dependency from: `1.2.0` | `Package.swift` line 13 |
| macOS minimum version is 13 | `Package.swift` `.macOS(.v13)` |
| `ghostty/` is a git submodule at `manaflow-ai/ghostty` fork | `.gitmodules` |
| Ghostty build command: `zig build -Demit-xcframework=true -Doptimize=ReleaseFast` | `CLAUDE.md` |
| Socket path default `/tmp/cmux.sock` | `TerminalController.swift:13` |
| `TerminalController` is a singleton (`static let shared`) | `TerminalController.swift:11` |
| `Panel` is a protocol | `Panels/Panel.swift:12` `public protocol Panel: AnyObject ...` |
| `BonsplitController` is a real class owned by `Workspace` | `Workspace.swift:50` |
| CLI file is `CLI/cmux.swift`, single file ~135 KB | file size 138 799 bytes ≈ 135.5 KB |
| `scripts/` contains `setup.sh`, `reload.sh`, `reloadp.sh`, `run-tests-v1.sh`, `run-tests-v2.sh`, `bump-version.sh` | directory listing |
| `.github/workflows/` contains `ci.yml`, `release.yml`, `nightly.yml`, `update-homebrew.yml` | directory listing |
| `docs/` contains `notifications.md`, `agent-browser-port-spec.md`, `ghostty-fork.md`, `v2-api-migration.md` | directory listing |
| 18 README files (1 default + 17 language variants) | directory listing |
| UI tests and e2e tests must run on VM via `ssh cmux-vm` | `CLAUDE.md` |
| `homebrew-cmux/` is managed by the release pipeline | confirmed by submodule structure and `update-homebrew.yml` |

---

## 3. Accuracy Issues

| # | Claim in overview | Problem | Evidence | Correction |
|---|-------------------|---------|----------|------------|
| A | §1 "Swift/AppKit으로 래핑" (wrapped with Swift/AppKit) | The app is a **SwiftUI** application. `cmuxApp.swift` declares `@main struct cmuxApp: App` (SwiftUI entry point). AppKit is used only as an adapter (`@NSApplicationDelegateAdaptor`). The README's own marketing copy says "Swift and AppKit" but the actual architecture is SwiftUI-primary. | `cmuxApp.swift:5-6`: `@main struct cmuxApp: App`; `cmuxApp.swift:18`: `@NSApplicationDelegateAdaptor(AppDelegate.self)` | Change to "Swift/SwiftUI + AppKit adapter" (or "Swift/SwiftUI+AppKit"). |
| B | §3 핵심 객체 관계 — "`AppDelegate`: 앱 진입점·서비스·키 이벤트 핸들러" | `AppDelegate` is **not** the entry point. The `@main` attribute is on `cmuxApp.swift`. `AppDelegate` is injected as an NSApplicationDelegateAdaptor. Calling it "앱 진입점" is factually wrong. | `cmuxApp.swift:5`: `@main struct cmuxApp: App`; `AppDelegate.swift:135`: `final class AppDelegate: NSObject, NSApplicationDelegate ...` (no `@main`) | Change `AppDelegate` description to "NSApplicationDelegateAdaptor; Finder 서비스·키 이벤트 핸들러 — 진입점은 `cmuxApp.swift`". Also add `cmuxApp.swift` to §2 directory tree and §3 object list. |
| C | §2 tree & §7 — `vendor/bonsplit/` described as "벤더드 Bonsplit 라이브러리" / "벤더드 라이브러리" | `vendor/bonsplit/` is a **git submodule** (`https://github.com/manaflow-ai/bonsplit.git`), not a vendored (copied) library. The distinction matters for update workflow and attribution. | `.gitmodules`: `[submodule "vendor/bonsplit"]` with url `https://github.com/manaflow-ai/bonsplit.git` | Change "벤더드 Bonsplit 라이브러리" → "git 서브모듈: manaflow-ai/bonsplit (스플릿 레이아웃)". Update §7 treatment note accordingly. |

---

## 4. Risky or Weakly-Supported Claims

| # | Claim | Why it is risky | Suggestion |
|---|-------|-----------------|------------|
| R1 | §8 item 3 — "`cmuxd/` 디렉터리가 최상위에 없음. 서브모듈이거나 ghostty 내부일 가능성" | `CLAUDE.md` clearly shows `cd cmuxd && zig build` command but `cmuxd/` does not exist at any visible top-level path in `cmux/`. The submodule list in `.gitmodules` does not include `cmuxd`. The directory may be absent from this repo copy or may live inside the `ghostty` submodule. Already flagged as uncertain but the speculation is still open. | Add a follow-up to check inside `ghostty/` submodule (when checked out) or treat `cmuxd` as a separate repo not embedded here. |
| R2 | §1 "배포: DMG 직접 다운로드, Homebrew Cask (`manaflow-ai/cmux`)" | Homebrew cask tap name inferred; not directly verified against `homebrew-cmux/` formula. | Read `homebrew-cmux/*.rb` (when submodule is checked out) to confirm cask name. |
| R3 | §3 IPC — "짧은 ref(`surface:1`) 기본, UUID는 `--id-format uuids` 옵션으로 선택" | IPC option name `--id-format uuids` was not verified in `TerminalController.swift` within this review. | Grep `TerminalController.swift` for `id-format` / `idFormat` to confirm the flag name. |
| R4 | §4 테스트 — "Swift 유닛 테스트 `GhosttyTabsTests/`" run with `xcodebuild … test` | `GhosttyTabsTests/` directory exists but the exact test command in the table omits the `-destination` and scheme flags shown in `CLAUDE.md`. | Align the command with the full form in `CLAUDE.md`. |
| R5 | §2 tree note — `Package.swift` path `Sources/` = SwiftPM 보조 경로 | `Package.swift` defines `path: "Sources"` but `Sources/` is the main SwiftUI/AppKit app source, not a standalone CLI target. The `CLI/cmux.swift` executable is entirely separate. The "보조/레거시" label is plausible but the structural mismatch is deeper than noted. | Expand section 8 item 1 or section 7 note to explain the path mismatch explicitly. |

---

## 5. Recommended Follow-up for the Next Agent

1. **Fix issue A** — Update the project identity sentence in §1 from "Swift/AppKit으로 래핑" to "Swift/SwiftUI + AppKit adapter로 구현". Check all other occurrences of "AppKit" in the overview for consistency.

2. **Fix issue B** — In §3 object table, change `AppDelegate` entry: remove "앱 진입점", add `cmuxApp.swift` as the actual `@main` entry point. Update §6 read-priority list to add `Sources/cmuxApp.swift` as item 1 or 2.

3. **Fix issue C** — Rename `vendor/bonsplit/` from "벤더드 Bonsplit 라이브러리" to "git 서브모듈 (manaflow-ai/bonsplit)" in both §2 tree and §7 table. Also note that `homebrew-cmux/` is likewise a git submodule.

4. **Resolve R1 (cmuxd)** — Check `ghostty/` submodule contents (when checked out on macOS) for a `cmuxd/` subdirectory. If found there, update §8 item 3. If `cmuxd` is a completely separate repo, clarify that and remove the speculation about it being inside ghostty.

5. **Low-priority** — After confirming, add `scripts/reloads.sh` (STAGING reload) and `scripts/rebuild.sh` to the scripts table in §2 for completeness; they appear in the directory listing but are absent from the overview.
