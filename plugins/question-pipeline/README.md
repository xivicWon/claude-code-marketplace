# Question Pipeline Plugin

Complete question processing pipeline for transforming ambiguous user questions into actionable, pattern-compliant code.

## Overview

This plugin provides a 7-skill pipeline that processes user questions from initial classification through code generation and ongoing maintenance.

## Pipeline Flow

```
[User Question]
       │
       ▼
┌────────────────────┐
│ QuestionClassifier │ → A/B/C 분류
└────────────────────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 │
   A. EXPLORATION                                        │
   (탐색 질문)                                            │
       │                                                 │
       ▼                                                 │
   ❌ 스킬 미사용                                         │
   ✅ AI 자유 응답                                        │
                                                         │
       ├─────────────────────────────────────────────────┤
       │                                                 │
       ▼                                                 │
   B. DECISION                                           │
   (결정 질문)                                            │
       │                                                 │
       ▼                                                 │
   ┌─────────────────┐                                   │
   │ IntentClarifier │                                   │
   └─────────────────┘                                   │
       │                                                 │
       ▼                                                 │
   ┌─────────────────┐                                   │
   │AmbiguityScanner │ (light mode)                      │
   └─────────────────┘                                   │
       │                                                 │
       ▼                                                 │
   결정 지원 응답                                          │
                                                         │
       ├─────────────────────────────────────────────────┤
       │                                                 │
       ▼                                                 │
   C. EXECUTION                                          │
   (실행 질문)                                            │
       │                                                 │
       ▼                                                 │
   ┌─────────────────┐                                   │
   │ AmbiguityScanner│                                   │
   └─────────────────┘                                   │
       │                                                 │
       ▼                                                 │
   ┌─────────────────┐                                   │
   │ IntentClarifier │                                   │
   └─────────────────┘                                   │
       │                                                 │
       ▼                                                 │
   ┌────────────────────┐                                │
   │ QuestionNormalizer │                                │
   └────────────────────┘                                │
       │                                                 │
       ▼                                                 │
   ┌──────────────────────────┐                          │
   │ DataTablePatternResolver │                          │
   └──────────────────────────┘                          │
       │                                                 │
       ▼                                                 │
   ┌──────────────────┐                                  │
   │ DataTableCreator │                                  │
   └──────────────────┘                                  │
       │                                                 │
       ▼                                                 │
   ┌──────────────────────┐                              │
   │ PatternDriftDetector │                              │
   └──────────────────────┘                              │
```

## Question Classification

The pipeline begins with **QuestionClassifier** which routes questions into three paths:

| Type | Definition | Example | Applied Skills |
|------|------------|---------|----------------|
| **EXPLORATION** | Information gathering, learning | "이 코드가 뭐하는 거야?" | None (AI free response) |
| **DECISION** | Choice/judgment needed | "A랑 B 중에 뭐가 나아?" | IntentClarifier, AmbiguityScanner(light) |
| **EXECUTION** | Concrete implementation request | "로그인 페이지 만들어줘" | Full pipeline |

### Classification Signals

```yaml
EXPLORATION:
  signals:
    - "뭐야", "뭐지", "왜", "어디", "언제", "어떻게"
    - "확인해줘", "찾아줘", "알려줘", "설명해줘"
  intention: 정보 획득

DECISION:
  signals:
    - "뭐가 나아", "어떤 게 좋아", "할까 말까"
    - "괜찮을까", "문제 없을까", "이래도 돼"
  intention: 판단 지원

EXECUTION:
  signals:
    - "해줘", "만들어줘", "추가해줘", "수정해줘"
    - "구현", "작성", "생성", "삭제"
    - 구체적 산출물 언급 (파일명, 컴포넌트명)
  intention: 실행/구현
```

### Confidence Handling

- **≥ 0.7**: Proceed with classification
- **0.5 ~ 0.7**: Ask user for clarification
- **< 0.5**: Fallback to EXECUTION (safer path)

## Skills

### 0. QuestionClassifier (NEW)

**Purpose**: Classify user questions to determine the appropriate processing pipeline.

- Routes questions into EXPLORATION, DECISION, or EXECUTION
- First skill in the pipeline - runs before any other processing
- Preserves AI freedom for exploration questions
- Falls back to EXECUTION when uncertain (safer path)

### 1. AmbiguityScanner

**Purpose**: Detect ambiguous expressions and missing decision factors in user questions.

- Identifies vague terms like "같이", "동일", "비슷하게"
- Classifies ambiguity types: COMPARISON, REFERENCE, OUTPUT, SCOPE, CRITERIA
- Does NOT judge or suggest solutions - only reveals uncertainty
- **Light mode** available for DECISION questions (핵심 모호성만)

### 2. IntentClarifier

**Purpose**: Identify the core intent and task type from user questions.

- Determines primaryAction (CREATE, MODIFY, ANALYZE, etc.)
- Identifies targetObject (UI, DATA, CODE, etc.)
- Specifies expected outputType (CODE, DOC, REPORT, etc.)
- Assigns confidence levels based on ambiguity

### 3. QuestionNormalizer

**Purpose**: Generate normalized re-question templates based on analysis.

- Creates structured clarification questions with options
- Produces templates that downstream skills can consume
- Minimizes free-text input by providing concrete choices

### 4. DataTablePatternResolver

**Purpose**: Identify and extract existing implementation patterns.

- Defines "same pattern" structurally rather than by intuition
- Separates fixed elements from variable elements
- Outputs pattern specs for code generation

### 5. DataTableCreator

**Purpose**: Generate code from confirmed pattern specifications.

- Pure transformation: pattern spec + values → code
- No judgment or interpretation
- Fails explicitly on constraint violations

### 6. PatternDriftDetector

**Purpose**: Detect if existing code has drifted from established patterns.

- Compares implementation against pattern specifications
- Assigns drift levels: LOW, MEDIUM, HIGH
- Identifies specific deviation points with line numbers

## Use Cases

1. **Exploration**: Understanding code, finding information → AI responds freely
2. **Decision Making**: Comparing options, validating approaches → Light analysis support
3. **New Feature Development**: Process vague requirements into specific, pattern-compliant implementations
4. **Code Review**: Verify new code follows established patterns
5. **Maintenance**: Detect pattern drift in existing codebase

## Design Principles

- **Question-First Routing**: Classify before processing
- **AI Freedom**: Exploration questions bypass the pipeline
- **Separation of Concerns**: Each skill has a single responsibility
- **Explicit Failure**: Skills fail clearly rather than guessing
- **No Judgment**: Skills transform/detect, not recommend
- **Deterministic Output**: Same input → Same output
- **Safe Fallback**: When uncertain, use the more thorough path

## Core Philosophy

> "이 흐름은 '질문을 자동화하기 위한 프레임'이지 '모든 질문을 통제하기 위한 규칙'이 아니다"

- **탐색 질문** → AI가 자유롭게 응답
- **결정 질문** → 가볍게 지원
- **실행 질문** → 체계적으로 처리
