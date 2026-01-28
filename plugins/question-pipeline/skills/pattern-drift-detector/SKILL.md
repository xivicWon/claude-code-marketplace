---
name: pattern-drift-detector
description: "Detect if existing code has drifted from established patterns. Compares current implementation against pattern specifications to identify deviations. Assigns drift levels (LOW/MEDIUM/HIGH) based on severity. Use for maintenance, code review, and pattern compliance checking."
version: 1.0.0
updated: 2026-01-28
---

# PatternDriftDetector

기존 코드가 확립된 패턴에서 벗어났는지 감지한다.

**역할 정의**:
- ⭕️ 현재 구현과 패턴 스펙 비교
- ⭕️ 이탈(Drift) 정도를 레벨로 분류
- ⭕️ 구체적인 이탈 지점 식별
- ❌ 수정 코드 생성 안 함
- ❌ 어느 쪽이 "맞다" 판단 안 함
- ❌ 패턴 변경 제안 안 함

## 전체 흐름에서 위치

```
[User Question]
       │
       ▼
┌─────────────────┐
│ AmbiguityScanner│
└─────────────────┘
       │
       ▼
┌─────────────────┐
│ IntentClarifier │
└─────────────────┘
       │
       ▼
┌────────────────────┐
│ QuestionNormalizer │
└────────────────────┘
       │
       ▼
┌──────────────────────────┐
│ DataTablePatternResolver │
└──────────────────────────┘
       │
       ▼
┌──────────────────┐
│ DataTableCreator │
└──────────────────┘
       │
       ▼
┌──────────────────────┐
│ PatternDriftDetector │ ← 이 스킬 (유지보수 단계)
└──────────────────────┘
```

## 입력

```json
{
  "targetFile": "src/pages/product/ProductListPage.tsx",
  "patternSpec": {
    "patternId": "datatable.v3.standard",
    "fixedElements": { ... },
    "variableElements": { ... },
    "constraints": [ ... ]
  },
  "options": {
    "checkStructure": true,
    "checkBehavior": true,
    "checkStyle": true,
    "checkDataFlow": true,
    "strictMode": false
  }
}
```

## 출력 형식

**고정 포맷 (JSON)**:

```json
{
  "targetFile": "string",
  "patternId": "string",
  "overallDriftLevel": "NONE | LOW | MEDIUM | HIGH",
  "summary": "string",

  "drifts": [
    {
      "id": "string",
      "category": "STRUCTURE | BEHAVIOR | STYLE | DATAFLOW",
      "level": "LOW | MEDIUM | HIGH",
      "element": "string",
      "expected": "any",
      "actual": "any",
      "location": {
        "line": "number",
        "column": "number"
      },
      "description": "string"
    }
  ],

  "compliance": {
    "structure": { "score": "number", "total": "number" },
    "behavior": { "score": "number", "total": "number" },
    "style": { "score": "number", "total": "number" },
    "dataFlow": { "score": "number", "total": "number" }
  },

  "constraintViolations": [
    {
      "constraint": "string",
      "violated": "boolean",
      "details": "string"
    }
  ]
}
```

## Drift Level 정의

| Level | 기준 | 영향도 | 예시 |
|-------|------|--------|------|
| **NONE** | 패턴과 완전 일치 | - | - |
| **LOW** | 사소한 차이, 기능 영향 없음 | 코드 스타일 | 변수명 다름, 주석 누락 |
| **MEDIUM** | 구조적 차이, 기능은 동작 | 유지보수성 | 다른 컴포넌트 사용, 다른 훅 사용 |
| **HIGH** | 핵심 패턴 위반, 동작 다를 수 있음 | 기능/안정성 | 서버사이드 → 클라이언트 페이지네이션 |

## 카테고리별 검사 항목

### STRUCTURE (구조)

```yaml
검사 항목:
  - wrapper 컴포넌트 일치
  - 자식 컴포넌트 구성
  - 컴포넌트 계층 구조
  - props 전달 방식

예시 Drift:
  - expected: "TablePagination"
    actual: "CustomPagination"
    level: MEDIUM
```

### BEHAVIOR (동작)

```yaml
검사 항목:
  - 이벤트 핸들러 패턴
  - 상태 관리 방식
  - 비동기 처리 방식
  - 에러 핸들링

예시 Drift:
  - expected: "server-side pagination"
    actual: "client-side pagination"
    level: HIGH
```

### STYLE (스타일)

```yaml
검사 항목:
  - CSS 클래스명
  - 인라인 스타일
  - 테마 변수 사용
  - 레이아웃 구조

예시 Drift:
  - expected: "var(--table-header-bg)"
    actual: "#f5f5f5"
    level: LOW
```

### DATAFLOW (데이터 흐름)

```yaml
검사 항목:
  - 데이터 페칭 훅
  - 캐싱 전략
  - 상태 라이브러리
  - 응답 변환

예시 Drift:
  - expected: "useQuery"
    actual: "useEffect + fetch"
    level: HIGH
```

## 예시

### 입력

```json
{
  "targetFile": "src/pages/product/ProductListPage.tsx",
  "patternSpec": {
    "patternId": "datatable.v3.standard",
    "fixedElements": {
      "structure": {
        "wrapper": "DataTableContainer",
        "header": { "component": "TableHeader" },
        "footer": { "component": "TablePagination" }
      },
      "behavior": {
        "pagination": { "type": "server-side" }
      },
      "style": {
        "rowHeight": "48px",
        "stripedRows": true
      },
      "dataFlow": {
        "fetchHook": "useQuery",
        "loadingState": "Skeleton"
      }
    },
    "constraints": [
      "페이지네이션은 반드시 서버 사이드로 구현"
    ]
  }
}
```

### 출력 (Drift 발견)

```json
{
  "targetFile": "src/pages/product/ProductListPage.tsx",
  "patternId": "datatable.v3.standard",
  "overallDriftLevel": "MEDIUM",
  "summary": "2개의 MEDIUM drift, 1개의 LOW drift 발견. 핵심 패턴은 유지되나 일부 구현이 다름.",

  "drifts": [
    {
      "id": "drift-001",
      "category": "STRUCTURE",
      "level": "MEDIUM",
      "element": "footer.component",
      "expected": "TablePagination",
      "actual": "CustomPagination",
      "location": { "line": 45, "column": 8 },
      "description": "패턴에 정의된 TablePagination 대신 CustomPagination 사용"
    },
    {
      "id": "drift-002",
      "category": "DATAFLOW",
      "level": "MEDIUM",
      "element": "loadingState",
      "expected": "Skeleton",
      "actual": "Spinner",
      "location": { "line": 28, "column": 12 },
      "description": "로딩 상태 표시에 Skeleton 대신 Spinner 사용"
    },
    {
      "id": "drift-003",
      "category": "STYLE",
      "level": "LOW",
      "element": "rowHeight",
      "expected": "48px",
      "actual": "52px",
      "location": { "line": 67, "column": 4 },
      "description": "행 높이가 패턴 정의(48px)와 다름(52px)"
    }
  ],

  "compliance": {
    "structure": { "score": 4, "total": 5 },
    "behavior": { "score": 3, "total": 3 },
    "style": { "score": 2, "total": 3 },
    "dataFlow": { "score": 3, "total": 4 }
  },

  "constraintViolations": [
    {
      "constraint": "페이지네이션은 반드시 서버 사이드로 구현",
      "violated": false,
      "details": "서버 사이드 페이지네이션 확인됨"
    }
  ]
}
```

### 출력 (심각한 Drift)

```json
{
  "targetFile": "src/pages/legacy/OldProductPage.tsx",
  "patternId": "datatable.v3.standard",
  "overallDriftLevel": "HIGH",
  "summary": "핵심 패턴 위반 발견. 서버사이드 페이지네이션 제약 조건 미준수.",

  "drifts": [
    {
      "id": "drift-001",
      "category": "BEHAVIOR",
      "level": "HIGH",
      "element": "pagination.type",
      "expected": "server-side",
      "actual": "client-side",
      "location": { "line": 34, "column": 6 },
      "description": "클라이언트 사이드 페이지네이션 사용 - 대량 데이터 시 성능 문제 가능"
    },
    {
      "id": "drift-002",
      "category": "DATAFLOW",
      "level": "HIGH",
      "element": "fetchHook",
      "expected": "useQuery",
      "actual": "useEffect + useState",
      "location": { "line": 15, "column": 2 },
      "description": "React Query 대신 직접 상태 관리 - 캐싱, 리페치 기능 누락"
    }
  ],

  "compliance": {
    "structure": { "score": 3, "total": 5 },
    "behavior": { "score": 1, "total": 3 },
    "style": { "score": 2, "total": 3 },
    "dataFlow": { "score": 1, "total": 4 }
  },

  "constraintViolations": [
    {
      "constraint": "페이지네이션은 반드시 서버 사이드로 구현",
      "violated": true,
      "details": "클라이언트 사이드 페이지네이션 감지됨 (line 34)"
    }
  ]
}
```

### 출력 (Drift 없음)

```json
{
  "targetFile": "src/pages/user/UserListPage.tsx",
  "patternId": "datatable.v3.standard",
  "overallDriftLevel": "NONE",
  "summary": "패턴과 완전히 일치. drift 없음.",

  "drifts": [],

  "compliance": {
    "structure": { "score": 5, "total": 5 },
    "behavior": { "score": 3, "total": 3 },
    "style": { "score": 3, "total": 3 },
    "dataFlow": { "score": 4, "total": 4 }
  },

  "constraintViolations": []
}
```

## 사용 시점

1. **코드 리뷰**: PR에서 패턴 준수 여부 확인
2. **정기 점검**: 프로젝트 전체 패턴 일관성 검사
3. **마이그레이션**: 기존 코드의 패턴 이탈 정도 파악
4. **문서화**: 현재 코드와 패턴 간 차이점 기록
5. **디버깅**: "왜 이 페이지만 다르게 동작하지?" 원인 파악

## Drift Level 결정 로직

```yaml
HIGH 조건 (하나라도 해당):
  - constraint 위반
  - 핵심 behavior 변경 (pagination type, data fetching)
  - 보안/성능 영향 가능성

MEDIUM 조건:
  - structure 컴포넌트 대체
  - dataFlow 훅/라이브러리 변경
  - 기능은 동작하나 유지보수성 저하

LOW 조건:
  - style 수치 미세 차이
  - 변수명/함수명 차이
  - 주석/문서 누락
```

## 옵션 설명

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| checkStructure | true | 구조 요소 검사 |
| checkBehavior | true | 동작 패턴 검사 |
| checkStyle | true | 스타일 규칙 검사 |
| checkDataFlow | true | 데이터 흐름 검사 |
| strictMode | false | true 시 LOW도 경고 처리 |

## 하지 않는 것

- ❌ **수정 코드 생성**: drift 감지만, 수정은 별도 스킬
- ❌ **판단**: "현재 코드가 틀렸다" 같은 판단
- ❌ **추천**: "이렇게 바꾸면 좋겠다" 제안
- ❌ **패턴 수정**: 현재 코드에 맞춰 패턴 변경
- ❌ **무시 처리**: 발견된 drift를 임의로 필터링

## 성공 기준

1. **완전 탐지**: 패턴과 다른 모든 부분 식별
2. **정확한 레벨링**: drift 심각도 적절히 분류
3. **구체적 위치**: line/column 정보 제공
4. **객관적 비교**: expected vs actual 명확히 제시
5. **재현 가능**: 동일 입력 → 동일 결과

## 학습 포인트

> "Drift는 '잘못'이 아니라 '다름'이다"

이 스킬은 판단하지 않는다:
- 의도적 변경일 수 있음
- 새로운 요구사항 반영일 수 있음
- 패턴 자체가 업데이트 필요할 수 있음

**"다름을 발견하고 기록하는 것"이 이 스킬의 역할**

이후 판단과 조치는 사람 또는 다른 스킬의 영역이다.
