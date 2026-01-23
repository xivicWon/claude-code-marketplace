# Git 히스토리로 이슈 업데이트 - 완전 가이드

## 개요

`update` 명령어는 git 커밋 히스토리를 자동으로 분석하여 GitLab 이슈를 **요구사항 중심**으로 업데이트합니다.

## 빠른 사용법

```bash
# 현재 브랜치에서 업데이트 (이슈 번호 자동 추출!)
/gitlab-workflow update

# 이슈 번호 명시
/gitlab-workflow update 345

# 특정 브랜치에서 업데이트
gitlab_workflow.py update --branch vtm-1372/345-feature

# 제목도 함께 업데이트
gitlab_workflow.py update --update-title

# 다른 베이스 브랜치 사용
gitlab_workflow.py update --base develop
```

## 자동 이슈 번호 추출

**이슈 번호를 입력하지 않아도 됩니다!**

브랜치명 형식이 `{asana}/{issue}-{summary}`이면 자동으로 이슈 번호를 추출합니다:

- `vtm-1372/345-feature` → #345
- `1372/308-fix-bug` → #308
- `VTM-999/42-refactor` → #42

## 생성되는 내용

명령어는 다음 내용으로 마크다운 요약을 생성합니다:

1. **브랜치 이름**
2. **변경 예정 사항** (요구사항 중심)
3. **커밋 메시지에서 추출한 작업 내용**

**중요:** 구현 결과가 아닌 **요구사항과 변경할 사항**을 중심으로 작성됩니다.

## 예제 출력

```markdown
# 브랜치: vtm-1372/345-feature

## 📋 변경 예정 사항

### 1. 사용자 대시보드 추가
분석 차트가 포함된 대시보드를 구현합니다.
사용자 통계 및 세션 추적 기능을 추가합니다.

---

### 2. 대시보드 테스트 추가
대시보드에 대한 포괄적인 테스트 커버리지를 추가합니다.

---
```

## 모범 사례

1. **좋은 커밋 메시지 작성**: 요약 품질은 커밋 메시지 품질에 달려 있습니다
2. **MR 전에 업데이트**: 머지 리퀘스트를 만들기 전에 작업 문서화
3. **정기적인 업데이트**: 긴 브랜치의 경우 주기적으로 업데이트
4. **Conventional Commits 사용**: `feat:`, `fix:` 등의 prefix는 자동으로 제거됩니다

## 커밋 메시지 작성 팁

```bash
# ✅ 좋은 예: 변경할 사항을 명확하게 설명
git commit -m "feat: 조치 담당자 삭제 권한 개선

운영자 또는 projectManager가 점검 중에
조치 담당자를 삭제할 수 있도록 권한 조건 변경"

# ❌ 나쁜 예: 구현 결과만 나열
git commit -m "hasRemediatePermission computed 수정"
```

## 참고 자료

- [SKILL.md](SKILL.md) - 완전한 문서
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 명령어 치트 시트
- [README.md](README.md) - 종합 가이드
