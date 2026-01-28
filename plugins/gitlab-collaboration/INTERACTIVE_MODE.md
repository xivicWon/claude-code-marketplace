# Interactive Mode - Quick Reference

## 🎯 빠른 시작

### Issue 생성 (대화형)

```bash
cd plugins/gitlab-collaboration
python shared/scripts/gitlab_workflow.py start --interactive
```

### MR 생성 (대화형)

```bash
cd plugins/gitlab-collaboration
python shared/scripts/gitlab_workflow.py mr --interactive
```

## 📚 구조

```
plugins/gitlab-collaboration/
├── shared/scripts/
│   ├── gitlab_workflow.py                 # 메인 워크플로우
│   ├── interactive_issue_create.py        # 이슈 대화형 입력
│   └── interactive_mr_create.py           # MR 대화형 입력
│
├── examples/
│   ├── INTERACTIVE_USAGE.md               # 상세 사용 가이드
│   ├── issue-example.json                 # JSON 방식 예시
│   └── README.md                          # JSON 방식 가이드
│
└── INTERACTIVE_MODE.md                    # 이 문서
```

## 🔄 동작 방식

```
Interactive Script → JSON 생성 → Forced Workflow
     (사용자 입력)      (/tmp)       (기존 코드)
```

### Phase 1: 대화형 입력 (interactive_*.py)

- 사용자와 대화
- 입력 검증
- JSON 생성 (/tmp/gitlab-*.json)
- JSON 경로 출력

### Phase 2: 워크플로우 실행 (gitlab_workflow.py)

- JSON 경로 추출
- JSON 로드
- forced_workflow() 실행 (기존 로직)

## 📋 명령어 옵션

### Issue Create

```bash
# Interactive mode
python gitlab_workflow.py start --interactive
python gitlab_workflow.py start -i

# JSON file mode (기존)
python gitlab_workflow.py start --from-file issue.json
```

### MR Create

```bash
# Interactive mode
python gitlab_workflow.py mr --interactive
python gitlab_workflow.py mr -i

# CLI args mode (기존)
python gitlab_workflow.py mr "MR Title" --target main --issue 342
```

## 🆚 JSON vs Interactive

| 기능 | JSON 파일 | Interactive |
|------|-----------|-------------|
| **파일 작성** | 필요 | 불필요 |
| **실행 속도** | 빠름 (파일 준비 후) | 즉시 |
| **재사용** | ✅ 가능 | ❌ 불가 |
| **자동화** | ✅ 가능 | ❌ 불가 |
| **템플릿** | ✅ 가능 | ❌ 불가 |
| **입력 검증** | 실행 시 | 입력 시 |
| **사용 시기** | 반복 작업, CI/CD | 빠른 일회성 작업 |

## 💡 추천 사용 패턴

### 일반 개발자 (수동 작업)

```bash
# 이슈 생성: Interactive
python gitlab_workflow.py start -i

# 작업...

# MR 생성: Interactive
python gitlab_workflow.py mr -i
```

### 팀 템플릿 사용

```bash
# 템플릿 준비 (1회)
cat > templates/feature.json <<EOF
{
  "issueCode": "PROJ-XXX",
  "title": "Feature template",
  "labels": ["feature"]
}
EOF

# 사용 (반복)
cp templates/feature.json my-issue.json
vim my-issue.json  # 수정
python gitlab_workflow.py start --from-file my-issue.json
```

### CI/CD 자동화

```bash
# JSON으로 자동화
cat > auto-issue.json <<EOF
{
  "issueCode": "$ISSUE_CODE",
  "title": "$COMMIT_MESSAGE",
  "labels": ["auto-generated"]
}
EOF

python gitlab_workflow.py start --from-file auto-issue.json
```

## 🎨 Interactive 예시

### Issue Create

```
$ python gitlab_workflow.py start -i

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 GitLab Issue Create - Interactive Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Issue Code: VTM-1372
📝 Title: Add user dashboard
📄 Description: Implement dashboard
🏷️  Labels: feature,ui

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Review:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Issue Code:  VTM-1372
  Title:       Add user dashboard
  Description: Implement dashboard
  Labels:      feature, ui
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 Proceed? (Y/n): y

✅ JSON created: /tmp/gitlab-issue-20260128.json

🚀 Starting forced workflow...
[... workflow continues ...]
```

### MR Create

```
$ python gitlab_workflow.py mr -i

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 GitLab MR Create - Auto-detect Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Auto-detected:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Source: vtm-1372/342-add-dashboard
  Target: main
  Issue:  #342
  Title:  Add user dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👉 Options:
  1. Proceed (Recommended)
  2. Edit title
  3. Change target
  4. Skip issue
  5. Cancel

Choose: 1

✅ MR created !123
```

## 🔧 Troubleshooting

### 권한 에러

```bash
chmod +x shared/scripts/interactive_*.py
```

### JSON_PATH not found

→ 스크립트 출력 확인:
```bash
python shared/scripts/interactive_issue_create.py
```

### Import 에러

→ Python 3.7+ 필요:
```bash
python3 --version
```

## 📚 상세 문서

- [Interactive 상세 가이드](examples/INTERACTIVE_USAGE.md)
- [JSON 방식 가이드](examples/README.md)
- [Issue Create Skill](skills/gitlab-issue-create/SKILL.md)
- [환경 설정](shared/references/QUICK_REFERENCE.md)

---

**Version 2.0** - Interactive Edition
