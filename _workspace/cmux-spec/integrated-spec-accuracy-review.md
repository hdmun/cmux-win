# Integrated Spec Accuracy Review

> Reviewer: Copilot (manual fallback after agent rate-limit)  
> Inputs: `_workspace/cmux-spec/integrated-spec.md`, `project-overview.md`, `folder-manifest.md`, `folders/*.md`, representative `cmux/` files  
> Date: 2026-05-27

---

## 1. Verdict

**pass**

No confirmed factual errors were found in the integrated spec after checking the revised overview, folder docs, and representative source files.

---

## 2. Verified Strengths

- `cmuxApp.swift` is correctly treated as the `@main` entry point, with `AppDelegate` as the lifecycle adapter.
- `vendor/bonsplit/` is correctly treated as a git submodule, not a vendored copy.
- `docs-site/` is correctly described as a standalone Next.js project with its own `package-lock.json`.
- `graphify-out/` is correctly treated as generated output and not assumed to be gitignored.
- `Sources/Find/` is now represented, including the search overlay responsibility.

---

## 3. Accuracy Issues

| claim | problem | evidence | correction |
|---|---|---|---|
| None confirmed | - | - | - |

---

## 4. Lower-confidence Concerns

- A few Windows-port clauses are synthesis from `_workspace` docs rather than direct `cmux/` source facts, but they are consistent with the current cmux-win authority model.
- The integrated spec intentionally mixes source-tree analysis with porting guidance; that is appropriate here, but future edits should keep the distinction clear.

---

## 5. Recommended Follow-up for the Next Agent

1. Treat `integrated-spec.md` as the top-level reading entry for future cmux reference work.
2. Use the per-folder docs for drill-down; they now cover all top-level folders.
3. If new repo facts appear, update the relevant folder doc first, then the integrated spec.
