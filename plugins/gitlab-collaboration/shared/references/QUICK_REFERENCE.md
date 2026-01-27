# GitLab Workflow - Quick Reference

빠른 참조 가이드 - 자주 사용하는 명령어와 패턴을 한눈에!

## 🚀 가장 많이 사용하는 명령어

```bash
# 0️⃣ 초기 설정 (처음 한 번만!)
/gitlab-init
# → 대화형 설정 마법사로 .env 파일 자동 생성

# 1️⃣ 환경 설정 검증
/gitlab-doctor

# 2️⃣ 인터랙티브 모드로 이슈 생성 (가장 추천)
/gitlab-issue-create

# 3️⃣ JSON 파일로 이슈 생성 (문서화된 기능)
/gitlab-issue-create --from-file docs/requirements/vtm-1372/342/issue.json

# 4️⃣ Git 히스토리로 이슈 업데이트 (이슈 번호 자동!)
/gitlab-issue-update

# 5️⃣ MR 생성
/gitlab-mr
```

## 📋 JSON 파일 템플릿

```json
{
  "asana": "VTM-1372",
  "title": "이슈 제목",
  "description": "상세 설명\n\n## 변경사항\n- 항목1\n- 항목2",
  "labels": ["bug", "feature"],
  "push": true
}
```

**필수 필드**: `asana`, `title`
**선택 필드**: `description`, `labels`, `push`

## 🌿 브랜치 이름 규칙

| 형식 | 예시 | 설명 |
|------|------|------|
| `{Asana}/{GitLab#}-{요약}` | `VTM-1372/342-add-feature` | 표준 형식 |
| `{숫자}/{GitLab#}-{요약}` | `1372/342-fix-bug` | 숫자만 사용 |
| `{Asana}/{GitLab#}` | `VTM-1372/342` | 최소 형식 |

## ⚡ 빠른 워크플로우

### 처음 사용하는 경우
```bash
# 1. 초기 설정 (대화형)
/gitlab-init
# → GitLab URL 입력
# → 토큰 입력 (자동 숨김 처리)
# → 프로젝트 경로 입력
# → .env 파일 자동 생성 (600 권한)

# 2. 검증
/gitlab-doctor
```

### 인터랙티브 모드
```bash
/gitlab-issue-create
# → 질문에 답변
# → 이슈 생성됨
# → 브랜치 생성됨
# → 푸시 확인

git add .
git commit -m "작업 내용"
git push

# 이슈를 요구사항으로 업데이트 (번호 자동 추출)
/gitlab-issue-update

/gitlab-mr
# → MR 생성 (변경사항 자동 요약)
```

### JSON 파일 모드
```bash
# issue.json 작성
/gitlab-issue-create --from-file issue.json
# → 자동 생성

git add .
git commit -m "작업 내용"
git push

# 요구사항으로 이슈 갱신 (번호 자동)
/gitlab-issue-update

/gitlab-workflow mr
# → 커밋 히스토리 기반 MR description 자동 생성
```

## 🔧 자주 사용하는 CLI 명령어

```bash
# 전체 옵션으로 시작
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  --asana VTM-1372 start "제목" --labels "bug" --push

# JSON 파일로 시작
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  start --from-file issue.json

# 이슈 업데이트 (번호 자동 추출)
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update

# 이슈 업데이트 (번호 명시)
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py update 345

# 이슈 업데이트 (특정 브랜치)
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  update --branch vtm-1372/345-feature --base main

# 이슈 업데이트 + 제목 변경
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  update --update-title

# 브랜치만 생성
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  branch VTM-1372/342-feature --push

# 현재 브랜치 푸시
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py push

# MR 생성
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  mr "MR 제목" --issue 342
```

## 📁 추천 파일 구조

```
docs/requirements/
└── vtm-{asana}/
    └── {gitlab-issue}/
        ├── issue.json          # 이슈 정의
        ├── requirements.md     # 요구사항
        ├── plan.md            # 구현 계획
        └── assets/            # 스크린샷 등
```

## 🏷️ 라벨 컨벤션

| 카테고리 | 라벨 |
|----------|------|
| **타입** | `feature`, `bug`, `enhancement`, `refactoring` |
| **우선순위** | `critical`, `high`, `medium`, `low` |
| **영역** | `frontend`, `backend`, `api`, `ui` |
| **상태** | `in-progress`, `blocked`, `needs-review` |

## 🐛 빠른 트러블슈팅

| 문제 | 해결 |
|------|------|
| 이슈 생성 실패 | `curl http://192.168.210.103:90/api/v4/projects` |
| 브랜치 이름 오류 | 형식 확인: `{asana}/{gitlab}-{요약}` |
| 푸시 실패 | `git remote -v` 확인 |
| JSON 오류 | `python3 -m json.tool issue.json` |

## ⚙️ 환경 설정 (.env.gitlab-workflow)

```bash
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe
GITLAB_REMOTE=gitlab
```

## 📚 추가 문서

- 📖 **전체 문서**: [SKILL.md](./SKILL.md)
- 📘 **상세 가이드**: [README.md](./README.md)
- 🔄 **업데이트 가이드**: [UPDATE_SUMMARY.md](./UPDATE_SUMMARY.md) - Git 히스토리 기반 이슈 업데이트
- 📝 **변경 이력**: [CHANGELOG.md](./CHANGELOG.md)
- 🔧 **JSON 스키마**: [issue-template.json](./issue-template.json)

## 💡 팁

1. **인터랙티브 모드 우선**: 빠른 버그 수정이나 임시 작업
2. **JSON 파일 사용**: 계획된 기능이나 문서화가 필요한 경우
3. **푸시 자동화**: `"push": true`로 시간 절약
4. **MR 자동 요약**: MR 생성 시 커밋 히스토리 자동 요약 (description 미입력 시)
5. **MR 링크**: 항상 이슈와 연결해서 자동 close 활용
6. **명확한 커밋 메시지**: MR description에 사용되므로 의미있게 작성
7. **명확한 제목**: 브랜치 이름이 자동 생성되므로 구체적으로 작성

## 🎯 실전 예제

### 버그 수정
```bash
/gitlab-workflow create
# Asana: VTM-1372
# Title: 로그인 버튼 클릭 안되는 문제 수정
# Labels: bug,critical
# Push: yes
```

### 신규 기능
```json
{
  "asana": "VTM-1372",
  "title": "사용자 대시보드 추가",
  "description": "## 기능\n- 일일 활성 사용자\n- 세션 통계",
  "labels": ["feature", "dashboard"],
  "push": true
}
```

### 리팩토링
```bash
/gitlab-workflow create
# Asana: 1372
# Title: API 엔드포인트 구조 개선
# Labels: refactoring,api
# Push: yes
```

---

**버전**: 3.0.0
**업데이트**: 2026-01-22
**문서**: `.claude/skills/gitlab-workflow/`
