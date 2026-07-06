# cmux-win

cmux-win 구현/태스크 진행 요청 시 `cmux-win-autonomous-execution` 스킬을 사용한다. 단순 질문은 직접 응답한다.
상세 권한 모델·운영 규칙은 `AGENTS.md`와 `.rules/*.md`를 참조한다 (본 파일은 포인터만 유지).

## 변경 이력

| 일자 | 내용 |
|------|------|
| 2026-06-18 | 하네스 도입: `cmux_plan` CLI 및 자율 실행 하네스 구현 (`e95ff9c1`) |
| 2026-07-04 | 평가 후속 수정: P1 stdout UTF-8 인코딩 크래시, P2 verify --dry-run exit 0 및 milestone rollup 역방향, P3 verify timeout·check-docs 테스트·한국어 트리거 |
| 2026-07-05 | grill-me 9개 결정 반영: scrollback/selection 계약+m2-9, Ghostty 파싱 m6-2 확장, IME 한글 조합 필수화, m0-8/m0-10/AT gate 워크스루 보강 (`plans/grill-me-2026-07-05.md`) |
