---
name: ambiguity-scanner
description: "Detect ambiguous expressions and missing decision factors in user questions. Supports 'full' mode for EXECUTION path (all ambiguities) and 'light' mode for DECISION path (only decision-blocking ambiguities). Does NOT judge or suggest solutions - only reveals uncertainty."
version: 1.2.0
updated: 2026-01-28
---

# AmbiguityScanner

질문에 포함된 모호한 표현과 누락된 결정 요소를 탐지한다.

**원칙**:
- ❌ 판단하지 않는다
- ⭕️ 불확실성만 드러낸다

## 입력

```yaml
question: string        # 사용자의 원본 자연어 질문
mode: full | light      # 스캔 모드 (기본: full)
```

## 검출 유형

| Type | 설명 | 예시 |
|------|------|------|
| COMPARISON | 비교 기준 불명확 | "같이", "동일", "비슷하게", "처럼" |
| REFERENCE | 참조 대상 불명확 | "다른 페이지", "기존 방식", "원래 것", "저번에" |
| OUTPUT | 산출물 불명확 | "만들어줘", "정리해줘", "처리해줘", "해줘" |
| SCOPE | 범위 불명확 | "전체", "일부", "필요한 것만", "적당히" |
| CRITERIA | 판단 기준 불명확 | "좋은", "적절한", "효율적인", "깔끔한" |

## 사용자 패턴 기반 우선 검출 표현

> 히스토리 분석 기반 (1,444개 질문 분석)

### HIGH Priority - 매우 빈번 (100회 이상)

| 표현 | 유형 | 빈도 | 필요한 결정 사항 |
|------|------|------|------------------|
| "해줘" | OUTPUT | 416회 | 산출물 형태, 수정 범위, 대상 파일 |
| "이/그 + 명사" | REFERENCE | 965회 | 지시 대상 명확화 (파일명, 함수명 등) |

### MEDIUM Priority - 자주 사용 (20-99회)

| 표현 | 유형 | 빈도 | 필요한 결정 사항 |
|------|------|------|------------------|
| "수정해줘" | OUTPUT | 36회 | 수정 대상, 수정 방식, 기대 결과 |
| "전체" | SCOPE | 36회 | 전체의 범위 정의 (파일/함수/프로젝트) |
| "다른 X" | REFERENCE | 34회 | 참조 대상 특정 |
| "동일하게" | COMPARISON | 34회 | 동일의 기준 (구조/스타일/동작) |
| "추가해줘" | OUTPUT | 34회 | 추가 위치, 추가 방식 |
| "기존" | REFERENCE | 31회 | 어떤 기존 것인지 특정 |
| "만들어줘" | OUTPUT | 29회 | 산출물 형태, 파일 위치 |
| "이전" | REFERENCE | 25회 | 어떤 이전 상태/버전인지 |
| "예쁘게" | CRITERIA | 25회 | 시각적 기준 정의 |

### LOW Priority - 간헐적 사용 (5-19회)

| 표현 | 유형 | 빈도 | 필요한 결정 사항 |
|------|------|------|------------------|
| "잘" | CRITERIA | 17회 | 품질 기준 정의 |
| "정리해줘" | OUTPUT | 17회 | 정리 방식, 출력 형태 |
| "처럼" | COMPARISON | 15회 | 비교 대상, 비교 기준 |
| "적절한" | CRITERIA | 14회 | 적절함의 기준 |
| "좀" | SCOPE | 12회 | 정도/범위 명시 |
| "제대로" | CRITERIA | 11회 | 올바름의 기준 |
| "따라/맞춰" | COMPARISON | 14회 | 참조 대상, 따를 범위 |
| "명확하게" | CRITERIA | 7회 | 명확함의 기준 |
| "같이" | COMPARISON | 5회 | 비교 대상, 동일 범위 |

## 처리 규칙

1. **검출만 한다** - 모호한 표현을 식별하고 유형을 분류
2. **새로운 해석을 추가하지 않음** - 원문에 없는 의미 부여 금지
3. **해결책 제안 금지** - 어떻게 해야 하는지 말하지 않음
4. **누락 없이 식별** - 모든 모호한 표현을 빠짐없이 탐지

## 출력 형식

**고정 포맷 (YAML)**:

```yaml
ambiguousPoints:
  - term: string           # 원문에서 발견된 모호한 표현
    type: COMPARISON | REFERENCE | OUTPUT | SCOPE | CRITERIA
    reason: string         # 왜 모호한지 설명
    requiredDecisions:     # 명확히 해야 할 결정 사항들
      - string
```

## 예시

### 입력

> "로그인 페이지를 다른 서비스처럼 깔끔하게 만들어줘"

### 출력

```yaml
ambiguousPoints:
  - term: "다른 서비스"
    type: REFERENCE
    reason: 어떤 서비스를 참조하는지 특정되지 않음
    requiredDecisions:
      - 참조할 구체적인 서비스명
      - 해당 서비스의 어떤 특성을 참조할 것인지

  - term: "처럼"
    type: COMPARISON
    reason: 비교 기준이 명확하지 않음
    requiredDecisions:
      - 레이아웃을 따를 것인지
      - 색상/스타일을 따를 것인지
      - 기능적 흐름을 따를 것인지

  - term: "깔끔하게"
    type: CRITERIA
    reason: 주관적 판단 기준으로 측정 불가
    requiredDecisions:
      - 여백 기준 (px 또는 비율)
      - 색상 수 제한
      - 폰트 종류 수 제한
      - 정렬 규칙

  - term: "만들어줘"
    type: OUTPUT
    reason: 산출물의 형태가 불명확
    requiredDecisions:
      - HTML/CSS 코드인지
      - 디자인 시안인지
      - 와이어프레임인지
      - 기존 코드 수정인지 신규 작성인지
```

### 입력

> "기존 API 응답이랑 비슷하게 에러 처리 추가해줘"

### 출력

```yaml
ambiguousPoints:
  - term: "기존 API 응답"
    type: REFERENCE
    reason: 어떤 API의 응답 형식을 참조하는지 특정되지 않음
    requiredDecisions:
      - 참조할 API 엔드포인트 경로
      - 해당 API의 응답 구조 확인 필요

  - term: "비슷하게"
    type: COMPARISON
    reason: 유사성의 범위가 정의되지 않음
    requiredDecisions:
      - 응답 포맷(JSON 구조)을 동일하게 할 것인지
      - HTTP 상태 코드 체계를 동일하게 할 것인지
      - 에러 메시지 스타일을 동일하게 할 것인지

  - term: "에러 처리"
    type: OUTPUT
    reason: 구현 범위가 불명확
    requiredDecisions:
      - 어떤 에러 케이스를 처리할 것인지
      - 클라이언트 에러(4xx)만인지 서버 에러(5xx)도 포함인지
      - 에러 로깅 포함 여부
      - 에러 복구 로직 포함 여부

  - term: "추가해줘"
    type: OUTPUT
    reason: 수정 대상과 방식이 불명확
    requiredDecisions:
      - 어떤 파일/함수에 추가할 것인지
      - 기존 코드를 수정할 것인지 새로 작성할 것인지
```

## 실제 사용 패턴 예시

### 입력 (히스토리 기반)

> "appscan 에서 했던것 처럼 nexpose 에도 반영되어있는가"

### 출력

```yaml
ambiguousPoints:
  - term: "했던것"
    type: REFERENCE
    reason: appscan에서 수행한 구체적인 작업이 특정되지 않음
    requiredDecisions:
      - 어떤 기능/변경사항을 참조하는지
      - 해당 작업의 파일/코드 위치

  - term: "처럼"
    type: COMPARISON
    reason: 비교 범위가 정의되지 않음
    requiredDecisions:
      - 코드 구조를 동일하게 할 것인지
      - 기능 동작을 동일하게 할 것인지
      - API 형식을 동일하게 할 것인지

  - term: "반영되어있는가"
    type: OUTPUT
    reason: 확인 범위와 방식이 불명확
    requiredDecisions:
      - 코드 리뷰가 필요한지
      - 테스트 실행이 필요한지
      - 단순 존재 여부 확인인지
```

### 입력 (히스토리 기반)

> "다른 NormalTable 에서는 row 간격마다 배경으로 표시되는데, 동일하게 맞춰줘"

### 출력

```yaml
ambiguousPoints:
  - term: "다른 NormalTable"
    type: REFERENCE
    reason: 어떤 NormalTable 컴포넌트를 참조하는지 특정되지 않음
    requiredDecisions:
      - 참조할 NormalTable의 파일 경로
      - 해당 컴포넌트의 스타일 구현 방식

  - term: "동일하게"
    type: COMPARISON
    reason: 동일의 범위가 정의되지 않음
    requiredDecisions:
      - 색상 값을 동일하게 할 것인지
      - 간격 크기를 동일하게 할 것인지
      - CSS 클래스를 공유할 것인지

  - term: "맞춰줘"
    type: OUTPUT
    reason: 수정 방식이 불명확
    requiredDecisions:
      - 기존 스타일 파일 수정인지
      - 새로운 스타일 추가인지
      - 공통 스타일 추출인지
```

## 실행 모드

### Full Mode (기본)

모든 모호한 표현을 빠짐없이 탐지한다. EXECUTION 경로에서 사용.

- 모든 검출 유형 (COMPARISON, REFERENCE, OUTPUT, SCOPE, CRITERIA) 탐지
- 모든 우선순위 (HIGH, MEDIUM, LOW) 표현 검출
- 상세한 requiredDecisions 제공

### Light Mode

**DECISION 경로 전용** - 결정에 필요한 핵심 모호성만 빠르게 검출한다.

**목적**: 판단/선택 질문에서 결정을 방해하는 핵심 불확실성만 식별

**검출 범위**:
- REFERENCE 유형만 검출 (비교 대상이 불명확하면 결정 불가)
- COMPARISON 유형 중 비교 기준이 완전히 누락된 경우만
- HIGH Priority 표현만 검출 (MEDIUM, LOW 무시)

**검출하지 않는 것**:
- OUTPUT 유형 (결정 질문은 산출물이 아닌 판단을 요청)
- SCOPE 유형 (결정 질문에서는 범위보다 선택이 중요)
- CRITERIA 유형 (주관적 기준은 결정 질문에서 허용)

**출력 형식** (간소화):

```yaml
mode: light
ambiguousPoints:
  - term: string
    type: REFERENCE | COMPARISON
    blocksDecision: true    # 이 모호성이 결정을 방해하는가
    quickResolution: string # 빠른 해소를 위한 단일 질문
```

### Light Mode 예시

**입력**:
```yaml
question: "Redux랑 Context 중에 뭐가 나아?"
mode: light
```

**출력**:
```yaml
mode: light
ambiguousPoints: []   # 비교 대상이 명확함 (Redux vs Context)
summary: "결정에 필요한 핵심 정보가 충분함"
```

---

**입력**:
```yaml
question: "기존 방식이랑 새로운 방식 중에 뭐가 나아?"
mode: light
```

**출력**:
```yaml
mode: light
ambiguousPoints:
  - term: "기존 방식"
    type: REFERENCE
    blocksDecision: true
    quickResolution: "어떤 기존 방식을 말씀하시나요?"
  - term: "새로운 방식"
    type: REFERENCE
    blocksDecision: true
    quickResolution: "어떤 새로운 방식을 비교하고 싶으신가요?"
summary: "비교 대상이 불명확하여 결정 지원 불가"
```

---

**입력**:
```yaml
question: "이 구조로 가도 괜찮을까?"
mode: light
```

**출력** (Full mode였다면 "괜찮을까"를 CRITERIA로 검출했겠지만, Light mode에서는 무시):
```yaml
mode: light
ambiguousPoints:
  - term: "이 구조"
    type: REFERENCE
    blocksDecision: true
    quickResolution: "어떤 구조를 말씀하시나요? (파일 경로나 코드 위치)"
summary: "참조 대상 명확화 필요"
```

### 모드 선택 기준

| 경로 | 모드 | 이유 |
|------|------|------|
| EXECUTION | full | 실행 전 모든 모호성 해소 필요 |
| DECISION | light | 결정 방해 요소만 빠르게 확인 |
| EXPLORATION | 미사용 | 탐색 질문은 모호성 분석 불필요 |

## 사용 시점

이 스킬은 다음 상황에서 사용:

1. 요구사항 분석 전 모호성 체크
2. 사용자 질문 해석 전 불확실성 확인
3. 스펙 문서 검토 시 누락된 결정 요소 탐지
4. 커뮤니케이션 명확화가 필요할 때

## 하지 않는 것

- ❌ 해결책 제안
- ❌ 추천
- ❌ 판단
- ❌ 설계
- ❌ "이렇게 하면 좋겠다" 류의 의견 제시
- ❌ 모호하지 않은 부분에 대한 언급

## 성공 기준

1. 모호한 표현이 누락 없이 식별됨
2. 각 모호성에 대해 명확한 유형 분류
3. 결정해야 할 사항이 구체적으로 나열됨
4. 새로운 해석이나 의견이 추가되지 않음
5. 출력 형식이 고정 YAML 포맷을 준수함
