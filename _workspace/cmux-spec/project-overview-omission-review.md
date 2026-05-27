# project-overview.md — Omission Review

> Reviewer: Copilot agent  
> Input: `_workspace/cmux-spec/project-overview.md`  
> Source inspected: `cmux/` tree (read-only)  
> Date: 2025-07

---

## 1. Verdict

**needs-update**

The overview is structurally sound and covers the major areas well. However, seven meaningful omissions were found spanning root files, architecture roles, build/tooling surfaces, and a missing caution about analytics code.

---

## 2. Covered Scope Summary

| Area | Coverage |
|------|----------|
| Top-level directory tree | Good — all major folders present |
| Root files table | Partial — 4 files missing |
| Architecture layers & core objects | Good — main objects described |
| IPC protocol (v1/v2) | Good |
| Build pipeline (xcodebuild + Zig) | Good |
| Test surfaces (Swift unit/UI + Python e2e) | Good |
| Release pipeline (Sparkle, Homebrew, GH Actions) | Partial — Sparkle key-management scripts missing |
| Excluded/low-value areas | Partial — analytics code unmentioned |
| Sources/ subsystems | Partial — window subsystem, analytics, entry-point duality missing |

---

## 3. Missing Items

| # | Item | Why It Matters | Suggested Addition |
|---|------|----------------|-------------------|
| 1 | `ghostty.h` (root file) | A hand-written C header that defines the Ghostty embedding API contract between the Zig/libghostty core and Swift. Distinct from `cmux-Bridging-Header.h`. Any developer touching Ghostty integration must read it first. | Add row to §2 "루트 주요 파일" table: `ghostty.h` → "Ghostty 임베딩 API C 헤더; Zig 코어 ↔ Swift 계약 정의. `cmux-Bridging-Header.h`와 별개." |
| 2 | `bun.lock` → Bun as JS runtime | `package.json` is listed but the spec implies npm. The `bun.lock` file confirms **Bun** is the actual JS package manager. `npm install` will not reproduce the lock; `bun install` is required for `docs-site/` and `web/` dev work. | Add `bun.lock` to §2 root-files table with note "Bun lockfile; JS 의존성은 `npm` 대신 `bun install`로 재현". Add Bun to §4 Build tooling prerequisites. |
| 3 | `PostHogAnalytics.swift` (Sources/) | An analytics integration (PostHog) is compiled into the app. Architecturally significant: it represents a telemetry/privacy surface that agents must not inadvertently trigger or break. Not mentioned anywhere in the overview. | Add to §3 architecture objects table. Add to §7 low-value/caution table: "운영 분석 코드; opt-in 정책은 `.rules/logging-privacy.md` 참조. 로직 변경 시 주의." |
| 4 | `cmuxApp.swift` entry point | The spec names `AppDelegate.swift` as "앱 진입점" but `cmuxApp.swift` (SwiftUI `@main`) is the actual app entry point in modern Swift. The dual-entry-point structure (SwiftUI App + AppDelegate lifecycle) is architecturally non-trivial and affects bootstrap order. | Update §3 "핵심 객체" to clarify `cmuxApp.swift` is `@main` / SwiftUI entry, and `AppDelegate` is the lifecycle delegate; note they coexist. |
| 5 | Sparkle key-management scripts | `scripts/` contains `derive_sparkle_public_key.swift`, `sparkle_generate_appcast.sh`, `sparkle_generate_keys.sh`. The spec mentions Sparkle for auto-updates but omits the operational scripts needed to rotate signing keys or regenerate the appcast. Whoever operates the release pipeline needs to know these exist. | Add sub-rows to §4 scripts table listing the three scripts as "Sparkle 서명 키 생성·appcast 재생성 도구". |
| 6 | `UITestRecorder.swift` in Sources/ (not tests/) | This file lives in `Sources/` (app bundle), not in `GhosttyTabsUITests/`. It ships inside the app binary and acts as a UI-test recording hook. Agents modifying Sources/ may accidentally change or expose this. | Add to §7 caution table: "앱 번들에 포함된 UI 테스트 레코더; 의도치 않은 수정 주의." |
| 7 | `Panels/bonsplit/` vs `vendor/bonsplit/` | `vendor/bonsplit/` is documented as the vendored library, but `Sources/Panels/` also contains a `bonsplit/` subdirectory. The relationship (symlink? copy? different abstraction layer?) is undocumented. An agent targeting split-pane behavior could edit the wrong copy. | Add a note in §2 under `vendor/bonsplit/` and `Sources/Panels/`: clarify whether `Panels/bonsplit/` is a wrapper over `vendor/bonsplit/` or a separate copy, and which one to edit. |

---

## 4. Optional Additions

| Item | Note |
|------|------|
| `scripts/notify_probe.sh` | Small notification probe script; worth listing under §4 for completeness alongside `run-tests-*.sh`. |
| `scripts/rebuild.sh` | Full rebuild helper not listed; the spec's `reload*.sh` catchall does not cover it. |
| `docs/assets/` | Subdirectory under `docs/` containing image assets for the Markdown specs. Minor; add a parenthetical in §5. |
| `WindowDecorationsController.swift`, `WindowToolbarController.swift`, `WindowAccessor.swift` | Constitute a window-chrome subsystem in Sources/; not critical but rounds out the architecture map. |
| `.vercelignore` | Controls Vercel deployment scope; worth a one-line mention in §4 "배포 지원" alongside `package.json`. |
| `Backport.swift` | API compatibility shim; low priority but relevant if targeting older macOS. |

---

## 5. Recommended Follow-Up for the Next Agent

1. **Resolve `cmuxApp.swift` vs `AppDelegate.swift` bootstrap order** — confirm which is `@main` and update §3 object table and §6 read-priority list accordingly. See `.rules/app-bootstrap-threading.md` for the authoritative contract.
2. **Clarify `Panels/bonsplit/` origin** — run a quick diff or check git history to determine if it is a copy or wrapper of `vendor/bonsplit/`, then update both §2 tree and §7 caution rows.
3. **Add Bun to §4 prerequisites** — verify whether `bun.lock` is at the `cmux/` root or under `docs-site/`/`web/`, and confirm `bun install` is the correct command, then update the spec.
4. **PostHog opt-in policy cross-reference** — after adding `PostHogAnalytics.swift` to §3 and §7, link to `.rules/logging-privacy.md` for the opt-in and redaction rules.
5. **Sparkle scripts** — confirm the three Sparkle scripts are still current (not stale), then add to §4 scripts table.
