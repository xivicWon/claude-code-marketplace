---
name: question-normalizer
description: "Generate normalized re-question templates based on ambiguity analysis and intent clarification. Creates structured clarification questions with options and produces a template that downstream skills/agents can consume directly. Trigger after AmbiguityScanner and IntentClarifier to formalize the clarification process."
version: 1.0.0
updated: 2026-01-28
---

# QuestionNormalizer

모호성 + 의도를 바탕으로 일반화된 재질문 템플릿을 생성한다.

**원칙**:
- ⭕️ 결정이 필요한 지점만 질문으로 만든다
- ⭕️ 선택지 형태를 우선 사용한다
- ⭕️ 자유 서술 질문은 최소화
- ❌ 답을 대신 채우지 않음
- ❌ 판단을 유도하지 않음

## 입력

```yaml
originalQuestion: string           # 사용자의 원본 질문
ambiguousPoints:                   # AmbiguityScanner 출력
  - term: string
    type: COMPARISON | REFERENCE | OUTPUT | SCOPE | CRITERIA
    reason: string
    requiredDecisions:
      - string
intent:                            # IntentClarifier 출력
  primaryAction: string
  targetObject: string
  outputType: string
  summary: string
confidenceLevel: HIGH | MEDIUM | LOW
```

## 출력 형식

**고정 포맷 (YAML)**:

```yaml
clarificationQuestions:
  - question: string               # 명확화를 위한 질문
    decisionType: string           # 결정 유형
    options:                       # 선택지 (2-5개 권장)
      - string
    allowFreeText: boolean         # 자유 입력 허용 여부 (기본: false)

normalizedRequestTemplate:
  intent: string                   # 정규화된 의도 문장
  fixedParts:                      # 확정된 부분
    - string
  variableParts:                   # 결정 필요한 변수
    - name: string                 # 변수명
      description: string          # 설명
      from: string                 # 해당 clarificationQuestion 참조
```

## 질문 생성 규칙

### 1. decisionType 매핑

| ambiguousPoint.type | decisionType | 질문 패턴 |
|---------------------|--------------|-----------|
| REFERENCE | TARGET_SELECTION | "어떤 X를 참조할까요?" |
| COMPARISON | COMPARISON_SCOPE | "어떤 측면을 동일하게 할까요?" |
| OUTPUT | OUTPUT_FORMAT | "어떤 형태로 산출할까요?" |
| SCOPE | RANGE_DEFINITION | "범위를 어디까지로 할까요?" |
| CRITERIA | QUALITY_STANDARD | "기준을 어떻게 정의할까요?" |

### 2. 선택지 생성 원칙

- **구체적**: 추상적 표현 지양 ("적당히" → 구체적 수치/옵션)
- **상호 배타적**: 중복되지 않는 선택지
- **실행 가능**: 선택 즉시 작업 가능한 수준
- **2-5개**: 너무 적으면 부족, 너무 많으면 혼란

### 3. 자유 서술 허용 조건

`allowFreeText: true`는 다음 경우에만:
- 선택지로 커버 불가능한 경우
- 파일 경로, 이름 등 사용자 고유 입력 필요
- 기타 옵션으로 커버 불가

## 예시

### 입력

```yaml
originalQuestion: "기존 API랑 동일하게 에러 처리 추가해줘"
ambiguousPoints:
  - term: "기존 API"
    type: REFERENCE
    reason: 어떤 API를 참조하는지 특정되지 않음
    requiredDecisions:
      - 참조할 API 엔드포인트 경로
      - 해당 API의 에러 처리 방식 확인
  - term: "동일하게"
    type: COMPARISON
    reason: 동일의 범위가 정의되지 않음
    requiredDecisions:
      - HTTP 상태 코드 체계
      - 응답 JSON 구조
      - 에러 메시지 스타일
  - term: "추가해줘"
    type: OUTPUT
    reason: 수정 대상이 불명확
    requiredDecisions:
      - 어떤 파일/함수에 추가할 것인지
intent:
  primaryAction: MODIFY
  targetObject: CODE
  outputType: CODE
  summary: "기존 API 패턴을 참조하여 에러 처리 코드 추가"
confidenceLevel: MEDIUM
```

### 출력

```yaml
clarificationQuestions:
  - question: "어떤 API를 참조할까요?"
    decisionType: TARGET_SELECTION
    options:
      - "src/api/user.ts의 getUserList"
      - "src/api/auth.ts의 login"
      - "src/api/common.ts의 공통 에러 핸들러"
      - "직접 지정"
    allowFreeText: true

  - question: "어떤 측면을 동일하게 할까요?"
    decisionType: COMPARISON_SCOPE
    options:
      - "HTTP 상태 코드 체계만"
      - "응답 JSON 구조만"
      - "에러 메시지 스타일만"
      - "위 모든 항목"
    allowFreeText: false

  - question: "어떤 파일에 에러 처리를 추가할까요?"
    decisionType: OUTPUT_FORMAT
    options:
      - "현재 열린 파일"
      - "직접 경로 지정"
    allowFreeText: true

normalizedRequestTemplate:
  intent: "[TARGET_API]의 에러 처리 패턴을 참조하여 [TARGET_FILE]에 [COMPARISON_SCOPE] 에러 처리 코드를 추가한다"
  fixedParts:
    - "에러 처리 코드 추가"
    - "기존 패턴 참조"
  variableParts:
    - name: TARGET_API
      description: "참조할 API 엔드포인트"
      from: "clarificationQuestions[0]"
    - name: COMPARISON_SCOPE
      description: "동일하게 적용할 범위"
      from: "clarificationQuestions[1]"
    - name: TARGET_FILE
      description: "수정 대상 파일"
      from: "clarificationQuestions[2]"
```

### 입력 (HIGH confidence - 질문 최소화)

```yaml
originalQuestion: "UserService.java에 로깅 추가해줘"
ambiguousPoints:
  - term: "로깅"
    type: SCOPE
    reason: 로깅 범위가 불명확
    requiredDecisions:
      - 어떤 메서드에 추가할지
      - 로그 레벨
intent:
  primaryAction: MODIFY
  targetObject: CODE
  outputType: CODE
  summary: "UserService.java에 로깅 코드 추가"
confidenceLevel: HIGH
```

### 출력 (질문 최소화)

```yaml
clarificationQuestions:
  - question: "어떤 메서드에 로깅을 추가할까요?"
    decisionType: RANGE_DEFINITION
    options:
      - "모든 public 메서드"
      - "CRUD 메서드만"
      - "특정 메서드 지정"
    allowFreeText: true

  - question: "로그 레벨은 어떻게 할까요?"
    decisionType: QUALITY_STANDARD
    options:
      - "INFO (일반 정보)"
      - "DEBUG (디버깅용)"
      - "메서드별 적절히 혼합"
    allowFreeText: false

normalizedRequestTemplate:
  intent: "UserService.java의 [TARGET_METHODS]에 [LOG_LEVEL] 레벨의 로깅 코드를 추가한다"
  fixedParts:
    - "대상 파일: UserService.java"
    - "작업: 로깅 코드 추가"
  variableParts:
    - name: TARGET_METHODS
      description: "로깅 추가 대상 메서드"
      from: "clarificationQuestions[0]"
    - name: LOG_LEVEL
      description: "로그 레벨"
      from: "clarificationQuestions[1]"
```

### 입력 (LOW confidence - 핵심 질문 우선)

```yaml
originalQuestion: "이거 좀 봐줘"
ambiguousPoints:
  - term: "이거"
    type: REFERENCE
    reason: 대상이 전혀 특정되지 않음
    requiredDecisions:
      - 어떤 파일/코드/화면을 말하는지
  - term: "봐줘"
    type: OUTPUT
    reason: 기대하는 행동이 불명확
    requiredDecisions:
      - 코드 리뷰인지, 에러 확인인지, 수정인지
intent:
  primaryAction: ANALYZE
  targetObject: UNKNOWN
  outputType: UNKNOWN
  summary: "특정되지 않은 대상에 대한 검토/확인 요청"
confidenceLevel: LOW
```

### 출력 (핵심부터 질문)

```yaml
clarificationQuestions:
  - question: "어떤 대상을 확인할까요?"
    decisionType: TARGET_SELECTION
    options:
      - "현재 열린 파일"
      - "마지막 수정한 파일"
      - "직접 지정"
    allowFreeText: true

  - question: "어떤 작업을 원하시나요?"
    decisionType: OUTPUT_FORMAT
    options:
      - "코드 리뷰 (품질/구조 검토)"
      - "에러 확인 (문제점 찾기)"
      - "설명 (코드 동작 설명)"
      - "수정 (문제 해결)"
    allowFreeText: false

normalizedRequestTemplate:
  intent: "[TARGET]에 대해 [ACTION]을 수행한다"
  fixedParts: []
  variableParts:
    - name: TARGET
      description: "확인 대상"
      from: "clarificationQuestions[0]"
    - name: ACTION
      description: "수행할 작업"
      from: "clarificationQuestions[1]"
```

## 워크플로우 연계

```
[User Question]
       │
       ▼
┌─────────────────┐
│ AmbiguityScanner│ → ambiguousPoints
└─────────────────┘
       │
       ▼
┌─────────────────┐
│ IntentClarifier │ → intent + confidenceLevel
└─────────────────┘
       │
       ▼
┌────────────────────┐
│ QuestionNormalizer │ → clarificationQuestions + normalizedRequestTemplate
└────────────────────┘
       │
       ▼
   [User Answers]
       │
       ▼
   [Execution with filled template]
```

## confidenceLevel에 따른 질문 전략

| Level | 전략 |
|-------|------|
| HIGH | 질문 최소화 (1-2개), 세부사항만 확인 |
| MEDIUM | 핵심 모호성에 대해 질문 (2-3개) |
| LOW | 기본 요소부터 질문 (대상 → 작업 → 산출물 순) |

## 선택지 생성 팁

### REFERENCE 유형
- 프로젝트 내 실제 파일/함수명 제시
- "현재 열린 파일", "마지막 수정 파일" 등 컨텍스트 활용
- "직접 지정" 옵션 포함

### COMPARISON 유형
- 비교 가능한 측면을 나열
- "전체", "일부" 구분 명확히
- 조합 옵션 제공 ("위 모든 항목")

### OUTPUT 유형
- 구체적 산출물 형태 나열
- 파일 형식 명시 (.ts, .json, .md)
- 실행 vs 생성 구분

### SCOPE 유형
- 범위를 구체적 수치로
- "전체", "일부", "특정 조건" 구분
- 예시와 함께 제시

### CRITERIA 유형
- 측정 가능한 기준으로 변환
- 업계 표준 옵션 제시
- "프로젝트 컨벤션 따름" 옵션

## 사용 시점

1. AmbiguityScanner + IntentClarifier 이후
2. 사용자에게 명확화 질문이 필요할 때
3. 자동화된 질문 생성이 필요할 때
4. 일관된 재요청 템플릿이 필요할 때

## 하지 않는 것

- ❌ 답을 대신 채우지 않음
- ❌ 판단을 유도하지 않음 (중립적 선택지)
- ❌ 불필요한 질문 생성
- ❌ 추천/제안 (선택지에 "(권장)" 등 표시 금지)

## 성공 기준

1. 이 출력만으로 일관된 재요청 가능
2. 이후 스킬/에이전트가 바로 소비 가능
3. 선택지 선택 → 즉시 실행 가능한 수준
4. 자유 서술 최소화
