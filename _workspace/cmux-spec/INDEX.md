# cmux-spec 문서 인덱스

> `_workspace/cmux-spec/` 내 모든 마크다운 문서의 목록과 간략한 설명.

---

## 핵심 명세 문서

| 파일 | 설명 |
|------|------|
| [project-overview.md](project-overview.md) | cmux 프로젝트 전체 개요. 정체·아키텍처·핵심 개념을 정리한 최상위 참조 문서. |
| [folder-manifest.md](folder-manifest.md) | `cmux/` read-only 소스 트리의 최상위 디렉터리 목록과 각 폴더의 역할 요약. |
| [integrated-spec.md](integrated-spec.md) | Windows 포트(cmux-win) 관점의 통합 참조 스펙. 구현 시 가장 먼저 읽어야 할 문서. |

---

## 리뷰·검토 문서

| 파일 | 설명 |
|------|------|
| [project-overview-accuracy-review.md](project-overview-accuracy-review.md) | `project-overview.md`의 사실 정확성 검토 결과. |
| [project-overview-omission-review.md](project-overview-omission-review.md) | `project-overview.md`에서 누락된 항목 검토 결과. |
| [folders-accuracy-review.md](folders-accuracy-review.md) | `folder-manifest.md` 및 `folders/*.md`의 사실 정확성 검토 결과. |
| [folders-omission-review.md](folders-omission-review.md) | `folder-manifest.md` 및 `folders/*.md`의 누락 항목 검토 결과. |
| [integrated-spec-accuracy-review.md](integrated-spec-accuracy-review.md) | `integrated-spec.md`의 사실 정확성 검토 결과. |
| [integrated-spec-omission-review.md](integrated-spec-omission-review.md) | `integrated-spec.md`의 누락 항목 검토 결과. |
| [spec-vs-source-gap-review.md](spec-vs-source-gap-review.md) | 명세 ↔ 실제 `cmux/` 소스 간 양방향 갭 분석. 명세 과잉·소스 누락 항목을 모두 포함. (2026-05-28) |
| [missing-items-review.md](missing-items-review.md) | `cmux/` 소스 트리 직접 분석으로 발견한 명세 전체 누락 항목 목록. (2026-05-29) |
| [verification-summary-2026-05-29.md](verification-summary-2026-05-29.md) | spec-vs-source-gap-review.md 및 missing-items-review.md의 모든 갭 항목이 명세에 반영되었음을 확인한 최종 검증 보고서. |
| [CONSISTENCY-CHECK-2026-05-29-FINAL.md](CONSISTENCY-CHECK-2026-05-29-FINAL.md) | 명세 ↔ 실제 소스 간 정합성 최종 점검. spec-vs-source-gap-review.md §6 처리 결과의 실제 적용 여부를 파일별로 검증. |

---

## 폴더별 세부 명세 (`folders/`)

| 파일 | 대상 폴더 | 설명 |
|------|-----------|------|
| [folders/00-dot-claude.md](folders/00-dot-claude.md) | `.claude` | Claude Code 에이전트 전용 설정 및 커스텀 슬래시 커맨드 정의. |
| [folders/01-dot-github.md](folders/01-dot-github.md) | `.github` | GitHub Actions CI/CD 워크플로 (PR 검증, 릴리즈 빌드·배포, Homebrew 갱신). |
| [folders/02-assets-xcassets.md](folders/02-assets-xcassets.md) | `Assets.xcassets` | Xcode 이미지 에셋 카탈로그 (앱 아이콘, UI 이미지 리소스). |
| [folders/03-cli.md](folders/03-cli.md) | `CLI` | `cmux` CLI 도구 Swift 소스. Unix 소켓(`/tmp/cmux.sock`)으로 앱과 통신. |
| [folders/04-docs.md](folders/04-docs.md) | `docs` | 내부 기술 스펙 문서 (API 설계, 포크 노트). `docs-site/`의 공개 문서와 구별. |
| [folders/05-docs-site.md](folders/05-docs-site.md) | `docs-site` | 공개 문서 사이트. Next.js + Fumadocs + Tailwind, Vercel 배포. |
| [folders/06-ghostty.md](folders/06-ghostty.md) | `ghostty` | git 서브모듈. Zig 터미널 렌더링 엔진 (GPU 가속, VT 파싱, PTY 관리). |
| [folders/07-ghosttytabs-xcodeproj.md](folders/07-ghosttytabs-xcodeproj.md) | `GhosttyTabs.xcodeproj` | 주 Xcode 프로젝트 정의 (앱·CLI·테스트 타겟, 빌드 설정, 코드 사이닝). |
| [folders/08-ghosttytabstests.md](folders/08-ghosttytabstests.md) | `GhosttyTabsTests` | Swift 유닛 테스트 타겟. 호스트 머신에서 직접 실행 가능. |
| [folders/09-ghosttytabsuitests.md](folders/09-ghosttytabsuitests.md) | `GhosttyTabsUITests` | Swift XCTest UI 테스트. 반드시 UTM VM(`ssh cmux-vm`)에서 실행. |
| [folders/10-graphify-out.md](folders/10-graphify-out.md) | `graphify-out` | `graphify` 스킬이 생성한 지식 그래프 캐시 파일 저장소. |
| [folders/11-homebrew-cmux.md](folders/11-homebrew-cmux.md) | `homebrew-cmux` | git 서브모듈. Homebrew Cask 정의 (`brew install --cask … cmux`). |
| [folders/12-node-modules.md](folders/12-node-modules.md) | `node_modules` | 루트 `package.json`의 `vercel` 의존성 설치 위치 (생성물 전용). |
| [folders/13-resources.md](folders/13-resources.md) | `Resources` | 앱 번들 런타임 리소스 (셸 통합 스크립트, terminfo, Claude 래퍼, 번들 메타데이터). |
| [folders/14-scripts.md](folders/14-scripts.md) | `scripts` | 빌드·개발·테스트·릴리즈용 Shell 스크립트 모음. |
| [folders/15-skills.md](folders/15-skills.md) | `skills` | 에이전트 스킬 문서 (소켓 API 조작, 브라우저 자동화, 릴리즈 등). |
| [folders/16-sources.md](folders/16-sources.md) | `Sources` | cmux 앱 핵심 Swift 소스 (SwiftUI, GhosttyKit, IPC, 탭·워크스페이스 관리). |
| [folders/17-tests.md](folders/17-tests.md) | `tests` | 소켓 API v1 기반 Python e2e 테스트. UTM VM에서 실행. |
| [folders/18-tests-v2.md](folders/18-tests-v2.md) | `tests_v2` | 소켓 API v2 기반 Python e2e 테스트 (현행). UTM VM에서 실행. |
| [folders/19-vendor.md](folders/19-vendor.md) | `vendor` | 외부 git 서브모듈 관리 루트 (현재 `bonsplit` 포함). |
| [folders/20-web.md](folders/20-web.md) | `web` | 마케팅·랜딩 사이트. Next.js + Tailwind, Vercel 배포. `docs-site/`와 별개. |
