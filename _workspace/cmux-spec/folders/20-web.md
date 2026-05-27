# `web`

## 역할 / 목적

**마케팅·랜딩 사이트**. cmux의 사용자-facing 홍보 페이지로 Next.js(App Router) + Tailwind CSS 스택으로 구성되며 Vercel에 배포된다. `docs-site/`의 기술 문서 사이트와 별개다.

## 주요 내용

```
web/
├── app/                    # Next.js App Router 레이아웃 및 페이지
│   ├── layout.tsx
│   ├── page.tsx            # 랜딩 페이지 (메인)
│   └── ...                 # 기타 라우트 (blog, community, legal 등)
├── public/                 # 정적 에셋 (이미지, 아이콘 등)
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── bun.lock                # web 전용 Bun lockfile
```

## 저장소 상호작용 / 의존성

- `docs-site/`와 달리 루트 `package.json` 워크스페이스에 포함되지 않으며 독립적인 `bun.lock`을 갖는다.
- Vercel에 별도 프로젝트로 배포된다.
- 앱 소스(`Sources/`, `CLI/`)와 직접 연결되지 않는다.

## 편집 지침

**마케팅 콘텐츠 변경 시만 접근**. 앱 코드나 API 작업 시 완전히 무시해도 된다. 로컬 미리보기: `cd web && bun dev`.

## 불확실성

없음.
