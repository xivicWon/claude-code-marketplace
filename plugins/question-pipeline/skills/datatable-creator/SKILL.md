---
name: datatable-creator
description: "Generate DataTable code from confirmed pattern specifications. Performs pure transformation without judgment or interpretation. Takes pattern specs from DataTablePatternResolver and produces implementation code. Fails explicitly on constraint violations or missing variable elements."
version: 1.0.0
updated: 2026-01-28
---

# DataTableCreator

확정된 패턴 스펙을 코드로 변환한다.

**역할 정의**:
- ⭕️ 패턴 스펙 → 실행 가능한 코드 변환
- ⭕️ 고정 요소는 그대로 적용
- ⭕️ 가변 요소는 입력값으로 채움
- ❌ 판단/해석 하지 않음
- ❌ 패턴 스펙에 없는 것을 추가하지 않음
- ❌ "더 나은" 방식 제안 안 함

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
│ DataTableCreator │ ← 이 스킬
└──────────────────┘
       │
       ▼
   [Generated Code]
```

## 입력

```json
{
  "patternSpec": {
    "patternId": "datatable.v3.standard",
    "fixedElements": { ... },
    "variableElements": { ... },
    "constraints": [ ... ],
    "dependencies": [ ... ]
  },
  "variableValues": {
    "columns": [ ... ],
    "queryKey": [ ... ],
    "fetchFn": "...",
    "rowKey": "id"
  },
  "targetPath": "src/pages/product/ProductListPage.tsx"
}
```

## 출력 형식

**고정 포맷 (JSON)**:

```json
{
  "status": "SUCCESS | FAILED",
  "generatedCode": {
    "mainFile": {
      "path": "string",
      "content": "string"
    },
    "additionalFiles": [
      {
        "path": "string",
        "content": "string",
        "reason": "string"
      }
    ]
  },
  "appliedPattern": {
    "patternId": "string",
    "fixedElementsApplied": [ ... ],
    "variableElementsFilled": [ ... ]
  },
  "validationResult": {
    "passed": true,
    "constraintsChecked": [ ... ]
  },
  "error": null
}
```

### 실패 시 출력

```json
{
  "status": "FAILED",
  "generatedCode": null,
  "appliedPattern": null,
  "validationResult": {
    "passed": false,
    "failedConstraints": [
      {
        "constraint": "string",
        "reason": "string",
        "requiredAction": "string"
      }
    ]
  },
  "error": {
    "type": "CONSTRAINT_VIOLATION | MISSING_VARIABLE | INVALID_INPUT",
    "message": "string",
    "details": { ... }
  }
}
```

## 처리 규칙

### 1. 고정 요소 적용

패턴 스펙의 `fixedElements`는 그대로 코드에 반영:

```yaml
# 입력 (fixedElements)
structure:
  wrapper: "DataTableContainer"
  header:
    component: "TableHeader"
  footer:
    component: "TablePagination"

# 출력 (그대로 적용)
<DataTableContainer>
  <TableHeader ... />
  <TableBody ... />
  <TablePagination ... />
</DataTableContainer>
```

### 2. 가변 요소 채우기

패턴 스펙의 `variableElements`는 입력된 값으로 채움:

```yaml
# variableElements 정의
- name: "columns"
  type: "ColumnDefinition[]"
  required: true

# variableValues 입력
columns:
  - key: "name"
    title: "이름"
    width: 200
  - key: "email"
    title: "이메일"

# 출력 (입력값 적용)
const columns = [
  { key: 'name', title: '이름', width: 200 },
  { key: 'email', title: '이메일' }
];
```

### 3. 제약 조건 검증

생성 전 모든 `constraints` 검증:

```yaml
constraints:
  - "컬럼 정의는 최소 1개 이상 필수"
  - "rowKey는 고유값이어야 함"
  - "페이지네이션은 반드시 서버 사이드"

# 위반 시 즉시 실패
```

### 4. 필수 가변 요소 확인

`required: true`인 가변 요소가 누락되면 실패:

```yaml
variableElements:
  - name: "queryKey"
    required: true
  - name: "fetchFn"
    required: true

# queryKey 누락 시
error:
  type: MISSING_VARIABLE
  message: "필수 가변 요소 'queryKey'가 누락됨"
```

## 예시

### 입력

```json
{
  "patternSpec": {
    "patternId": "datatable.v3.standard",
    "fixedElements": {
      "structure": {
        "wrapper": "DataTableContainer",
        "header": { "component": "TableHeader" },
        "body": { "component": "TableBody", "virtualization": true },
        "footer": { "component": "TablePagination" }
      },
      "behavior": {
        "pagination": { "type": "server-side", "defaultPageSize": 20 },
        "sorting": { "type": "server-side" }
      },
      "dataFlow": {
        "fetchHook": "useQuery",
        "loadingState": "Skeleton",
        "errorBoundary": true
      }
    },
    "variableElements": {
      "structure": [
        { "name": "columns", "required": true },
        { "name": "rowKey", "required": true, "default": "id" }
      ],
      "dataFlow": [
        { "name": "queryKey", "required": true },
        { "name": "fetchFn", "required": true }
      ]
    },
    "constraints": [
      "컬럼 정의는 최소 1개 이상 필수"
    ]
  },
  "variableValues": {
    "columns": [
      { "key": "name", "title": "상품명", "width": 200 },
      { "key": "price", "title": "가격", "width": 100, "align": "right" },
      { "key": "stock", "title": "재고", "width": 80, "align": "center" }
    ],
    "rowKey": "productId",
    "queryKey": ["products", "list"],
    "fetchFn": "productApi.getList"
  },
  "targetPath": "src/pages/product/ProductListPage.tsx"
}
```

### 출력 (성공)

```json
{
  "status": "SUCCESS",
  "generatedCode": {
    "mainFile": {
      "path": "src/pages/product/ProductListPage.tsx",
      "content": "import React from 'react';\nimport { useQuery } from '@tanstack/react-query';\nimport {\n  DataTableContainer,\n  TableHeader,\n  TableBody,\n  TablePagination,\n  Skeleton\n} from '@internal/ui-components';\nimport { productApi } from '@/api/product';\n\nconst columns = [\n  { key: 'name', title: '상품명', width: 200 },\n  { key: 'price', title: '가격', width: 100, align: 'right' },\n  { key: 'stock', title: '재고', width: 80, align: 'center' }\n];\n\nexport function ProductListPage() {\n  const [pagination, setPagination] = useState({ page: 1, pageSize: 20 });\n  const [sorting, setSorting] = useState({ field: null, order: null });\n\n  const { data, isLoading, error } = useQuery({\n    queryKey: ['products', 'list', pagination, sorting],\n    queryFn: () => productApi.getList({ ...pagination, ...sorting })\n  });\n\n  if (isLoading) return <Skeleton />;\n  if (error) throw error;\n\n  return (\n    <DataTableContainer>\n      <TableHeader title=\"상품 목록\" />\n      <TableBody\n        columns={columns}\n        data={data.items}\n        rowKey=\"productId\"\n        virtualization\n        onSort={setSorting}\n      />\n      <TablePagination\n        current={pagination.page}\n        pageSize={pagination.pageSize}\n        total={data.total}\n        onChange={setPagination}\n      />\n    </DataTableContainer>\n  );\n}\n"
    },
    "additionalFiles": []
  },
  "appliedPattern": {
    "patternId": "datatable.v3.standard",
    "fixedElementsApplied": [
      "DataTableContainer wrapper",
      "TableHeader component",
      "TableBody with virtualization",
      "TablePagination component",
      "server-side pagination",
      "useQuery hook",
      "Skeleton loading state"
    ],
    "variableElementsFilled": [
      { "name": "columns", "value": "3 columns defined" },
      { "name": "rowKey", "value": "productId" },
      { "name": "queryKey", "value": "['products', 'list']" },
      { "name": "fetchFn", "value": "productApi.getList" }
    ]
  },
  "validationResult": {
    "passed": true,
    "constraintsChecked": [
      { "constraint": "컬럼 정의는 최소 1개 이상 필수", "status": "PASSED" }
    ]
  },
  "error": null
}
```

### 입력 (실패 케이스 - 필수 요소 누락)

```json
{
  "patternSpec": { ... },
  "variableValues": {
    "columns": [],
    "rowKey": "id"
  },
  "targetPath": "src/pages/empty/EmptyPage.tsx"
}
```

### 출력 (실패)

```json
{
  "status": "FAILED",
  "generatedCode": null,
  "appliedPattern": null,
  "validationResult": {
    "passed": false,
    "failedConstraints": [
      {
        "constraint": "컬럼 정의는 최소 1개 이상 필수",
        "reason": "columns 배열이 비어있음",
        "requiredAction": "최소 1개의 컬럼 정의 필요"
      }
    ],
    "missingVariables": [
      { "name": "queryKey", "required": true },
      { "name": "fetchFn", "required": true }
    ]
  },
  "error": {
    "type": "CONSTRAINT_VIOLATION",
    "message": "패턴 제약 조건 위반으로 코드 생성 불가",
    "details": {
      "failedConstraints": 1,
      "missingRequiredVariables": 2
    }
  }
}
```

## 실패 조건

다음 조건에서 즉시 실패 (코드 생성하지 않음):

| 조건 | 에러 타입 | 설명 |
|------|-----------|------|
| 제약 조건 위반 | CONSTRAINT_VIOLATION | constraints 중 하나라도 위반 |
| 필수 가변 요소 누락 | MISSING_VARIABLE | required: true인 요소 값 없음 |
| 잘못된 입력 형식 | INVALID_INPUT | 타입 불일치, 형식 오류 |
| 패턴 스펙 손상 | INVALID_PATTERN | patternSpec 구조 오류 |

## 하지 않는 것

- ❌ **판단**: "이 방식이 더 좋다" 류의 의견
- ❌ **해석**: 입력에 없는 의미 추론
- ❌ **추가**: 패턴에 정의되지 않은 요소 삽입
- ❌ **생략**: 고정 요소 중 일부 누락
- ❌ **변형**: 패턴 스펙과 다른 구현
- ❌ **추천**: 다른 패턴이나 방식 제안

## 성공 기준

1. **결정론적**: 동일 입력 → 동일 출력
2. **완전 적용**: 모든 fixedElements가 코드에 반영됨
3. **정확한 채움**: variableValues가 올바른 위치에 삽입됨
4. **명시적 실패**: 문제 시 애매하게 넘어가지 않고 즉시 실패
5. **투명한 결과**: 무엇이 적용되었는지 appliedPattern에 명시

## 학습 포인트

> "이 스킬은 변환기(Transformer)이지 생성기(Generator)가 아니다"

- 입력(패턴 스펙 + 값)이 완전하면 → 코드 생성
- 입력이 불완전하면 → 명시적 실패
- 판단이 필요한 상황 → 이 스킬의 영역 밖

**패턴 스펙이 명확하면 누가 실행해도 같은 결과**
