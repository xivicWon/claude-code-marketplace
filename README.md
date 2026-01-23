# Claude Code 마켓플레이스

Claude Code를 위한 커스텀 플러그인 마켓플레이스입니다.

## 개요

이 저장소는 개발 워크플로우 자동화를 위한 Claude Code 플러그인을 호스팅합니다.

## 마켓플레이스

### baubau

**제작자:** xivic
**버전:** 1.0.0
**목적:** 개발 워크플로우 자동화

#### 포함된 플러그인

##### gitlab-collaboration

GitLab 워크플로우 자동화 플러그인입니다.

**주요 기능:**
- GitLab 이슈 생성 및 관리
- 브랜치 자동 생성 및 관리
- Merge Request 워크플로우 자동화
- 대화형 또는 JSON 파일 기반 워크플로우

**제공 스킬:**
- `/gitlab-workflow` - GitLab 워크플로우 자동화

**사용 예시:**
```bash
# 환경 검증
/gitlab-workflow doctor

# 이슈 생성
/gitlab-workflow create

# 이슈 업데이트
/gitlab-workflow update

# Merge Request 생성
/gitlab-workflow mr
```

## 설치

```bash
# Claude Code 설정에 마켓플레이스 추가 (.claude/settings.json)
{
  "marketplaces": [
    {
      "name": "baubau",
      "url": "https://raw.githubusercontent.com/your-username/marketplaces/main/baubau"
    }
  ]
}
```

## 라이선스

MIT License
