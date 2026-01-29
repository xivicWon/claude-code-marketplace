#!/usr/bin/env python3
"""UserPromptSubmit hook for question-pipeline auto-classification.

Automatically classifies user questions into:
- EXPLORATION (이해 필요): Free AI response
- DECISION (판단 필요): Light pipeline support
- EXECUTION (실행 필요): Full pipeline
"""

import os
import sys
import json
import re


def classify_question(question: str) -> dict:
    """Classify user question into EXPLORATION, DECISION, or EXECUTION."""

    # Signal patterns with weights
    exploration_patterns = [
        (r'(뭐|무엇|무슨).*(야|지|니|까)', 0.9),
        (r'왜.*(야|지|니|까|해)', 0.9),
        (r'어디.*(야|서|에)', 0.9),
        (r'어떻게.*(돼|되|야)', 0.8),
        (r'설명해줘', 0.9),
        (r'알려줘', 0.7),
        (r'확인해줘', 0.6),
        (r'찾아줘', 0.6),
    ]

    decision_patterns = [
        (r'(뭐|어떤|어느).*(나아|나을)', 0.95),
        (r'(뭐|어떤|어느).*(좋아|좋을)', 0.9),
        (r'괜찮[을나아]', 0.85),
        (r'문제.*없[을나을까]', 0.85),
        (r'해도.*될까', 0.9),
        (r'할까.*말까', 0.95),
        (r'\bvs\b|VS', 0.9),
    ]

    execution_patterns = [
        (r'만들어줘', 0.95),
        (r'수정해줘', 0.95),
        (r'추가해줘', 0.95),
        (r'삭제해줘', 0.95),
        (r'구현해줘', 0.95),
        (r'작성해줘', 0.9),
        (r'고쳐줘', 0.9),
        (r'바꿔줘', 0.9),
        (r'적용해줘', 0.9),
        (r'제거해줘', 0.9),
    ]

    # Calculate scores
    scores = {
        'EXPLORATION': 0.0,
        'DECISION': 0.0,
        'EXECUTION': 0.0
    }

    matched_signals = []

    # Check exploration patterns
    for pattern, weight in exploration_patterns:
        if re.search(pattern, question):
            scores['EXPLORATION'] += weight
            matched_signals.append({
                'signal': pattern,
                'weight': weight,
                'type': 'EXPLORATION'
            })

    # Check decision patterns
    for pattern, weight in decision_patterns:
        if re.search(pattern, question):
            scores['DECISION'] += weight
            matched_signals.append({
                'signal': pattern,
                'weight': weight,
                'type': 'DECISION'
            })

    # Check execution patterns
    for pattern, weight in execution_patterns:
        if re.search(pattern, question):
            scores['EXECUTION'] += weight
            matched_signals.append({
                'signal': pattern,
                'weight': weight,
                'type': 'EXECUTION'
            })

    # Determine classification
    max_score = max(scores.values())

    if max_score == 0:
        # No clear signal - fallback to EXECUTION (safer)
        classification_type = 'EXECUTION'
        confidence = 0.3
        reason = "신호 불명확, 안전한 EXECUTION으로 fallback"
    else:
        classification_type = max(scores, key=scores.get)
        confidence = min(max_score / 2.0, 1.0)  # Normalize to 0-1 range
        reason = f"{classification_type} 신호 감지 (score: {max_score:.2f})"

    # Build suggested pipeline
    if classification_type == 'EXPLORATION':
        suggested_pipeline = []
        pipeline_message = "탐색 질문 - AI 자유 응답"
    elif classification_type == 'DECISION':
        suggested_pipeline = [
            'question-pipeline:intent-clarifier',
            'question-pipeline:ambiguity-scanner (light mode)'
        ]
        pipeline_message = "결정 질문 - 비교 분석 지원"
    else:  # EXECUTION
        suggested_pipeline = [
            'question-pipeline:ambiguity-scanner',
            'question-pipeline:intent-clarifier',
            'question-pipeline:question-normalizer',
            'question-pipeline:datatable-pattern-resolver',
            'question-pipeline:datatable-creator',
            'question-pipeline:pattern-drift-detector'
        ]
        pipeline_message = "실행 질문 - 전체 파이프라인 적용"

    return {
        'classification': {
            'type': classification_type,
            'confidence': round(confidence, 2),
            'reason': reason
        },
        'matchedSignals': matched_signals,
        'suggestedPipeline': suggested_pipeline,
        'pipelineMessage': pipeline_message
    }


def format_classification_message(result: dict, user_prompt: str) -> str:
    """Format classification result as a readable message."""
    cls = result['classification']
    cls_type = cls['type']
    confidence = cls['confidence']

    # Type emoji and Korean
    type_info = {
        'EXPLORATION': ('🔍', '탐색', '정보 확인/이해 목적'),
        'DECISION': ('🤔', '결정', '비교/판단 지원'),
        'EXECUTION': ('⚙️', '실행', '구체적 구현 요청')
    }

    emoji, korean, description = type_info[cls_type]

    message = f"""# 🎯 Auto Question Classification

**사용자 질문**: "{user_prompt}"

**분류 결과**: {emoji} **{cls_type}** ({korean})
**신뢰도**: {confidence:.0%}
**설명**: {description}

---

## Claude, 다음과 같이 처리하세요:

{result['pipelineMessage']}
"""

    if result['suggestedPipeline']:
        message += "\n### 권장 파이프라인 순서\n\n"
        for i, skill in enumerate(result['suggestedPipeline'], 1):
            message += f"{i}. {skill}\n"
        message += "\n**IMPORTANT**: 위 스킬들을 순서대로 사용하여 질문을 처리하세요.\n"
    else:
        message += "\n**IMPORTANT**: 추가 스킬 없이 자유롭게 응답하세요. 질문의 의도를 파악하고 직접 답변하시면 됩니다.\n"

    if result['matchedSignals']:
        message += "\n### 분류 근거 (매칭된 신호)\n\n"
        for sig in result['matchedSignals'][:3]:  # Show top 3
            message += f"- `{sig['signal']}` (가중치: {sig['weight']}, 타입: {sig['type']})\n"

    message += "\n---\n\n**Remember**: 이 분류는 자동으로 수행되었습니다. 분류 결과에 따라 적절한 처리 방식을 선택하세요."

    return message


def main():
    """Main entry point for UserPromptSubmit hook."""
    # Debug log file
    debug_log = os.path.join(os.path.dirname(__file__), 'hook-debug.log')

    print("user-prompt-submit hook started", file=sys.stderr)
    try:
        with open(debug_log, 'a') as f:
            f.write(f"\n=== Hook called at {__import__('datetime').datetime.now()} ===\n")
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Extract user prompt
        user_prompt = input_data.get('userPrompt', '')

        if not user_prompt:
            # No prompt to classify
            print(json.dumps({'continue': True}), file=sys.stdout)
            sys.exit(0)

        # Classify the question
        classification_result = classify_question(user_prompt)

        # Debug log
        with open(debug_log, 'a') as f:
            f.write(f"User prompt: {user_prompt}\n")
            f.write(f"Classification: {classification_result['classification']}\n")

        # Format message
        message = format_classification_message(classification_result, user_prompt)

        # Output result with visible systemMessage
        cls_type = classification_result['classification']['type']
        confidence = classification_result['classification']['confidence']
        pipeline_msg = classification_result['pipelineMessage']

        output = {
            'continue': True,
            'systemMessage': f'✓ 질문 분류: {cls_type} ({confidence:.0%} 신뢰도) - {pipeline_msg}',
            'suppressOutput': False,
            'hookSpecificOutput': {
                'hookEventName': 'UserPromptSubmit',
                'additionalContext': message
            }
        }

        # Debug log output
        with open(debug_log, 'a') as f:
            f.write(f"Output JSON:\n{json.dumps(output, indent=2, ensure_ascii=False)}\n")

        print(json.dumps(output), file=sys.stdout)

    except Exception as e:
        # On error, continue without classification
        with open(debug_log, 'a') as f:
            f.write(f"ERROR: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())

        error_output = {
            'continue': True,
            'systemMessage': f'Question classification error: {str(e)}'
        }
        print(json.dumps(error_output), file=sys.stdout)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
