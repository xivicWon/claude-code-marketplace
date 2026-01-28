# Interactive Mode Usage Guide

## 개요

JSON 파일 작성 없이 대화형으로 GitLab 워크플로우를 사용할 수 있습니다.

`★ Insight ─────────────────────────────────────`
**Interactive Mode 동작 방식:**
1. Interactive 스크립트 실행 → 사용자 입력 수집
2. 임시 JSON 파일 생성 (/tmp/gitlab-*.json)
3. JSON 경로 반환
4. 기존 forced workflow 실행
`─────────────────────────────────────────────────`

## 🎯 gitlab-issue-create (Interactive)

### 명령어

```bash
# Interactive mode
python shared/scripts/gitlab_workflow.py start --interactive

# 또는 단축형
python shared/scripts/gitlab_workflow.py start -i
```

### 실행 예시

```
$ python shared/scripts/gitlab_workflow.py start --interactive

🔄 Launching interactive mode...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 GitLab Issue Create - Interactive Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Issue Code (e.g., VTM-1372): VTM-1372
📝 Title: Add user dashboard
📄 Description (optional, press Enter to skip): Implement dashboard with analytics and charts
🏷️  Labels (comma-separated, optional): feature,ui,dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Review your input:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Issue Code:  VTM-1372
  Title:       Add user dashboard
  Description: Implement dashboard with analytics and charts
  Labels:      feature, ui, dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 Create GitLab issue and branch with these details? (Y/n): y

✅ JSON file created: /tmp/gitlab-issue-20260128_143022.json

JSON_PATH=/tmp/gitlab-issue-20260128_143022.json

🚀 Starting forced workflow with: /tmp/gitlab-issue-20260128_143022.json

🔍 Phase 0: Pre-flight validation
   ✅ Loaded JSON: /tmp/gitlab-issue-20260128_143022.json
   ✅ Issue Code: VTM-1372
   ✅ Title: Add user dashboard
   ...

[... forced workflow continues ...]
```

### 생성된 JSON 예시

```json
{
  "issueCode": "VTM-1372",
  "title": "Add user dashboard",
  "description": "Implement dashboard with analytics and charts",
  "labels": ["feature", "ui", "dashboard"]
}
```

### 입력 검증

**Issue Code 형식:**
- ✅ Valid: `VTM-1372`, `PROJ-123`, `1372`
- ❌ Invalid: `vtm_1372`, `project`

**Required 필드:**
- Issue Code (필수)
- Title (필수)

**Optional 필드:**
- Description (선택)
- Labels (선택, 쉼표로 구분)

## 🎯 gitlab-mr (Interactive)

### 명령어

```bash
# Interactive mode
python shared/scripts/gitlab_workflow.py mr --interactive

# 또는 단축형
python shared/scripts/gitlab_workflow.py mr -i
```

### 실행 예시

```
$ python shared/scripts/gitlab_workflow.py mr --interactive

🔄 Launching interactive mode...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 GitLab MR Create - Auto-detect Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ Detecting MR details from current branch...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Auto-detected MR details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Source Branch: vtm-1372/342-add-dashboard
  Target Branch: main (from .env)
  Issue Number:  #342 (from branch name)
  MR Title:      Add user dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 Options:
  1. Proceed with these details (Recommended)
  2. Edit MR title
  3. Change target branch
  4. Skip issue linking
  5. Cancel

Choose (1-5): 1

✅ JSON file created: /tmp/gitlab-mr-20260128_143530.json

JSON_PATH=/tmp/gitlab-mr-20260128_143530.json

✅ Loaded MR details from: /tmp/gitlab-mr-20260128_143530.json

✅ Created merge request !123: Add user dashboard
   Source: vtm-1372/342-add-dashboard → Target: main
   URL: http://gitlab.com/project/merge_requests/123
   Linked to issue #342 (will auto-close on merge)
```

### 자동 감지 로직

1. **Source Branch**: 현재 체크아웃된 브랜치
2. **Target Branch**: `.env`의 `BASE_BRANCH` 설정
3. **Issue IID**: 브랜치 이름에서 추출 (예: `vtm-1372/342-feature` → `342`)
4. **MR Title**: 첫 번째 커밋 제목 (또는 브랜치 이름에서)

### Interactive 옵션

```
Choose (1-5): 2  # Edit title

Current title: Add user dashboard
New title: Implement user dashboard with analytics

[... menu returns ...]

Choose (1-5): 3  # Change target branch

Current target: main
New target branch: develop

[... menu returns ...]

Choose (1-5): 4  # Skip issue linking

✅ Issue linking disabled

[... menu returns ...]

Choose (1-5): 1  # Proceed
```

### 생성된 JSON 예시

```json
{
  "title": "Add user dashboard",
  "targetBranch": "main",
  "issueIID": 342
}
```

## 🆚 비교: JSON vs Interactive

### JSON 파일 방식

**장점:**
- ✅ 재사용 가능 (템플릿)
- ✅ 버전 관리 가능
- ✅ CI/CD 자동화 가능
- ✅ 문서화 가능

**단점:**
- ❌ 파일 작성 필요
- ❌ 빠른 실행 어려움

**사용 시기:**
- 반복적인 이슈 생성
- 팀 템플릿 사용
- 자동화 스크립트

```bash
# 템플릿 재사용
cp templates/feature-issue.json my-issue.json
vim my-issue.json  # 수정
python gitlab_workflow.py start --from-file my-issue.json
```

### Interactive 방식

**장점:**
- ✅ 파일 작성 불필요
- ✅ 빠른 실행
- ✅ 직관적인 UX
- ✅ 입력 검증 즉시

**단점:**
- ❌ 재사용 불가
- ❌ 자동화 어려움

**사용 시기:**
- 빠른 이슈 생성
- 일회성 작업
- 수동 실행

```bash
# 바로 실행
python gitlab_workflow.py start -i
# [대화형 입력]
```

## 🔄 내부 동작 흐름

### gitlab-issue-create

```
사용자: gitlab_workflow.py start --interactive
         ↓
1. run_interactive_script('interactive_issue_create.py')
         ↓
2. interactive_issue_create.py 실행
   - 사용자 입력 수집
   - 입력 검증
   - /tmp/gitlab-issue-{timestamp}.json 생성
   - "JSON_PATH=/tmp/..." 출력
         ↓
3. gitlab_workflow.py가 stdout에서 JSON_PATH 추출
         ↓
4. forced_workflow(json_file_path) 호출
         ↓
5. 기존 강제 워크플로우 실행
```

### gitlab-mr

```
사용자: gitlab_workflow.py mr --interactive
         ↓
1. run_interactive_script('interactive_mr_create.py')
         ↓
2. interactive_mr_create.py 실행
   - 현재 브랜치 정보 자동 감지
   - 사용자 확인/수정
   - /tmp/gitlab-mr-{timestamp}.json 생성
   - "JSON_PATH=/tmp/..." 출력
         ↓
3. gitlab_workflow.py가 JSON 로드
         ↓
4. create_merge_request() 호출
         ↓
5. MR 생성
```

## 📝 Tips

### Issue Create

1. **빠른 입력**: 필수 항목만 입력하고 Enter로 skip
   ```
   Description (optional, press Enter to skip): [Enter]
   Labels (optional): [Enter]
   ```

2. **이슈 코드 형식**: 대소문자 구분 없음
   ```
   vtm-1372  → VTM-1372 (자동 변환)
   ```

3. **레이블 입력**: 쉼표로 구분, 공백 자동 제거
   ```
   feature, ui, dashboard  → ["feature", "ui", "dashboard"]
   ```

### MR Create

1. **자동 감지 신뢰**: 대부분의 경우 Option 1로 진행
   ```
   Choose (1-5): 1  # 90% 케이스
   ```

2. **브랜치 이름 규칙 준수**: 자동 감지를 위해
   ```
   ✅ vtm-1372/342-add-dashboard  # Issue #342 자동 감지
   ❌ feature/dashboard           # 수동 입력 필요
   ```

3. **이슈 연결 생략**: hotfix 등 이슈 없는 작업
   ```
   Choose (1-5): 4  # Skip issue linking
   ```

## 🐛 Troubleshooting

### Interactive 스크립트가 실행 안 됨

```bash
# 실행 권한 확인
ls -la shared/scripts/interactive_*.py

# 권한 부여
chmod +x shared/scripts/interactive_issue_create.py
chmod +x shared/scripts/interactive_mr_create.py
```

### JSON_PATH를 찾을 수 없음

**원인**: 스크립트가 중간에 취소되었거나 에러 발생

**해결**: 다시 실행하거나 JSON 파일 직접 사용
```bash
# 직접 JSON 사용
python gitlab_workflow.py start --from-file /tmp/gitlab-issue-*.json
```

### 입력 검증 실패

**Issue Code 검증:**
```
❌ Invalid format
✅ Use: VTM-1372, 1372, PROJ-123
```

**해결**: 올바른 형식으로 재입력

## 📚 See Also

- [기존 JSON 방식 가이드](README.md)
- [강제 워크플로우 설명](../skills/gitlab-issue-create/SKILL.md)
- [환경 설정](../shared/references/QUICK_REFERENCE.md)

---

**Version 2.0** - Interactive Mode Edition
*No files, just talk*
