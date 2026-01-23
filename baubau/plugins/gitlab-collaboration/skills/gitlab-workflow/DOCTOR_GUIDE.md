# Doctor 명령어 완전 가이드

GitLab Workflow 스킬의 환경 설정을 검증하고 문제를 진단하는 포괄적인 도구입니다.

## 개요

Doctor 명령어는 다음을 확인합니다:
1. ✅ **환경 변수** - GITLAB_URL, GITLAB_TOKEN, GITLAB_PROJECT 설정
2. ✅ **Git 리포지토리** - 현재 디렉토리가 git 리포지토리인지 확인
3. ✅ **Git 원격** - 원격 저장소 설정 확인
4. ✅ **GitLab API 연결** - GitLab 서버 접근 가능 여부
5. ✅ **토큰 권한** - API 토큰이 올바른 권한을 가지고 있는지
6. ✅ **Issue 디렉토리** - issue.json 저장 경로 (선택사항)

## 사용 시기

### 필수로 실행해야 하는 경우

1. **처음 설치 후**
   ```bash
   /gitlab-workflow doctor
   ```
   스킬을 처음 설정한 후 모든 것이 올바르게 구성되었는지 확인

2. **문제가 발생했을 때**
   - API 에러가 발생하는 경우
   - 이슈 생성이 실패하는 경우
   - 브랜치 푸시가 안 되는 경우
   - 원인을 모르는 오류가 발생하는 경우

3. **환경이 변경된 후**
   - GitLab 서버 주소 변경
   - 새로운 프로젝트로 전환
   - 토큰 재생성
   - Git 원격 저장소 변경

### 선택적으로 실행하는 경우

- 정기적인 health check (주기적으로 실행하여 환경 상태 확인)
- 팀원에게 설정 방법을 알려줄 때 (올바르게 설정되었는지 검증용)

## 실행 방법

### Claude Code에서

```bash
/gitlab-workflow doctor
```

### CLI에서 직접

```bash
python3 .claude/skills/gitlab-workflow/scripts/gitlab_workflow.py doctor
```

### 환경 변수 없이도 실행 가능

Doctor는 검증이 목적이므로 환경 변수가 없어도 실행됩니다:
- 환경 변수가 없으면 해당 항목이 "Missing"으로 표시
- 누락된 항목에 대한 해결 방법 제공

## 출력 예제

### 모든 체크 통과

```
🏥 Running GitLab Workflow Doctor...

📋 Checking environment variables...
   ✅ GITLAB_URL: Set
   ✅ GITLAB_TOKEN: Set
   ✅ GITLAB_PROJECT: Set

📦 Checking Git repository...
   ✅ Git repository: Found

🌐 Checking Git remote...
   ✅ Git remote 'gitlab': ssh://git@192.168.210.103:4022/withvtm_2.0/withvtm-fe.git

🔌 Checking GitLab API connectivity...
   ✅ GitLab API: Connected
   ✅ Project: withVTM_2.0 / withVTM-FE
   ✅ URL: http://192.168.210.103:90/withvtm_2.0/withvtm-fe

🔑 Checking GitLab token permissions...
   ✅ Token permissions: Valid (can read issues)
   ✅ Token user: catchu87

📁 Checking issue directory...
   ✅ Issue directory: docs/requirements

============================================================
✅ All checks passed! GitLab workflow is ready to use.

💡 Try: /gitlab-workflow create
============================================================
```

### 체크 실패 예제

```
🏥 Running GitLab Workflow Doctor...

📋 Checking environment variables...
   ❌ GITLAB_URL: Missing
   ✅ GITLAB_TOKEN: Set
   ❌ GITLAB_PROJECT: Missing

📦 Checking Git repository...
   ❌ Git repository: Not found (not in a git repository)

🌐 Checking Git remote...
   ❌ Git remote: Not configured
   💡 Run: git remote add gitlab http://192.168.210.103:90/withvtm_2.0/withvtm-fe.git

🔌 Checking GitLab API connectivity...
   ❌ GitLab API: Connection failed
   💡 Error: GitLab API Error (401): {'message': '401 Unauthorized'}

🔑 Checking GitLab token permissions...
   ⏭️  Skipped (API not connected)

📁 Checking issue directory...
   ⚠️  Issue directory: Not configured (using default: docs/requirements)

============================================================
❌ Some checks failed. Please fix the issues above.

💡 Common fixes:
   • Set environment variables in .claude/.env.gitlab-workflow
   • Run 'git init' if not in a git repository
   • Add git remote: git remote add gitlab <url>
   • Check GitLab token has 'api' scope
============================================================
```

## 각 체크 항목 상세

### 1. 환경 변수 체크

**검사 내용:**
- `GITLAB_URL` 설정 여부
- `GITLAB_TOKEN` 설정 여부
- `GITLAB_PROJECT` 설정 여부

**해결 방법:**
`.claude/.env.gitlab-workflow` 파일 생성:
```bash
GITLAB_URL=http://192.168.210.103:90
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT=withvtm_2.0/withvtm-fe
GITLAB_REMOTE=gitlab
```

### 2. Git 리포지토리 체크

**검사 내용:**
- 현재 디렉토리가 git 리포지토리인지
- git 명령어가 설치되어 있는지

**해결 방법:**
```bash
# Git 초기화
git init

# Git 설치 확인
git --version
```

### 3. Git 원격 체크

**검사 내용:**
- 설정된 원격 저장소 존재 여부
- 원격 저장소 URL 확인

**해결 방법:**
```bash
# 원격 저장소 추가
git remote add gitlab http://192.168.210.103:90/withvtm_2.0/withvtm-fe.git

# 또는 SSH
git remote add gitlab ssh://git@192.168.210.103:4022/withvtm_2.0/withvtm-fe.git

# 원격 저장소 확인
git remote -v
```

### 4. GitLab API 연결 체크

**검사 내용:**
- GitLab 서버 접근 가능 여부
- 프로젝트 정보 조회 성공 여부
- 프로젝트 이름과 URL 표시

**해결 방법:**
```bash
# 수동으로 API 테스트
curl -H "PRIVATE-TOKEN: your-token" \
  http://192.168.210.103:90/api/v4/projects/withvtm_2.0%2Fwithvtm-fe

# 네트워크 연결 확인
ping 192.168.210.103

# 방화벽 설정 확인
```

### 5. 토큰 권한 체크

**검사 내용:**
- 토큰으로 이슈 목록 조회 가능한지 (`api` scope 필요)
- 현재 사용자 정보 조회
- 사용자 이름 표시

**해결 방법:**
1. GitLab → User Settings → Access Tokens
2. 새 토큰 생성 시 `api` scope 선택
3. 생성된 토큰을 `.env.gitlab-workflow`에 설정

### 6. Issue 디렉토리 체크

**검사 내용:**
- `ISSUE_DIR` 환경 변수 설정 여부
- 설정된 디렉토리 존재 여부

**참고:**
- 이 체크는 선택사항입니다
- 디렉토리가 없으면 자동으로 생성됩니다
- 기본값: `docs/requirements`

## 문제 해결 플로우

```
doctor 실행
    │
    ├─ 모든 체크 통과? ─ Yes ─→ 스킬 사용 가능!
    │
    └─ No ─→ 실패한 항목 확인
              │
              ├─ 환경 변수? ─→ .env.gitlab-workflow 설정
              ├─ Git 리포지토리? ─→ git init 실행
              ├─ Git 원격? ─→ git remote add
              ├─ API 연결? ─→ URL/네트워크 확인
              └─ 토큰 권한? ─→ 새 토큰 생성 (api scope)
              │
              └─→ 수정 후 다시 doctor 실행
```

## 자주 묻는 질문

### Q: Doctor를 매번 실행해야 하나요?
A: 아니요. 처음 설정할 때와 문제가 발생했을 때만 실행하면 됩니다.

### Q: 일부 체크가 실패해도 스킬을 사용할 수 있나요?
A: 환경 변수, API 연결, 토큰 권한은 필수입니다. Issue 디렉토리는 선택사항입니다.

### Q: Doctor가 실패하는데 스킬은 정상 작동합니다.
A: Doctor는 포괄적인 검증을 수행하므로 일부 선택적 항목이 실패해도 기본 기능은 작동할 수 있습니다.

### Q: 환경 변수를 설정했는데도 "Missing"으로 표시됩니다.
A: `.env.gitlab-workflow` 파일 위치를 확인하세요:
   - 프로젝트 루트: `.claude/.env.gitlab-workflow`
   - 또는 git 루트에서 상대 경로로 찾습니다

### Q: API 연결은 되는데 권한 체크가 실패합니다.
A: 토큰에 `api` scope가 없는 것입니다. GitLab에서 새 토큰을 생성할 때 반드시 `api` scope를 선택하세요.

## 고급 사용

### CI/CD 환경에서

```bash
# Exit code로 성공/실패 확인
python3 .claude/skills/gitlab-workflow/scripts/gitlab_workflow.py doctor
if [ $? -eq 0 ]; then
  echo "Setup is valid"
else
  echo "Setup has issues"
  exit 1
fi
```

### 자동화 스크립트에서

```bash
# Doctor 실행 후 자동으로 워크플로우 시작
/gitlab-workflow doctor && /gitlab-workflow create
```

## 추가 참고 자료

- [SKILL.md](SKILL.md) - 전체 스킬 문서
- [README.md](README.md) - 사용자 가이드
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 빠른 참조

---

**버전**: 3.2.0
**업데이트**: 2026-01-22
**문서**: `.claude/skills/gitlab-workflow/`
