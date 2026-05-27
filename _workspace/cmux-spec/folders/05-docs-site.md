# `docs-site`

## 역할 / 목적

cmux 공개 문서 사이트. Next.js(App Router) + Fumadocs(mdx) + Tailwind CSS 스택으로 구성되며 Vercel에 자동 배포된다. 사용자 설치·기능·API·키보드 단축키 가이드를 제공한다.

## 주요 내용

```
docs-site/
├── app/                    # Next.js App Router 레이아웃 및 페이지
├── content/
│   └── docs/               # MDX 문서 콘텐츠
│       ├── index.mdx
│       ├── installation.mdx
│       ├── concepts.mdx
│       ├── keyboard-shortcuts.mdx
│       ├── cli.mdx
│       ├── notifications.mdx
│       ├── osc-sequences.mdx
│       ├── socket-api.mdx
│       ├── splits.mdx
│       ├── tabs.mdx
│       ├── configuration.mdx
│       ├── environment-variables.mdx
│       ├── claude-code-hooks.mdx
│       └── changelog.mdx          # 릴리즈 별 변경 이력
├── lib/                    # 유틸리티
├── public/                 # 정적 에셋
├── next.config.mjs
├── source.config.ts        # Fumadocs 소스 설정
├── tailwind.config.ts
├── vercel.json
└── package.json
```

## 저장소 상호작용 / 의존성

- `scripts/bump-version.sh`가 `content/docs/changelog.mdx`를 릴리즈 시 자동 갱신한다.
- 이 폴더는 **독립적인 Next.js 프로젝트**이며 자체 `package.json` / `package-lock.json`(npm)으로 의존성을 관리한다.
- 루트 `node_modules/`와는 별개로 동작하며, 루트 패키지의 `vercel` 의존성과 workspace를 공유하지 않는다.
- `.vercelignore`로 Vercel 배포 범위를 제어한다.

## 편집 지침

**문서 콘텐츠 변경은 `content/docs/`만 편집**. Next.js/Fumadocs 설정 변경은 드물다. 앱 기능 변경 시 대응하는 MDX 파일을 함께 갱신해야 한다. 로컬 미리보기는 `docs-site/` 기준 npm 스크립트를 우선 따른다.

## 불확실성

없음.
