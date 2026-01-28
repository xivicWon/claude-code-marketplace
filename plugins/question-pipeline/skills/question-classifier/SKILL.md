---
name: question-classifier
description: "Classify user questions into EXPLORATION (이해 필요), DECISION (판단 필요), or EXECUTION (실행 필요) types. Routes questions to appropriate processing: free response for exploration, light support for decisions, full pipeline for execution. First skill in pipeline."
version: 1.1.0
updated: 2026-01-28
---

# QuestionClassifier

사용자 질문을 분류하여 적절한 처리 경로를 결정한다.

**원칙**:
- 파이프라인의 **첫 번째** 관문
- 탐색 질문에는 AI 자유 응답 보장
- 불확실하면 안전한 쪽(EXECUTION)으로 fallback

## 입력

사용자의 원본 자연어 질문

## 분류 유형

| Type | 정의 | AI 처리 방식 |
|------|------|--------------|
| **EXPLORATION** | 정보 수집, 탐색, 학습 목적 | 스킬 미사용, AI 자유 응답 |
| **DECISION** | 선택/판단이 필요한 질문 | IntentClarifier → AmbiguityScanner(light) |
| **EXECUTION** | 구체적 실행/구현 요청 | 전체 파이프라인 적용 |

## 경로별 의미와 철학

### EXPLORATION (탐색) - "알고 싶다"

**핵심 질문**: "이게 뭐야?", "왜 그래?", "어디 있어?"

**의미**:
- 사용자가 **정보를 얻고 싶은** 상태
- 아직 무엇을 할지 결정하지 않았거나, 먼저 이해가 필요한 상황
- 코드, 구조, 동작 원리에 대한 **호기심과 학습** 목적

**왜 AI 자유 응답인가**:
- 탐색 질문은 "정답"보다 "이해"가 목적
- 모호성 분석이 오히려 탐색을 방해함 (예: "왜"라는 질문에 "왜의 범위를 명확히 해주세요"는 부자연스러움)
- AI가 맥락을 파악해 자유롭게 설명하는 것이 가장 효과적
- **통제하지 않음** = 질문의 자유로운 흐름 보장

**응답 시 설명 예시**:
> "탐색 질문으로 분류했습니다. 구현이나 수정 요청이 아닌 정보 확인 목적이므로, 바로 설명드리겠습니다."

---

### DECISION (결정) - "뭐가 나아?"

**핵심 질문**: "A vs B?", "이래도 돼?", "어떤 게 좋아?"

**의미**:
- 사용자가 **선택의 기로**에 서 있는 상태
- 이미 옵션들을 알고 있지만, 판단이 필요한 상황
- 장단점 비교, 리스크 확인, 방향 검증 목적

**왜 가볍게 지원하는가**:
- 결정 질문은 **판단의 주체가 사용자**
- AI는 정보와 관점을 제공하되, 결정을 대신하지 않음
- 전체 파이프라인은 과함 - 비교 대상만 명확하면 충분
- IntentClarifier로 비교 맥락 파악 + AmbiguityScanner(light)로 결정 방해 요소만 확인

**응답 시 설명 예시**:
> "결정 질문으로 분류했습니다. 두 옵션의 비교 분석을 통해 판단에 필요한 정보를 드리겠습니다. 최종 선택은 상황에 맞게 결정해 주세요."

---

### EXECUTION (실행) - "만들어줘"

**핵심 질문**: "~해줘", "~만들어줘", "~추가해줘"

**의미**:
- 사용자가 **구체적인 산출물**을 원하는 상태
- 코드, 파일, 기능 등 실제 결과물이 필요한 상황
- 모호한 요청을 명확한 구현으로 변환해야 함

**왜 전체 파이프라인인가**:
- 실행 요청은 **결과의 품질이 중요**
- "다른 거랑 똑같이"라는 말의 "똑같이"를 정의해야 일관된 코드 생성 가능
- 모호성을 해소하지 않으면 → 잘못된 코드 → 재작업
- 체계적 분석이 오히려 시간을 절약함

**응답 시 설명 예시**:
> "실행 질문으로 분류했습니다. 요청하신 내용을 정확히 구현하기 위해 몇 가지 확인이 필요합니다."

---

### 경로 선택의 핵심 기준

```
┌─────────────────────────────────────────────────────────┐
│                    사용자의 현재 상태                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   "모르겠어"          "고민돼"           "해줘"           │
│       │                  │                 │            │
│       ▼                  ▼                 ▼            │
│   EXPLORATION        DECISION          EXECUTION        │
│   (이해 필요)         (판단 필요)        (실행 필요)       │
│       │                  │                 │            │
│       ▼                  ▼                 ▼            │
│   자유 설명           비교 분석          체계적 구현       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**기억할 것**:
- EXPLORATION = 이해의 자유
- DECISION = 판단의 지원
- EXECUTION = 구현의 정확성

## 분류 기준

### EXPLORATION (탐색 질문)

**의도**: 정보 획득, 이해, 탐색

**신호 패턴**:
- 의문사: "뭐야", "뭐지", "왜", "어디", "언제", "어떻게"
- 요청: "확인해줘", "찾아줘", "알려줘", "설명해줘"
- 이해: "이해가 안 돼", "모르겠어", "궁금해"
- 조회: "보여줘", "어디 있어", "뭐가 있어"

**예시**:
- "이 코드가 뭐하는 거야?"
- "이 함수 어디서 호출돼?"
- "왜 이렇게 구현했어?"
- "에러 메시지가 뭐야?"
- "이 패턴이 뭔지 설명해줘"

**적용 스킬**: 없음 (AI 자유 응답)

---

### DECISION (결정 질문)

**의도**: 판단 지원, 선택 도움

**신호 패턴**:
- 비교: "뭐가 나아", "어떤 게 좋아", "뭐가 맞아"
- 선택: "A vs B", "선택", "결정", "고민"
- 확인: "괜찮을까", "문제 없을까", "이래도 돼"
- 판단: "할까 말까", "해도 될까", "맞나"

**예시**:
- "Redux랑 Context 중에 뭐가 나아?"
- "이렇게 해도 문제 없을까?"
- "A 방식이랑 B 방식 중에 어떤 게 좋아?"
- "이 구조로 가도 괜찮을까?"
- "성능이랑 가독성 중에 뭘 우선해야 해?"

**적용 스킬**:
1. IntentClarifier (full)
2. AmbiguityScanner (light mode)

---

### EXECUTION (실행 질문)

**의도**: 구체적 실행, 구현, 생성

**신호 패턴**:
- 생성: "만들어줘", "생성해줘", "작성해줘"
- 수정: "수정해줘", "고쳐줘", "바꿔줘", "변경해줘"
- 추가: "추가해줘", "넣어줘", "붙여줘"
- 삭제: "삭제해줘", "제거해줘", "지워줘"
- 구현: "구현해줘", "적용해줘", "반영해줘"
- 구체적 산출물 언급: 파일명, 컴포넌트명, 함수명

**예시**:
- "로그인 페이지 만들어줘"
- "에러 처리 추가해줘"
- "이 함수 리팩토링해줘"
- "UserService.ts에 메서드 추가해줘"
- "다른 컴포넌트랑 동일하게 수정해줘"

**적용 스킬**: 전체 파이프라인
1. AmbiguityScanner
2. IntentClarifier
3. QuestionNormalizer
4. DataTablePatternResolver
5. DataTableCreator
6. PatternDriftDetector

## 분류 신호 상세

```yaml
EXPLORATION:
  primary_signals:
    - pattern: "(뭐|무엇|무슨).*[야지니까]"
      weight: 0.9
    - pattern: "왜.*[야지니까해]"
      weight: 0.9
    - pattern: "어디.*[야서에]"
      weight: 0.9
    - pattern: "어떻게.*[돼되야]"
      weight: 0.8
    - pattern: "설명해줘"
      weight: 0.9
    - pattern: "알려줘"
      weight: 0.7
    - pattern: "확인해줘"
      weight: 0.6
    - pattern: "찾아줘"
      weight: 0.6
  secondary_signals:
    - "이해", "모르", "궁금", "의미", "역할"

DECISION:
  primary_signals:
    - pattern: "(뭐|어떤|어느).*나아"
      weight: 0.95
    - pattern: "(뭐|어떤|어느).*좋아"
      weight: 0.9
    - pattern: "괜찮[을나아]"
      weight: 0.85
    - pattern: "문제.없[을나을까]"
      weight: 0.85
    - pattern: "해도.될까"
      weight: 0.9
    - pattern: "할까.말까"
      weight: 0.95
    - pattern: "vs|VS"
      weight: 0.9
  secondary_signals:
    - "선택", "결정", "고민", "비교", "차이"

EXECUTION:
  primary_signals:
    - pattern: "만들어줘"
      weight: 0.95
    - pattern: "수정해줘"
      weight: 0.95
    - pattern: "추가해줘"
      weight: 0.95
    - pattern: "삭제해줘"
      weight: 0.95
    - pattern: "구현해줘"
      weight: 0.95
    - pattern: "작성해줘"
      weight: 0.9
    - pattern: "고쳐줘"
      weight: 0.9
    - pattern: "바꿔줘"
      weight: 0.9
    - pattern: "적용해줘"
      weight: 0.9
  secondary_signals:
    - 파일명 언급 (*.ts, *.tsx, *.js, *.css 등)
    - 컴포넌트명 언급 (PascalCase)
    - 함수명 언급 (camelCase + 괄호)
```

## 신뢰도 처리

```yaml
confidenceThreshold:
  high: 0.7      # 분류대로 진행
  medium: 0.5    # 경계선 - 질문 가능
  low: 0.0       # fallback to EXECUTION

fallbackStrategy:
  confidence >= 0.7:
    action: "분류대로 진행"

  confidence 0.5 ~ 0.7:
    action: "사용자에게 확인"
    question: "어떤 도움이 필요하신가요?"
    options:
      - "정보/설명이 필요해요 (탐색)"
      - "결정을 도와주세요 (판단)"
      - "직접 만들어주세요 (실행)"

  confidence < 0.5:
    action: "EXECUTION으로 fallback"
    reason: "불확실할 때는 더 철저한 처리 경로 선택"
```

## 출력 형식

**고정 포맷 (YAML)**:

```yaml
classification:
  type: EXPLORATION | DECISION | EXECUTION
  confidence: number  # 0.0 ~ 1.0
  reason: string      # 분류 근거 설명

matchedSignals:
  - signal: string    # 매칭된 패턴/키워드
    weight: number    # 해당 신호의 가중치

suggestedPipeline:
  - skillName: string
    mode: "full" | "light" | "skip"
    reason: string    # 해당 모드 선택 이유
```

## 예시

### 예시 1: EXPLORATION

**입력**:
> "이 useEffect가 왜 두 번 실행되는 거야?"

**출력**:
```yaml
classification:
  type: EXPLORATION
  confidence: 0.95
  reason: "'왜'로 시작하는 원인 탐색 질문, 이해 목적

matchedSignals:
  - signal: "왜.*[야지]"
    weight: 0.9
  - signal: "거야" (의문형 종결)
    weight: 0.85

suggestedPipeline:
  - skillName: AmbiguityScanner
    mode: skip
    reason: 탐색 질문은 모호성 분석 불필요
  - skillName: IntentClarifier
    mode: skip
    reason: AI 자유 응답 허용
  - skillName: QuestionNormalizer
    mode: skip
    reason: 정제 불필요
```

---

### 예시 2: DECISION

**입력**:
> "useState랑 useReducer 중에 뭐가 나아?"

**출력**:
```yaml
classification:
  type: DECISION
  confidence: 0.92
  reason: "A vs B 비교 및 '뭐가 나아' 판단 요청"

matchedSignals:
  - signal: "뭐가 나아"
    weight: 0.95
  - signal: "랑...중에" (비교 구문)
    weight: 0.8

suggestedPipeline:
  - skillName: IntentClarifier
    mode: full
    reason: 비교 맥락과 판단 기준 파악 필요
  - skillName: AmbiguityScanner
    mode: light
    reason: 결정에 필요한 핵심 요소만 확인
  - skillName: QuestionNormalizer
    mode: skip
    reason: 결정 질문은 정규화 불필요
```

---

### 예시 3: EXECUTION

**입력**:
> "로그인 페이지를 다른 서비스처럼 깔끔하게 만들어줘"

**출력**:
```yaml
classification:
  type: EXECUTION
  confidence: 0.95
  reason: "'만들어줘'라는 명시적 구현 요청, 구체적 산출물(로그인 페이지) 언급"

matchedSignals:
  - signal: "만들어줘"
    weight: 0.95
  - signal: "로그인 페이지" (구체적 산출물)
    weight: 0.7

suggestedPipeline:
  - skillName: AmbiguityScanner
    mode: full
    reason: "다른 서비스", "깔끔하게" 등 모호한 표현 다수
  - skillName: IntentClarifier
    mode: full
    reason: 구현 의도와 범위 파악 필요
  - skillName: QuestionNormalizer
    mode: full
    reason: 명확한 요구사항으로 정제 필요
  - skillName: DataTablePatternResolver
    mode: full
    reason: 기존 패턴 참조 필요
  - skillName: DataTableCreator
    mode: full
    reason: 코드 생성 필요
  - skillName: PatternDriftDetector
    mode: full
    reason: 패턴 준수 검증 필요
```

---

### 예시 4: 경계선 케이스 (확인 필요)

**입력**:
> "이 API 응답 처리해줘"

**출력**:
```yaml
classification:
  type: EXECUTION  # 임시 분류
  confidence: 0.55
  reason: "'처리해줘'는 실행 신호이나, 구체적 행동이 불명확"

matchedSignals:
  - signal: "처리해줘"
    weight: 0.6

clarificationNeeded: true
clarificationQuestion: "어떤 도움이 필요하신가요?"
clarificationOptions:
  - label: "API 응답 구조 설명 (탐색)"
    mapsTo: EXPLORATION
  - label: "응답 처리 방식 비교 (판단)"
    mapsTo: DECISION
  - label: "응답 처리 코드 작성 (실행)"
    mapsTo: EXECUTION
```

## 복합 신호 처리

하나의 질문에 여러 유형의 신호가 있을 때:

```yaml
priorityOrder:
  1. EXECUTION 신호가 명확하면 → EXECUTION
  2. DECISION 신호만 있으면 → DECISION
  3. EXPLORATION 신호만 있으면 → EXPLORATION
  4. 혼합 신호 → 가장 높은 가중치 신호 따름
  5. 동등 가중치 → EXECUTION (안전한 쪽)
```

**예시** - 복합 신호:
> "왜 이렇게 구현했는지 설명하고 더 나은 방식으로 수정해줘"

```yaml
classification:
  type: EXECUTION  # "수정해줘"가 최종 행동
  confidence: 0.85
  reason: "탐색(왜, 설명) + 실행(수정해줘) 복합, 최종 요청이 실행"

matchedSignals:
  - signal: "왜"
    weight: 0.9
    type: EXPLORATION
  - signal: "설명"
    weight: 0.7
    type: EXPLORATION
  - signal: "수정해줘"
    weight: 0.95
    type: EXECUTION

suggestedPipeline:
  # EXECUTION 파이프라인 적용, 단 탐색 부분도 응답에 포함
```

## 사용 시점

이 스킬은 **모든 사용자 질문의 첫 단계**에서 사용:

1. 질문 수신 즉시 분류 실행
2. 분류 결과에 따라 후속 스킬 결정
3. EXPLORATION이면 스킬 체인 생략, AI 자유 응답

## 핵심 원칙

> "이 흐름은 '질문을 자동화하기 위한 프레임'이지 '모든 질문을 통제하기 위한 규칙'이 아니다"

- **탐색 질문** → AI가 자유롭게 응답
- **결정 질문** → 가볍게 지원 (의도 파악 + 핵심 모호성만)
- **실행 질문** → 체계적으로 처리 (전체 파이프라인)

## 성공 기준

1. 분류가 사용자 의도와 일치
2. 탐색 질문에 불필요한 스킬 적용 안 함
3. 실행 질문의 모호성을 놓치지 않음
4. 경계선 케이스에서 적절히 확인 요청
5. confidence 수치가 실제 확실성 반영
