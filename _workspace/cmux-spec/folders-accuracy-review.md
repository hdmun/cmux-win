# Folder-Spec Accuracy Review

> Reviewer: GitHub Copilot (automated)  
> Date: 2025-07  
> Inputs: `folder-manifest.md` + `folders/*.md` (21 files)  
> Reference tree: `cmux/` (read-only)

---

## 1. Verdict

**needs-update** — 5 confirmed factual errors across 3 spec files. The remaining 18 folder docs are accurate.

---

## 2. Verified Strengths

- All 21 top-level directories are present in the actual tree with correct names and classifications.
- `CLI/cmux.swift` size claim (~135 KB) is accurate: actual = 138,799 bytes = 135.5 KB.
- `docs/` file list (`notifications.md`, `agent-browser-port-spec.md`, `v2-api-migration.md`, `ghostty-fork.md`, `assets/`) is exact.
- `.github/workflows/` workflow filenames (`ci.yml`, `nightly.yml`, `release.yml`, `update-homebrew.yml`) are all confirmed.
- `GhosttyTabsTests/` and `GhosttyTabsUITests/` file lists match exactly.
- `Assets.xcassets/` structure (`AppIcon-Debug.appiconset/`, `AppIcon.appiconset/`, `Contents.json`) is correct.
- `Resources/shell-integration/` contents (`.zlogin`, `.zprofile`, `.zshenv`, `.zshrc`, `cmux-zsh-integration.zsh`, `cmux-bash-integration.bash`) match exactly.
- `Resources/` root layout (`bin/`, `ghostty/`, `shell-integration/`, `terminfo-overlay/`, `Info.plist`) is correct.
- `scripts/` file list is complete and accurate.
- `vendor/bonsplit` submodule URL and path match `.gitmodules`.
- `ghostty/` and `homebrew-cmux/` submodule URLs match `.gitmodules`.
- `ghostty/` structural contents (build.zig, AGENTS.md, AI_POLICY.md, HACKING.md, dist/, include/, macos/, src/) are present.
- `setup.sh` build command (`cd ghostty && zig build -Demit-xcframework=true -Doptimize=ReleaseFast`) matches exactly.
- `tests/` count "40여 개" and `tests_v2/` count "40여 개" are both accurate (41 Python files each).
- `skills/` top-level subfolder names (`cmux/`, `cmux-browser/`, `cmux-debug-windows/`, `release/`) match exactly.
- `docs-site/content/docs/` MDX file list matches exactly.
- `web/` has independent `bun.lock` (confirmed) and is not a workspace member (confirmed).

---

## 3. Accuracy Issues

| # | File | Claim | Problem | Evidence | Correction |
|---|------|-------|---------|----------|------------|
| 1 | `01-dot-github.md` | "`skills/release/` 폴더에 `release.md` 파일이 있어 릴리즈 에이전트 스킬 문서가 워크플로와 연동된다" | Wrong filename. The cited file does not exist. | `Get-ChildItem cmux/skills/release` → `SKILL.md` only; no `release.md` | Replace `release.md` with `SKILL.md` |
| 2 | `05-docs-site.md` | "루트 `package.json`의 JS 워크스페이스에 포함되며" | Root `package.json` has **no `workspaces` field** — docs-site is not a declared workspace member. | `cmux/package.json` = `{"dependencies":{"vercel":"^50.9.5"},"license":"..."}` only | Remove the workspace membership claim; state that docs-site has its own standalone `package.json` |
| 3 | `05-docs-site.md` | "node_modules/는 이 사이트와 `web/`의 공유 의존성을 포함한다" | Follows from error #2. No workspace definition means root `node_modules/` does not contain docs-site or web dependencies — it contains only `vercel` CLI dependencies. | Root `package.json` has a single `vercel` dependency; docs-site has its own `package-lock.json`; web has its own `bun.lock` | Remove shared-dependency claim; note that docs-site manages its own deps via its own `package-lock.json` |
| 4 | `05-docs-site.md` | "`bun.lock`으로 의존성이 관리된다" | docs-site itself has a `package-lock.json` (npm), not a `bun.lock`. The root `bun.lock` is for the root-level `vercel` package only. | `cmux/docs-site/package-lock.json` exists; `cmux/docs-site/bun.lock` does not | Change to: "docs-site 자체 의존성은 `docs-site/package-lock.json`(npm)으로 관리된다" |
| 5 | `10-graphify-out.md` | "`.gitignore`에 포함되어 있을 것으로 예상된다" | `graphify-out` is **not** in `.gitignore`. The string "graphify" does not appear anywhere in `cmux/.gitignore`. | Full content of `cmux/.gitignore` read; no "graphify" entry found | Remove the expectation. Note: graphify-out is NOT gitignored and will be tracked by git unless excluded manually |
| 6 | `12-node-modules.md` | "docs-site/와 web/의 JavaScript/TypeScript 의존성이 설치된 위치" | Same root as error #2–3: root `package.json` defines no workspace; root `node_modules/` does not contain docs-site or web packages. | Root `package.json` has only `vercel` dep; docs-site and web each have their own lock files and no shared workspace definition | Change to: "루트 `vercel` 의존성의 설치 위치. `docs-site/`와 `web/`의 의존성은 여기에 포함되지 않는다" |

---

## 4. Lower-Confidence Concerns

These require deeper investigation but are not confirmed errors:

1. **`06-ghostty.md` — GhosttyKit.xcframework root symlink undocumented**  
   `setup.sh` builds `ghostty/macos/GhosttyKit.xcframework` *and* creates a symlink at the repo root (`ln -sf ghostty/macos/GhosttyKit.xcframework GhosttyKit.xcframework`). The spec describes the artifact only as residing inside `macos/` and does not mention the root-level symlink. The symlink is what `GhosttyTabs.xcodeproj` likely resolves at build time. The current spec is not strictly wrong but is incomplete about the consumption path.

2. **`07-ghosttytabs-xcodeproj.md` — xcframework link path**  
   Related to concern #1: the spec says the project "링크한다" (links) GhosttyKit.xcframework from the `ghostty/` submodule but the actual link target may be the repo-root symlink, not a path inside the submodule directly. Verify the `project.pbxproj` `FRAMEWORK_SEARCH_PATHS` to confirm.

3. **`05-docs-site.md` — bun dev instruction**  
   The spec recommends `bun dev` for local preview, but docs-site has a `package-lock.json` indicating npm is the canonical package manager for that subdirectory. `bun dev` will likely work (bun is compatible with npm projects), but the guidance could mislead developers to expect `bun install` to work when `npm install` is the expected workflow for docs-site.

4. **`10-graphify-out.md` — git tracking consequence**  
   Since `graphify-out/` is not in `.gitignore`, runs of the graphify skill will produce untracked committed or dirty-state files. This may or may not be intentional. The spec says to ignore the directory during development but it's unclear whether it should be gitignored or committed.

---

## 5. Recommended Follow-Up for the Next Agent

**Priority fixes (confirmed errors):**

1. **`01-dot-github.md`** — Change `release.md` → `SKILL.md` in the cross-reference to `skills/release/`.

2. **`05-docs-site.md`** — Rewrite the dependency/workspace section:
   - Remove "루트 `package.json`의 JS 워크스페이스에 포함되며"
   - Remove "node_modules/는 이 사이트와 web/의 공유 의존성을 포함한다"
   - Replace `bun.lock` mention with `package-lock.json` for docs-site itself
   - Note that docs-site is a standalone Next.js project managed independently with npm

3. **`10-graphify-out.md`** — Remove the gitignore expectation claim. Explicitly state that `graphify-out/` is currently NOT in `.gitignore` and flag whether this is intentional.

4. **`12-node-modules.md`** — Correct the description to reflect root `node_modules` contains only the `vercel` CLI dependency, not docs-site/web packages.

**Investigation needed:**

5. **`06-ghostty.md` / `07-ghosttytabs-xcodeproj.md`** — Confirm whether `project.pbxproj` references `GhosttyKit.xcframework` via the repo-root symlink or via the path inside `ghostty/macos/`. Update whichever spec is imprecise once confirmed.

6. **`graphify-out/` gitignore decision** — Confirm with the team whether `graphify-out/` should be added to `.gitignore`. If yes, add it and update the spec to state it IS gitignored.
