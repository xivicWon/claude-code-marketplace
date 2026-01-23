# GitLab Workflow 자동화 - 완전 가이드

GitLab issue → branch → merge request 워크플로우를 완전 자동화합니다. JSON 파일 지원, git 히스토리 분석, MR 설명 자동 생성 기능을 포함합니다.

## 빠른 시작

### 방법 1: 인터랙티브 (질문에 답변)
```bash
/gitlab-workflow create
```

### 방법 2: JSON 파일에서 생성 (더 빠름)
```bash
/gitlab-workflow create --from-file docs/requirements/vtm-1372/342/issue.json
```

### 방법 3: Git 히스토리로 이슈 업데이트 (이슈 번호 자동 추출)
```bash
/gitlab-workflow update
```

### 방법 4: 자동 생성된 설명으로 MR 생성
```bash
/gitlab-workflow mr
```

### 방법 5: 환경 설정 검증 (처음 사용 전 권장)
```bash
/gitlab-workflow doctor
```

## JSON 파일 형식

GitLab 이슈 구성을 정의하는 JSON 파일을 생성합니다:

```json
{
  "asana": "VTM-1372",
  "title": "조치 담당자 해제 기능 추가",
  "description": "취약점 상세 페이지에서 조치 담당자를 해제할 수 있는 기능을 추가합니다.\n\n## 주요 변경사항\n- 조치 담당자 표시 영역에 '해제' 버튼 추가\n- 해제 시 확인 다이얼로그 표시\n- API 호출하여 담당자 정보 삭제\n- 성공/실패 토스트 메시지 표시",
  "labels": ["enhancement", "feature"],
  "push": true
}
```

### 필드 참조

| 필드 | 타입 | 필수 여부 | 설명 |
|-------|------|----------|-------------|
| `asana` | string | ✅ 필수 | Asana 이슈 식별자 (예: "VTM-1372", "1372") |
| `title` | string | ✅ 필수 | GitLab 이슈 제목 |
| `description` | string | ❌ 선택 | 이슈 설명 (마크다운 지원, 줄바꿈은 `\n` 사용) |
| `labels` | array/string | ❌ 선택 | 라벨 배열 `["bug", "feature"]` 또는 문자열 `"bug,feature"` |
| `push` | boolean | ❌ 선택 | 자동으로 원격에 푸시 (기본값: `false`) |

## 사용 예제

### 예제 1: 최소 JSON
```json
{
  "asana": "VTM-1372",
  "title": "로그인 버그 수정"
}
```

### 예제 2: 설명과 라벨 포함
```json
{
  "asana": "1372",
  "title": "사용자 대시보드 추가",
  "description": "사용자 분석을 위한 새 대시보드를 만듭니다.\n\n## 기능\n- 일일 활성 사용자 차트\n- 세션 지속 시간 통계",
  "labels": ["feature", "dashboard"]
}
```

### 예제 3: 자동 푸시 포함
```json
{
  "asana": "VTM-1400",
  "title": "API 엔드포인트 업데이트",
  "description": "/api/users 엔드포인트 리팩토링",
  "labels": ["refactoring"],
  "push": true
}
```

## CLI 사용법

### JSON 파일에서 생성
```bash
# 상대 경로 사용
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  start --from-file docs/requirements/vtm-1372/342/issue.json

# 절대 경로 사용
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  start --from-file /path/to/issue.json
```

### CLI 인자로 JSON 값 재정의
```bash
# JSON 파일에 라벨이 지정되어 있지만 CLI로 재정의
.claude/skills/gitlab-workflow/scripts/gitlab_workflow.py \
  start --from-file issue.json --labels "bug,critical"
```

## 파일 구조

이슈 JSON 파일의 권장 디렉토리 구조:

```
docs/
└── requirements/
    └── vtm-{asana}/
        └── {gitlab-issue}/
            ├── issue.json          # 이슈 정의
            ├── requirements.md     # 상세 요구사항
            └── plan.md            # 구현 계획
```

예제:
```
docs/
└── requirements/
    └── vtm-1372/
        ├── 342/
        │   ├── issue.json
        │   ├── requirements.md
        │   └── plan.md
        └── 343/
            ├── issue.json
            └── requirements.md
```

## JSON 파일의 장점

1. **버전 관리**: Git에서 이슈 정의 추적
2. **재사용성**: 유사한 이슈에 템플릿 사용
3. **일관성**: 팀 전체의 이슈 형식 표준화
4. **자동화**: CI/CD 파이프라인과 통합
5. **문서화**: 코드와 함께 이슈 스펙 유지

## JSON 스키마

`.claude/skills/gitlab-workflow/issue-template.json`에 IDE 검증 및 자동 완성을 위한 JSON 스키마가 제공됩니다.

### VS Code 설정

`.vscode/settings.json`에 추가:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["**/requirements/**/issue.json"],
      "url": "./.claude/skills/gitlab-workflow/issue-template.json"
    }
  ]
}
```

이렇게 하면 `requirements/` 디렉토리의 모든 `issue.json` 파일에 대해 자동 완성 및 검증이 활성화됩니다.

## 문제 해결

### "Error: File not found"
- 파일 경로가 올바른지 확인 (현재 디렉토리 기준 상대 경로 또는 절대 경로)
- 파일이 존재하는지 확인: `ls -la docs/requirements/vtm-1372/342/issue.json`

### "Error: Invalid JSON"
- JSON 구문 검증: `python3 -m json.tool issue.json`
- 후행 쉼표 확인 (JSON에서는 허용되지 않음)
- 특수 문자의 적절한 이스케이프 확인

### "Error: Asana issue is required"
- JSON 파일에 `"asana"` 필드 추가
- 또는 CLI로 제공: `--asana VTM-1372`

### "Error: Issue title is required"
- JSON 파일에 `"title"` 필드 추가
- 또는 CLI 인자로 제공 (위치 인자)

## 모범 사례

1. **JSON 파일을 단순하게 유지**: 필요한 필드만 포함
2. **의미 있는 파일 경로 사용**: Asana/GitLab 이슈 번호로 구성
3. **버전 관리**: 코드와 함께 JSON 파일 커밋
4. **설명 문서화**: 명확성을 위해 마크다운 사용
5. **JSON 구문 테스트**: 커밋 전에 검증

## 고급 기능

### Git 히스토리로 이슈 업데이트

**이슈 번호 불필요!** 현재 브랜치명에서 자동으로 추출합니다.

```bash
# 가장 간단한 방법 (이슈 번호 자동 추출)
/gitlab-workflow update

# 이슈 번호를 명시적으로 지정
/gitlab-workflow update 345

# 특정 브랜치에서 업데이트
gitlab_workflow.py update --branch vtm-1372/345-feature

# 첫 번째 커밋에서 제목 업데이트
gitlab_workflow.py update --update-title

# 다른 베이스 브랜치 사용
gitlab_workflow.py update --base develop
```

**생성되는 내용:**
- 브랜치 이름
- 변경 예정 사항 (요구사항 중심)
- 커밋 메시지에서 추출한 작업 내용

**중요:** 이슈 설명은 **구현 결과가 아닌 요구사항과 변경할 사항**을 중심으로 작성됩니다.

**출력 예제:**
```markdown
# 브랜치: vtm-1372/345-remediation-improvements

## 📋 변경 예정 사항

### 1. 조치 담당자 삭제 기능 개선
운영자 또는 projectManager가 점검 중에 조치 담당자를 삭제할 수 있도록 권한 조건을 개선합니다.

---

### 2. 삭제 버튼 UI 표시 조건 변경
hasRemediatePermission computed 로직을 수정하여 더 많은 사용자에게 삭제 기능을 제공합니다.

---
```

자세한 가이드는 [UPDATE_SUMMARY.md](./UPDATE_SUMMARY.md)를 참조하세요.

### 자동 생성된 MR 설명

MR 생성 시 git 히스토리에서 설명을 자동으로 생성:

```bash
/gitlab-workflow mr

# 자동으로:
# 📝 git 히스토리에서 MR 설명 생성 중...
# ✅ vtm-1372/345-feature 커밋에서 설명 생성 완료
# ✅ MR !123 생성 완료
```

**기능:**
- 소스와 타겟 브랜치 간 커밋 분석
- 통계와 함께 포맷된 마크다운 생성
- 모든 커밋 메시지와 메타데이터 포함
- 이슈에 자동 링크 (`Closes #345`)

**수동 설명 (자동 생성 건너뛰기):**
```bash
gitlab_workflow.py mr "MR 제목" \
  --description "사용자 정의 설명" \
  --issue 345
```

### 자동 저장된 issue.json

이슈 생성 시 워크플로우가 자동으로 issue.json을 저장:

```
docs/requirements/
└── vtm-1372/
    └── 345/
        └── issue.json  # 이슈 데이터와 함께 자동 저장
```

**저장되는 데이터:**
```json
{
  "id": "345",
  "asana": "vtm-1372",
  "branch": "vtm-1372/345-feature-name",
  "title": "이슈 제목",
  "description": "전체 설명",
  "labels": ["enhancement"],
  "push": true
}
```

`.claude/.env.gitlab-workflow`에서 저장 위치 구성:
```bash
ISSUE_DIR=docs/requirements
```

## 완전한 워크플로우 예제

```bash
# 1. 이슈와 브랜치 생성
/gitlab-workflow create --from-file docs/requirements/vtm-1372/345/issue.json
# → GitLab 이슈 #345 생성
# → 브랜치 vtm-1372/345-feature 생성
# → issue.json 자동 저장

# 2. 작업 수행
git commit -m "VTM-1372 feat: 기능 구현"
git commit -m "VTM-1372 test: 테스트 추가"
git push

# 3. 실제 작업 내용으로 이슈 업데이트
/gitlab-workflow update
# → 브랜치명에서 이슈 번호 자동 추출
# → 이슈 설명을 요구사항 중심으로 작성

# 4. 자동 생성된 설명으로 MR 생성
/gitlab-workflow mr
# → 커밋 분석
# → MR 설명 생성
# → 이슈 #345에 링크
# → MR이 머지되면 이슈 자동 닫힘
```

## 참고 자료

- [SKILL.md](./SKILL.md) - 완전한 스킬 문서
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 빠른 명령어 참조
- [UPDATE_SUMMARY.md](./UPDATE_SUMMARY.md) - 업데이트 기능 가이드
- [CHANGELOG.md](./CHANGELOG.md) - 버전 히스토리
- [issue-template.json](./issue-template.json) - JSON 스키마 정의
- [gitlab_workflow.py](./scripts/gitlab_workflow.py) - Python 스크립트 소스
