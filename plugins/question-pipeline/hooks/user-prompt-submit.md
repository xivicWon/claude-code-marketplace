---
event: UserPromptSubmit
description: Automatically classify user questions using question-classifier and route to appropriate pipeline
enabled: true
---

# Auto Question Classification

You MUST classify every user question before responding.

## Classification Process

1. **Analyze the user's message** using question-classifier criteria
2. **Determine the type**: EXPLORATION, DECISION, or EXECUTION
3. **Follow the appropriate pipeline** based on classification

## Classification Criteria

### EXPLORATION (탐색)
- Intent: Information gathering, understanding, exploration
- Signals: "뭐야", "왜", "어디", "설명해줘", "알려줘", "확인해줘"
- Action: Respond freely without additional skills

### DECISION (결정)
- Intent: Helping with choices and judgments
- Signals: "뭐가 나아", "어떤 게 좋아", "괜찮을까", "vs", "선택"
- Action: Use IntentClarifier + AmbiguityScanner (light mode)

### EXECUTION (실행)
- Intent: Concrete implementation, creation, modification
- Signals: "만들어줘", "수정해줘", "추가해줘", "삭제해줘", "구현해줘"
- Action: Apply full pipeline (AmbiguityScanner → IntentClarifier → QuestionNormalizer → etc.)

## Required Response Format

For every user message, you MUST internally classify it first, then:

**For EXPLORATION:**
- Respond directly and freely
- Optional: Briefly mention "탐색 질문으로 분류했습니다"

**For DECISION:**
- Use question-pipeline:intent-clarifier skill (if needed)
- Use question-pipeline:ambiguity-scanner skill with light mode (if needed)
- Provide comparison and analysis

**For EXECUTION:**
- MANDATORY: Use full question-pipeline
- Start with question-pipeline:ambiguity-scanner
- Then question-pipeline:intent-clarifier
- Then question-pipeline:question-normalizer (if needed)
- Execute the implementation

## Confidence Handling

- **High confidence (≥ 0.7)**: Proceed with classification
- **Medium (0.5-0.7)**: Ask user to clarify intent
- **Low (< 0.5)**: Default to EXECUTION (safer)

## Example Workflow

User: "이 함수가 뭐하는 거야?"
→ Classification: EXPLORATION (confidence: 0.95)
→ Action: Explain freely

User: "Redux랑 Context 중에 뭐가 나아?"
→ Classification: DECISION (confidence: 0.92)
→ Action: IntentClarifier + AmbiguityScanner (light)

User: "로그인 페이지 만들어줘"
→ Classification: EXECUTION (confidence: 0.95)
→ Action: Full pipeline

---

**Remember**: This classification happens automatically for EVERY user message. You don't need to explain the classification process unless it's helpful for the user.
