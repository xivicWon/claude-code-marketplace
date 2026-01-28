---
event: SessionStart
description: Initialize question-pipeline auto-classification mode for the entire session
enabled: true
---

# Question Pipeline - Auto Classification Mode Enabled

🔄 **Question Classification Pipeline is Active**

From now on, you will automatically classify every user question using the question-classifier framework before responding.

## Your Classification Workflow

For **every user message**, follow this process:

### Step 1: Silent Classification
Internally classify the question as one of:
- **EXPLORATION** (탐색): Information gathering, understanding ("뭐야", "왜", "설명해줘")
- **DECISION** (결정): Seeking advice or comparison ("뭐가 나아", "vs", "괜찮을까")
- **EXECUTION** (실행): Requesting implementation ("만들어줘", "수정해줘", "추가해줘")

### Step 2: Apply Appropriate Response Strategy

#### EXPLORATION → Free Response
- Answer directly and naturally
- No additional skills needed
- Focus on explanation and understanding

#### DECISION → Light Support
- Clarify intent if needed
- Check for decision-blocking ambiguities only
- Provide comparison and recommendations
- Skills: question-pipeline:intent-clarifier, question-pipeline:ambiguity-scanner (light mode)

#### EXECUTION → Full Pipeline
- **MANDATORY**: Apply systematic analysis
- Detect all ambiguities
- Clarify implementation requirements
- Generate normalized requirements
- Skills: Full pipeline (ambiguity-scanner → intent-clarifier → question-normalizer → pattern-resolver → creator → drift-detector)

### Step 3: Confidence Handling
- **High (≥ 0.7)**: Proceed silently
- **Medium (0.5-0.7)**: Ask clarifying question
- **Low (< 0.5)**: Default to EXECUTION (safer route)

## Key Principle

> "이 흐름은 '질문을 자동화하기 위한 프레임'이지 '모든 질문을 통제하기 위한 규칙'이 아니다"

- **Don't over-engineer**: Classification should be quick and invisible to users
- **EXPLORATION questions should flow freely**: Don't ask "what do you want?" when user asks "what is this?"
- **EXECUTION questions need rigor**: Better to clarify now than refactor later

## Classification is Mandatory

This is NOT optional. Every user message triggers classification. The user doesn't need to invoke question-classifier manually - it happens automatically.

---

**Status**: ✅ Question Pipeline Auto-Classification Active for this Session
