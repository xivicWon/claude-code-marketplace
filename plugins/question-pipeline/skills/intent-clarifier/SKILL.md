---
name: intent-clarifier
description: "Identify the core intent and task type from user questions. Supports two modes: EXECUTION path (after AmbiguityScanner) and DECISION path (before AmbiguityScanner, without ambiguousPoints). Allows 'intent candidates' even when ambiguous. Trigger when you need to understand 'what is this question trying to do'."
version: 1.1.0
updated: 2026-01-28
---

# IntentClarifier

질문의 핵심 의도와 작업 유형을 명확히 식별한다.

**원칙**:
- ⭕️ 모호해도 "의도 후보"까지는 허용
- ⭕️ 불확실하면 confidenceLevel을 낮춘다
- ❌ 세부 설계 하지 않음
- ❌ 모호성 해소 시도 하지 않음

## 입력

```yaml
originalQuestion: string           # 사용자의 원본 질문
ambiguousPoints:                   # AmbiguityScanner 출력 (선택)
  - term: string
    type: string
    reason: string
    requiredDecisions: [string]
```

## 식별 대상

### 1. 작업 목적 (primaryAction)

| Action | 설명 | 키워드 |
|--------|------|--------|
| QUERY | 정보 조회/확인 | 확인해줘, 찾아줘, 어디있어, 뭐야 |
| CREATE | 새로 생성 | 만들어줘, 생성해줘, 추가해줘 |
| MODIFY | 기존 수정 | 수정해줘, 바꿔줘, 고쳐줘, 변경해줘 |
| DELETE | 삭제 | 삭제해줘, 제거해줘, 없애줘 |
| ANALYZE | 분석/검토 | 분석해줘, 검토해줘, 리뷰해줘 |
| TRANSFORM | 형식 변환 | 변환해줘, 바꿔줘, 포맷해줘 |
| EXPLAIN | 설명 요청 | 설명해줘, 알려줘, 왜 그래 |
| EXECUTE | 실행/수행 | 실행해줘, 돌려줘, 테스트해줘 |
| COMPARE | 비교 | 비교해줘, 차이가 뭐야, 뭐가 다르지 |
| ORGANIZE | 정리/구조화 | 정리해줘, 구조화해줘, 리팩토링 |

### 2. 대상 객체 (targetObject)

| Object | 설명 | 예시 |
|--------|------|------|
| UI | 화면/컴포넌트 | 버튼, 페이지, 모달, 테이블 |
| DATA | 데이터/모델 | DB, API 응답, JSON, 상태 |
| LOGIC | 비즈니스 로직 | 함수, 알고리즘, 규칙 |
| CODE | 코드 전반 | 파일, 클래스, 모듈 |
| CONFIG | 설정 | 환경변수, 설정파일, 옵션 |
| DOC | 문서 | README, 스펙, 주석 |
| STYLE | 스타일 | CSS, 테마, 레이아웃 |
| TEST | 테스트 | 테스트코드, 테스트케이스 |
| INFRA | 인프라 | Docker, CI/CD, 배포 |
| UNKNOWN | 불명확 | 대상 특정 불가 |

### 3. 기대 산출물 유형 (outputType)

| Type | 설명 | 예시 |
|------|------|------|
| CODE | 실행 가능한 코드 | .ts, .vue, .java, .py |
| SPEC | 명세/스펙 문서 | 요구사항, API 스펙 |
| DOC | 일반 문서 | 설명서, 가이드, README |
| JSON | 구조화된 데이터 | 설정, 스키마, 응답 |
| DIAGRAM | 다이어그램 | 시퀀스, ERD, 플로우차트 |
| REPORT | 분석 리포트 | 코드리뷰, 성능분석 |
| ANSWER | 단순 응답 | 설명, 확인 결과 |
| COMMAND | 실행 명령 | CLI, 스크립트 |
| MIXED | 복합 산출물 | 코드 + 문서 |
| UNKNOWN | 불명확 | 산출물 특정 불가 |

## 출력 형식

**고정 포맷 (YAML)**:

```yaml
intent:
  primaryAction: string      # 작업 목적
  targetObject: string       # 대상 객체
  outputType: string         # 기대 산출물
  summary: string            # 한 문장 요약
confidenceLevel: HIGH | MEDIUM | LOW
confidenceReason: string     # 신뢰도 판단 근거
```

### 신뢰도 기준

| Level | 조건 |
|-------|------|
| HIGH | 모든 요소가 명확히 식별됨, 모호성 없음 |
| MEDIUM | 1-2개 요소 추론 필요, 합리적 추론 가능 |
| LOW | 핵심 요소 불명확, 여러 해석 가능 |

## 예시

### 입력

```yaml
originalQuestion: "로그인 페이지를 다른 서비스처럼 깔끔하게 만들어줘"
ambiguousPoints:
  - term: "다른 서비스"
    type: REFERENCE
    reason: 어떤 서비스를 참조하는지 특정되지 않음
  - term: "깔끔하게"
    type: CRITERIA
    reason: 주관적 판단 기준
  - term: "만들어줘"
    type: OUTPUT
    reason: 산출물 형태 불명확
```

### 출력

```yaml
intent:
  primaryAction: CREATE
  targetObject: UI
  outputType: CODE
  summary: "로그인 페이지 UI를 새로 생성하거나 개선하는 코드 작성"
confidenceLevel: MEDIUM
confidenceReason: "작업(CREATE)과 대상(UI-로그인페이지)은 명확하나, 참조 기준과 스타일 기준이 모호하여 구체적 구현 방향 불확실"
```

### 입력

```yaml
originalQuestion: "API 응답 시간이 왜 느린지 확인해줘"
ambiguousPoints: []
```

### 출력

```yaml
intent:
  primaryAction: ANALYZE
  targetObject: DATA
  outputType: REPORT
  summary: "API 응답 시간 지연 원인 분석 및 리포트 제공"
confidenceLevel: HIGH
confidenceReason: "작업(분석), 대상(API 응답), 산출물(분석 결과)이 모두 명확"
```

### 입력

```yaml
originalQuestion: "이거 좀 고쳐줘"
ambiguousPoints:
  - term: "이거"
    type: REFERENCE
    reason: 대상 특정 불가
  - term: "좀"
    type: SCOPE
    reason: 범위 불명확
  - term: "고쳐줘"
    type: OUTPUT
    reason: 수정 방식 불명확
```

### 출력

```yaml
intent:
  primaryAction: MODIFY
  targetObject: UNKNOWN
  outputType: UNKNOWN
  summary: "특정되지 않은 대상을 수정"
confidenceLevel: LOW
confidenceReason: "작업 유형(수정)만 식별 가능, 대상과 산출물 모두 불명확하여 실행 불가"
```

## 복합 의도 처리

하나의 질문에 여러 의도가 포함된 경우:

### 입력

```yaml
originalQuestion: "사용자 목록 API 만들고 문서도 작성해줘"
```

### 출력

```yaml
intent:
  primaryAction: CREATE
  targetObject: CODE
  outputType: MIXED
  summary: "사용자 목록 API 코드 생성 및 관련 문서 작성"
confidenceLevel: HIGH
confidenceReason: "복합 작업이나 각 요소가 명확함 (API 코드 + 문서)"
subIntents:
  - primaryAction: CREATE
    targetObject: DATA
    outputType: CODE
    summary: "사용자 목록 API 엔드포인트 생성"
  - primaryAction: CREATE
    targetObject: DOC
    outputType: DOC
    summary: "API 문서 작성"
```

## 경로별 사용 방식

QuestionClassifier의 분류 결과에 따라 IntentClarifier의 사용 방식이 달라진다.

### EXECUTION 경로 (AmbiguityScanner → IntentClarifier)

```
[User Question]
       │
       ▼
┌─────────────────┐
│ AmbiguityScanner│ → ambiguousPoints (full mode)
└─────────────────┘
       │
       ▼
┌─────────────────┐
│ IntentClarifier │ → intent + confidenceLevel
└─────────────────┘
```

- AmbiguityScanner의 `ambiguousPoints`를 입력으로 받음
- `ambiguousPoints`가 많을수록 `confidenceLevel` 하락
- OUTPUT 유형 모호성 → `outputType` 불확실
- REFERENCE 유형 모호성 → `targetObject` 불확실
- SCOPE/CRITERIA 모호성 → 실행 가능하나 결과 품질 불확실

### DECISION 경로 (IntentClarifier → AmbiguityScanner)

```
[User Question]
       │
       ▼
┌─────────────────┐
│ IntentClarifier │ → intent (ambiguousPoints 없이 실행)
└─────────────────┘
       │
       ▼
┌─────────────────┐
│ AmbiguityScanner│ → light mode (결정 방해 요소만)
└─────────────────┘
```

**DECISION 경로에서의 특징**:

1. **ambiguousPoints 없이 실행**: 모호성 분석 전에 의도부터 파악
2. **COMPARE/ANALYZE 위주**: 결정 질문은 대부분 비교/분석 의도
3. **outputType = ANSWER**: 결정 질문의 산출물은 대부분 판단/조언
4. **confidenceLevel 산정 기준 완화**: 모호성 정보 없이도 의도 파악에 집중

**DECISION 경로 입력 형식**:

```yaml
originalQuestion: string           # 사용자의 원본 질문
ambiguousPoints: []                # 빈 배열 또는 생략
context:
  questionType: DECISION           # 경로 힌트 (선택)
```

**DECISION 경로 예시**:

입력:
```yaml
originalQuestion: "Redux랑 Context 중에 뭐가 나아?"
ambiguousPoints: []
context:
  questionType: DECISION
```

출력:
```yaml
intent:
  primaryAction: COMPARE
  targetObject: CODE
  outputType: ANSWER
  summary: "Redux와 Context API의 비교 분석 및 상황별 권장 제공"
confidenceLevel: HIGH
confidenceReason: "비교 대상(Redux, Context)과 작업(비교)이 명확함. 결정 질문으로서 판단 지원이 목적."
decisionContext:
  comparisonTargets: ["Redux", "Context API"]
  decisionFactors: []              # 아직 파악 안 됨 - AmbiguityScanner(light)에서 확인
```

**DECISION 경로 추가 출력 필드**:

```yaml
decisionContext:                   # DECISION 경로에서만 출력
  comparisonTargets: [string]      # 비교 대상들
  decisionFactors: [string]        # 결정에 필요한 요소들 (파악된 경우)
  missingContext: [string]         # 결정을 위해 추가로 필요한 정보
```

### EXPLORATION 경로 (IntentClarifier 미사용)

탐색 질문은 의도 분석 없이 AI가 자유롭게 응답한다.

### 경로별 비교 요약

| 경로 | 실행 순서 | ambiguousPoints 입력 | 주요 primaryAction | outputType |
|------|-----------|---------------------|-------------------|------------|
| EXECUTION | AmbiguityScanner → IntentClarifier | 있음 (full) | CREATE, MODIFY, DELETE | CODE, MIXED |
| DECISION | IntentClarifier → AmbiguityScanner | 없음 | COMPARE, ANALYZE | ANSWER |
| EXPLORATION | 미사용 | - | - | - |

## 사용 시점

1. 작업 시작 전 의도 파악
2. AmbiguityScanner 이후 의도 정리
3. 요구사항 분류/태깅
4. 작업 위임 전 컨텍스트 정리

## 하지 않는 것

- ❌ 세부 설계 (구현 방법, 아키텍처)
- ❌ 모호성 해소 시도 (해결책 제안)
- ❌ 작업 실행
- ❌ 우선순위 판단
- ❌ 추천/제안

## 성공 기준

1. "이 질문이 뭘 하려는지" 한 문장으로 설명 가능 (`summary`)
2. 세 가지 핵심 요소 식별: 작업/대상/산출물
3. 불확실하면 `confidenceLevel`을 정직하게 낮춤
4. 새로운 해석이나 설계를 추가하지 않음
