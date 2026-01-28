---
name: datatable-pattern-resolver
description: "Identify and extract existing DataTable implementation patterns to provide reusable, explicit specifications. Defines 'same pattern' structurally rather than by intuition. Outputs pattern specs that downstream CREATE/APPLY skills can consume. Does NOT generate code - only interprets and defines patterns."
version: 1.0.0
updated: 2026-01-28
---

# DataTablePatternResolver

기존에 존재하는 DataTable 구현 패턴을 식별·추출하여 새로운 DataTable 생성 시 재사용 가능한 명확한 기준으로 제공한다.

**역할 정의**:
- ⭕️ "동일한 패턴"의 실체를 구조적으로 규정
- ⭕️ 감(느낌) 기반이 아닌 참조 가능한 패턴 스펙 제공
- ⭕️ 이후 CREATE / APPLY 스킬의 입력으로 사용
- ❌ 생성은 안 함, 패턴만 해석·정의

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
│ DataTablePatternResolver │ ← 이 스킬
└──────────────────────────┘
       │
       ▼
┌──────────────────┐
│ DataTableCreator │ (실제 생성 스킬)
└──────────────────┘
```

## 입력

```json
{
  "targetComponent": "DataTable",
  "referencePage": "UserListPage",
  "context": {
    "framework": "React | Vue | Angular",
    "designSystem": "InternalUI | Ant | MUI | Custom",
    "projectPath": "src/pages/UserListPage.tsx"
  }
}
```

## 출력 형식

**고정 포맷 (JSON)**:

```json
{
  "patternId": "string",
  "patternName": "string",
  "version": "string",

  "fixedElements": {
    "structure": {},
    "behavior": {},
    "style": {},
    "dataFlow": {}
  },

  "variableElements": {
    "structure": [],
    "behavior": [],
    "style": [],
    "dataFlow": []
  },

  "constraints": [],
  "dependencies": [],

  "referenceFiles": [],
  "applicability": {}
}
```

## 처리 단계

### 1. 후보 패턴 탐색

동일 컴포넌트 타입과 프레임워크/UI 규칙을 기준으로 탐색:

```yaml
searchCriteria:
  componentType: DataTable
  framework: React
  designSystem: InternalUI

searchLocations:
  - "src/components/**/Table*.tsx"
  - "src/pages/**/*List*.tsx"
  - "src/features/**/Table*.tsx"
```

### 2. 패턴 요소 분해

#### 구조 (Structure)
```yaml
fixedStructure:
  - wrapper: "div.table-container"
  - header: "TableHeader component"
  - body: "TableBody with virtualization"
  - footer: "TableFooter with pagination"

variableStructure:
  - columns: "정의 필요"
  - rowTemplate: "커스텀 가능"
  - emptyState: "커스텀 가능"
```

#### 동작 (Behavior)
```yaml
fixedBehavior:
  pagination: true
  paginationType: "server-side"
  sorting: "server-side"
  defaultPageSize: 20

variableBehavior:
  - onRowClick: "optional"
  - onSelectionChange: "optional"
  - customFilters: "optional"
```

#### 스타일 (Style)
```yaml
fixedStyle:
  rowHeight: "48px"
  headerBackground: "var(--table-header-bg)"
  borderStyle: "1px solid var(--border-color)"
  stripedRows: true

variableStyle:
  - columnWidth: "각 컬럼별 정의"
  - cellAlignment: "컬럼별 지정"
```

#### 데이터 흐름 (DataFlow)
```yaml
fixedDataFlow:
  fetchPattern: "useQuery hook"
  stateManagement: "React Query"
  errorHandling: "ErrorBoundary"
  loadingState: "Skeleton"

variableDataFlow:
  - queryKey: "페이지별 정의"
  - queryFn: "API 엔드포인트별"
  - transformResponse: "optional"
```

### 3. 패턴 ID 생성

```
{component}.{version}.{variant}

예시:
- datatable.v3.standard
- datatable.v3.selectable
- datatable.v3.editable
- datatable.v2.legacy
```

## 예시

### 입력

```json
{
  "targetComponent": "DataTable",
  "referencePage": "UserListPage",
  "context": {
    "framework": "React",
    "designSystem": "InternalUI",
    "projectPath": "src/pages/user/UserListPage.tsx"
  }
}
```

### 출력

```json
{
  "patternId": "datatable.v3.standard",
  "patternName": "Standard DataTable with Server-side Pagination",
  "version": "3.0",

  "fixedElements": {
    "structure": {
      "wrapper": "DataTableContainer",
      "header": {
        "component": "TableHeader",
        "props": ["title", "actions", "filters"]
      },
      "body": {
        "component": "TableBody",
        "virtualization": true,
        "rowComponent": "TableRow"
      },
      "footer": {
        "component": "TablePagination",
        "position": "bottom-right"
      }
    },
    "behavior": {
      "pagination": {
        "enabled": true,
        "type": "server-side",
        "defaultPageSize": 20,
        "pageSizeOptions": [10, 20, 50, 100]
      },
      "sorting": {
        "enabled": true,
        "type": "server-side",
        "multiSort": false
      },
      "selection": {
        "enabled": false,
        "type": null
      }
    },
    "style": {
      "rowHeight": "48px",
      "headerHeight": "56px",
      "stripedRows": true,
      "hoverEffect": true,
      "borderRadius": "8px",
      "theme": "light"
    },
    "dataFlow": {
      "fetchHook": "useQuery",
      "stateLibrary": "react-query",
      "cacheTime": "5min",
      "staleTime": "1min",
      "errorBoundary": true,
      "loadingState": "Skeleton",
      "emptyState": "EmptyTablePlaceholder"
    }
  },

  "variableElements": {
    "structure": [
      {
        "name": "columns",
        "type": "ColumnDefinition[]",
        "description": "테이블 컬럼 정의",
        "required": true
      },
      {
        "name": "rowKey",
        "type": "string | (row) => string",
        "description": "각 행의 고유 키",
        "required": true,
        "default": "id"
      },
      {
        "name": "headerActions",
        "type": "ReactNode",
        "description": "헤더 우측 액션 버튼들",
        "required": false
      }
    ],
    "behavior": [
      {
        "name": "onRowClick",
        "type": "(row) => void",
        "description": "행 클릭 핸들러",
        "required": false
      },
      {
        "name": "filters",
        "type": "FilterConfig[]",
        "description": "필터 설정",
        "required": false
      },
      {
        "name": "searchable",
        "type": "boolean",
        "description": "검색 기능 활성화",
        "required": false,
        "default": false
      }
    ],
    "style": [
      {
        "name": "columnWidths",
        "type": "Record<string, string | number>",
        "description": "컬럼별 너비",
        "required": false
      },
      {
        "name": "cellAlign",
        "type": "Record<string, 'left' | 'center' | 'right'>",
        "description": "셀 정렬",
        "required": false,
        "default": "left"
      }
    ],
    "dataFlow": [
      {
        "name": "queryKey",
        "type": "string[]",
        "description": "React Query 캐시 키",
        "required": true
      },
      {
        "name": "fetchFn",
        "type": "(params) => Promise<PageResponse>",
        "description": "데이터 조회 함수",
        "required": true
      },
      {
        "name": "transformResponse",
        "type": "(data) => TableData",
        "description": "응답 변환 함수",
        "required": false
      }
    ]
  },

  "constraints": [
    "페이지네이션은 반드시 서버 사이드로 구현",
    "한 페이지 최대 100개 row 제한",
    "컬럼 정의는 최소 1개 이상 필수",
    "rowKey는 고유값이어야 함"
  ],

  "dependencies": [
    "@tanstack/react-query ^5.0.0",
    "@internal/ui-components ^2.0.0",
    "react ^18.0.0"
  ],

  "referenceFiles": [
    {
      "path": "src/pages/user/UserListPage.tsx",
      "role": "primary-reference",
      "lines": "45-120"
    },
    {
      "path": "src/components/table/DataTable.tsx",
      "role": "base-component"
    },
    {
      "path": "src/hooks/useTableQuery.ts",
      "role": "data-fetching"
    }
  ],

  "applicability": {
    "recommendedFor": [
      "목록 페이지",
      "관리자 대시보드",
      "데이터 조회 화면"
    ],
    "notRecommendedFor": [
      "실시간 업데이트가 필요한 경우 (v3.realtime 사용)",
      "인라인 편집이 필요한 경우 (v3.editable 사용)",
      "트리 구조 데이터 (TreeTable 사용)"
    ]
  }
}
```

## 패턴 변형 (Variants)

동일 기본 패턴에서 파생된 변형들:

| PatternId | 설명 | 추가 고정 요소 |
|-----------|------|----------------|
| datatable.v3.standard | 기본 조회용 | - |
| datatable.v3.selectable | 행 선택 가능 | selection: { enabled: true, type: 'checkbox' } |
| datatable.v3.editable | 인라인 편집 | editing: { enabled: true, mode: 'cell' } |
| datatable.v3.expandable | 행 확장 가능 | expansion: { enabled: true } |
| datatable.v3.realtime | 실시간 업데이트 | websocket: { enabled: true } |

## 패턴 비교

두 패턴 간 차이점 분석:

```json
{
  "comparePatterns": ["datatable.v3.standard", "datatable.v2.legacy"],
  "differences": {
    "structure": [
      {
        "element": "pagination",
        "v3": "TablePagination component",
        "v2": "inline pagination div",
        "migration": "Replace with TablePagination"
      }
    ],
    "behavior": [
      {
        "element": "dataFetching",
        "v3": "useQuery hook",
        "v2": "useEffect + useState",
        "migration": "Refactor to useQuery"
      }
    ]
  }
}
```

## 패턴 검증

추출된 패턴이 유효한지 검증:

```yaml
validationChecks:
  - name: "completeness"
    description: "필수 요소가 모두 정의되었는지"
    required: true

  - name: "consistency"
    description: "고정 요소가 참조 파일들에서 일관되게 사용되는지"
    required: true

  - name: "applicability"
    description: "다른 페이지에 적용 가능한 수준으로 일반화되었는지"
    required: true

  - name: "documentation"
    description: "사람이 이해하고 설명할 수 있는 수준인지"
    required: true
```

## 성공 기준

1. **명문화**: 패턴이 사람이 설명 가능한 수준으로 정의됨
2. **재현 가능**: 동일 입력에 대해 동일 패턴 출력
3. **적용 가능**: DataTableCreator가 바로 소비 가능한 스펙
4. **분리 명확**: 고정 요소 vs 변동 요소가 명확히 구분됨

## 하지 않는 것

- ❌ 코드 생성
- ❌ 패턴 추천 (요청된 패턴만 해석)
- ❌ 패턴 변경/개선 제안
- ❌ 프레임워크 간 변환

## 학습 포인트

> "결과가 매번 다르면 패턴 정의가 안 된 상태"

이 스킬의 핵심은 **암묵지를 형식지로 변환**하는 것:

- 개발자가 "그거랑 똑같이"라고 말할 때
- 실제로 "똑같다"의 기준이 무엇인지 명시
- 그 기준을 다른 스킬/사람이 재사용 가능하게 문서화

**패턴을 명문화하는 순간이 학습임**
