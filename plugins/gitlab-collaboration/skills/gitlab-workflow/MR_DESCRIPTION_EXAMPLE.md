# MR Description 자동 생성 예시

이 문서는 `/gitlab-workflow mr` 명령어로 생성되는 MR description의 실제 예시를 보여줍니다.

## 생성되는 MR Description 구조

### 1. Issue Summary (이슈 요약)
Issue 번호, 제목, 상태, 라벨 정보를 표시합니다.

### 2. Requirements (요구사항)
Issue description에 작성된 전체 요구사항을 그대로 포함합니다.

### 3. Implementation (구현 내용)
커밋 메시지를 분석하여 실제로 구현한 내용을 요약합니다.

### 4. Changes Summary (변경 통계)
파일 변경, 추가/삭제된 라인 수 등 통계 정보를 표시합니다.

### 5. Detailed Commit History (상세 커밋 히스토리)
모든 커밋의 세부 정보를 표시합니다.

---

## 실제 생성 예시

아래는 실제로 생성되는 MR description의 예시입니다:

```markdown
# 📋 Issue Summary

**Issue**: #342 - 사용자 대시보드 추가
**Status**: opened
**Labels**: feature, dashboard, ui
**URL**: http://192.168.210.103:90/withvtm_2.0/withvtm-fe/-/issues/342

## 📝 Requirements (요구사항)

사용자 활동을 모니터링할 수 있는 대시보드를 추가합니다.

### 필수 기능
- 일일 활성 사용자(DAU) 차트
- 세션 통계 위젯
- 실시간 데이터 업데이트

### 기술 요구사항
- Vue 3 Composition API 사용
- Vuetify 3 컴포넌트 활용
- Chart.js로 차트 구현
- 반응형 레이아웃

## ✅ Implementation (구현 내용)

### 주요 구현 사항:

1. 사용자 대시보드 기본 레이아웃 구현
2. DAU 차트 컴포넌트 추가
3. 세션 통계 위젯 구현
4. 실시간 데이터 업데이트 로직 추가
5. 반응형 레이아웃 적용

## 📊 Changes Summary

- **Files changed**: 8
- **Insertions**: +387
- **Deletions**: -45
- **Total commits**: 5

## 📜 Detailed Commit History

### 1. VTM-1372 feat: 사용자 대시보드 기본 레이아웃 구현
- **Commit**: `a1b2c3d4`
- **Author**: 홍길동
- **Date**: Thu Jan 23 14:30:00 2026 +0900

Vue 3 Composition API를 사용하여 대시보드 페이지 구조 생성
- UserDashboard.vue 컴포넌트 추가
- 라우팅 설정
- 기본 레이아웃 구성

---

### 2. VTM-1372 feat: DAU 차트 컴포넌트 추가
- **Commit**: `b2c3d4e5`
- **Author**: 홍길동
- **Date**: Thu Jan 23 15:45:00 2026 +0900

Chart.js를 활용한 일일 활성 사용자 차트 구현
- DAUChart.vue 컴포넌트 생성
- API 연동 로직
- 차트 옵션 설정

---

### 3. VTM-1372 feat: 세션 통계 위젯 구현
- **Commit**: `c3d4e5f6`
- **Author**: 홍길동
- **Date**: Thu Jan 23 16:20:00 2026 +0900

실시간 세션 통계를 보여주는 위젯 추가
- SessionStats.vue 컴포넌트
- 평균 세션 시간 표시
- 활성 세션 수 표시

---

### 4. VTM-1372 feat: 실시간 데이터 업데이트 로직 추가
- **Commit**: `d4e5f6g7`
- **Author**: 홍길동
- **Date**: Thu Jan 23 17:10:00 2026 +0900

10초마다 자동으로 데이터를 갱신하는 로직 구현
- setInterval을 사용한 폴링
- API 호출 최적화
- 에러 처리

---

### 5. VTM-1372 refactor: 반응형 레이아웃 적용
- **Commit**: `e5f6g7h8`
- **Author**: 홍길동
- **Date**: Thu Jan 23 17:45:00 2026 +0900

모바일/태블릿/데스크톱에서 최적화된 레이아웃 제공
- Vuetify Grid 시스템 활용
- 반응형 브레이크포인트 설정
- 모바일 UI 개선

---

Closes #342
```

---

## 주요 특징

### 1. Requirements와 Implementation 매핑
- **Requirements**: Issue에 작성된 "무엇을 할 것인가"
- **Implementation**: 커밋에서 추출한 "무엇을 했는가"
- 두 섹션을 비교하여 요구사항이 어떻게 구현되었는지 명확히 확인 가능

### 2. Conventional Commits 자동 처리
- `feat:`, `fix:`, `refactor:` 등의 prefix를 자동으로 제거
- 깔끔한 구현 요약 제공
- 상세 커밋 히스토리에는 원본 메시지 유지

### 3. 완전한 추적 가능성
- Issue의 요구사항부터 최종 구현까지 전체 흐름 추적
- 리뷰어가 요구사항 대비 구현 내용을 쉽게 확인
- 문서화 자동화로 일관성 유지

### 4. 자동 Issue Close
- MR 하단의 `Closes #342` 키워드
- MR이 머지되면 자동으로 Issue가 close됨
- 수동 작업 불필요

---

## 사용 팁

### 좋은 Issue Description 작성
MR description의 Requirements 섹션은 Issue description을 그대로 가져오므로, Issue를 작성할 때 명확하고 구조화된 요구사항을 작성하는 것이 중요합니다:

```markdown
## 개요
[기능 설명]

## 필수 기능
- 기능 1
- 기능 2
- 기능 3

## 기술 요구사항
- 요구사항 1
- 요구사항 2

## UI/UX
- UI 요구사항
```

### 의미 있는 커밋 메시지 작성
Implementation 섹션의 품질은 커밋 메시지에 달려있습니다:

```bash
# ✅ 좋은 예
git commit -m "VTM-1372 feat: 사용자 대시보드 기본 레이아웃 구현"
git commit -m "VTM-1372 feat: DAU 차트 컴포넌트 추가"

# ❌ 나쁜 예
git commit -m "update"
git commit -m "fix"
```

### Issue 번호는 필수
Issue 번호를 제공하지 않으면 Requirements 섹션이 생성되지 않습니다. 가능하면 항상 Issue와 연결하여 완전한 MR description을 생성하세요.

---

## 비교: Before vs After

### Before (Issue 없이)
```markdown
## 📊 Changes Summary

- **Files changed**: 8
- **Insertions**: +387
- **Deletions**: -45
- **Total commits**: 5

## 📜 Detailed Commit History
[커밋 목록...]
```

### After (Issue 포함) ⭐
```markdown
# 📋 Issue Summary
[Issue 정보]

## 📝 Requirements (요구사항)
[Issue description 전체]

## ✅ Implementation (구현 내용)
[커밋 기반 구현 요약]

## 📊 Changes Summary
[통계]

## 📜 Detailed Commit History
[커밋 목록...]

Closes #342
```

Issue를 포함하면 **요구사항 → 구현 → 상세 내역**의 완전한 스토리를 제공합니다!
