---
name: business-doc-schema
description: "Business document JSON schema, templates, validation rules, and standard definitions for BS (Business Scenario) and TC (Test Case) documents. Use when: (1) User requests 'init' or template generation, (2) Validating business document structure, (3) Understanding document field definitions, (4) Creating new BS/TC documents, (5) Checking grade levels, code formats, or persona structures"
---

# Business Document Schema

Standard structure for business scenario (BS) and test case (TC) documents used in project planning and requirement tracking.

## Quick Reference

### Required Fields

- **code**: Unique ID (BS-001, TC-042)
- **grade**: P1 (Critical), P2 (Major), P3 (Minor)
- **gradeDescription**: Matches grade
- **itemName**: Brief title
- **scenario**: Detailed description
- **persona**: Object with user-type requirements
  - Each persona: `expectedResult` + `acceptanceCriteria` array

### Code Formats

- **BS-XXX**: Business Scenario (features, requirements)
- **TC-XXX**: Test Case (testing scenarios)
- Pattern: `^(BS|TC)-\d{3}$`

### Grade Levels

| Grade | Description | Use For |
|-------|-------------|---------|
| P1 | Critical | Security, data integrity, system stability |
| P2 | Major | UX, operations, important features |
| P3 | Minor | Enhancements, polish, nice-to-haves |

### Standard Personas

- **normalUser**: End user focus (usability, clarity)
- **operationUser**: Admin focus (management, debugging, monitoring)

## Templates

### Minimal (Required Fields Only)

```json
{
  "code": "BS-XXX",
  "grade": "P1",
  "gradeDescription": "Critical",
  "itemName": "",
  "scenario": "",
  "persona": {
    "normalUser": {
      "expectedResult": "",
      "acceptanceCriteria": []
    },
    "operationUser": {
      "expectedResult": "",
      "acceptanceCriteria": []
    }
  }
}
```

### Standard (With Common Optional Fields)

```json
{
  "code": "BS-XXX",
  "grade": "P2",
  "gradeDescription": "Major",
  "itemName": "",
  "scenario": "",
  "persona": {
    "normalUser": {
      "expectedResult": "",
      "acceptanceCriteria": []
    },
    "operationUser": {
      "expectedResult": "",
      "acceptanceCriteria": []
    }
  },
  "status": "TODO",
  "priority": 1,
  "assignee": "",
  "estimatedEffort": "5d",
  "dueDate": "2026-MM-DD",
  "tags": [],
  "dependencies": []
}
```

See [TEMPLATES.md](references/TEMPLATES.md) for extended template with all tracking fields.

## Validation Rules

**Required**:
- All 6 core fields must exist
- code matches `^(BS|TC)-\d{3}$`
- grade is P1, P2, or P3
- gradeDescription matches grade
- persona has ≥1 user type
- Each persona has expectedResult + non-empty acceptanceCriteria array

**Format**:
- status (if present): TODO, IN_PROGRESS, REVIEW, DONE, BLOCKED
- priority (if present): 1-5
- dueDate (if present): YYYY-MM-DD

See [VALIDATION.md](references/VALIDATION.md) for complete rules and error messages.

## Field Guidelines

### acceptanceCriteria

Write testable, specific criteria:

✅ Good:
- "에러 발생 시 사용자가 이해할 수 있는 한글 메시지가 표시된다"
- "API 응답 시간이 95 percentile 기준 500ms 이하이다"

❌ Bad:
- "에러 처리가 잘 된다" (not testable)
- "성능이 좋다" (not measurable)

### expectedResult

Focus on outcomes, not implementation. Use numbered lists. Be persona-specific.

### scenario

2-5 sentences. Explain the "why" not just the "what". Include business context.

See [FIELD_GUIDE.md](references/FIELD_GUIDE.md) for all field best practices.

## Examples

### Security Feature (P1)

```json
{
  "code": "BS-001",
  "grade": "P1",
  "gradeDescription": "Critical",
  "itemName": "예외 처리 표준화",
  "scenario": "시스템 전반에 걸쳐 일관된 예외 처리 메커니즘 구현",
  "persona": {
    "normalUser": {
      "expectedResult": "1. 이해하기 쉬운 에러 메시지\n2. 에러 코드로 문제 식별\n3. 해결 가이드 제공",
      "acceptanceCriteria": [
        "에러 발생 시 한글 메시지 표시",
        "기술 세부사항 미노출",
        "에러 코드로 문의 가능"
      ]
    },
    "operationUser": {
      "expectedResult": "1. 계층화된 예외 구조\n2. 글로벌 핸들러\n3. 일관된 포맷\n4. 상세 로깅\n5. 통계 모니터링",
      "acceptanceCriteria": [
        "커스텀 예외로 변환",
        "스택 트레이스 로깅",
        "요청 정보 기록",
        "대시보드에서 추이 확인"
      ]
    }
  }
}
```

See [EXAMPLES.md](references/EXAMPLES.md) for more examples including test cases, user features, and common patterns.

## Optional Fields

Common optional fields for project tracking:

- **status**, **priority**, **assignee**, **reviewer**
- **estimatedEffort**, **actualEffort**, **dueDate**, **completedDate**
- **module**, **category**, **tags**, **version**
- **dependencies**, **relatedItems**
- **createdBy**, **createdDate**, **updatedBy**, **updatedDate**

See [OPTIONAL_FIELDS.md](references/OPTIONAL_FIELDS.md) for complete list and usage.

## Common Patterns

### Authentication/Authorization

normalUser: "안전하고 쉬운 로그인"
operationUser: "권한 관리 및 감사"

### API Endpoints

normalUser: "빠르고 안정적인 응답"
operationUser: "모니터링 및 진단"

### Data Processing

normalUser: "정확한 결과 확인"
operationUser: "오류 추적 및 재처리"

See [PATTERNS.md](references/PATTERNS.md) for detailed pattern catalog.

## Usage

This skill provides command-based interface for business document management.

### Available Commands

**help** - Show usage guide
**create** - Create new business document (auto-detects complexity)
**doctor [issue]** - Validate and diagnose document issues

### Command: help

Display comprehensive usage guide for users.

**Trigger**: User says "help", "how to use", "가이드"

**Action**:
1. Read `references/USER_GUIDE.md`
2. Display relevant sections based on user's question
3. Provide quick start examples

**Example**:
```
User: "business-doc-schema help"
→ Show USER_GUIDE.md overview + quick start
```

### Command: create

Create new business document with automatic complexity detection.

**Trigger**: User says "create", "new document", "BS-XXX 만들어줘"

**Workflow**:

1. **Gather Input** (flexible format)
   - Ask user to describe what they want (free form)
   - Accept markdown, bullet points, or natural language
   - Minimal required: what, why, who, priority

2. **Analyze Complexity** (automatic)
   Evaluate based on:
   - Number of systems involved
   - External integrations needed
   - Business logic complexity
   - Estimated effort
   - User-stated priority

   **Complexity Matrix**:
   ```
   Simple (2-stage):
   - Single component
   - No external integration
   - < 5 days effort
   - P3 priority

   Medium (4-stage, no plan):
   - Multiple components
   - Some external integration
   - 5-10 days effort
   - P2 priority

   Complex (4-stage, full):
   - New subsystem
   - Multiple external integrations
   - > 10 days effort
   - P1 priority
   ```

3. **Generate Documents**

   **For Simple (2-stage)**:
   ```
   docs/business-doc-analyzer/BS-XXX/
   └── scenario.for-ai.json
   ```

   **For Medium (4-stage, no plan)**:
   ```
   docs/business-doc-analyzer/BS-XXX/
   ├── scenario-request.for-human.md
   ├── scenario.for-ai.json
   └── report-readme.for-human.md (after analysis)
   ```

   **For Complex (4-stage, full)**:
   ```
   docs/business-doc-analyzer/BS-XXX/
   ├── scenario-request.for-human.md
   ├── scenario.for-ai.json
   ├── report-plan.for-ai.json
   ├── report-readme.for-human.md
   └── analysis-report.for-human.md
   ```

4. **Confirm with User**
   ```
   ✓ Complexity detected: Medium
   ✓ Pipeline: 4-stage (streamlined)
   ✓ Generated: scenario-request.for-human.md
   ✓ Generated: scenario.for-ai.json

   Next steps:
   1. Review scenario.for-ai.json
   2. Run analysis when ready
   ```

**Example Interaction**:
```
User: "create BS-003"

AI: "무엇을 만들고 싶으신가요? 자유롭게 설명해주세요."

User: "사용자가 프로필 사진을 업로드하고 수정할 수 있으면 좋겠어요.
지금은 기본 아이콘만 있어서 구분이 안 돼요."

AI: [Analyzes complexity]
→ Simple task (file upload, basic CRUD)
→ Uses 2-stage pipeline

✓ Created: docs/business-doc-analyzer/BS-003/scenario.for-ai.json
✓ Complexity: Simple (2-stage)
✓ Ready for analysis
```

### Command: doctor [issue]

Validate and diagnose existing documents.

**Trigger**: User says "doctor", "validate BS-XXX", "check document"

**Usage**:
```bash
# Validate specific document
doctor BS-001

# Check all documents
doctor --all

# Fix issues automatically
doctor BS-001 --fix
```

**Checks**:

1. **Schema Validation**
   - All required fields present
   - Code format: `^(BS|TC)-\d{3}$`
   - Grade matches gradeDescription
   - Persona structure correct

2. **Content Quality**
   - acceptanceCriteria are testable
   - expectedResult is specific
   - scenario provides context
   - No vague terms ("잘", "좋게")

3. **Consistency**
   - Grade matches priority
   - Dependencies exist
   - Related items valid

4. **File Structure**
   - Correct naming (for-ai, for-human)
   - Required files present for complexity level
   - No orphaned files

**Output**:
```
Diagnosing BS-001...

✅ Schema: Valid
✅ Code format: BS-001 ✓
✅ Grade: P1 (Critical) ✓

⚠️ Content Issues:
- acceptanceCriteria[1]: "잘 처리된다" → Not testable
  Suggestion: "5초 이내에 처리 완료된다"

- expectedResult: Too vague
  Suggestion: Add specific outcomes

❌ Structure Issues:
- Missing: report-readme.for-human.md (expected for P1)

📊 Summary:
- Schema: ✅ Pass
- Content: ⚠️ 1 warning
- Structure: ❌ 1 error

Run 'doctor BS-001 --fix' to auto-fix?
```

**Auto-fix** (with --fix flag):
- Generate missing files
- Suggest specific acceptanceCriteria
- Standardize terminology
- Fix formatting

### Legacy: init (deprecated, use 'create')

For backward compatibility, "init" still works:

User says "init" or requests template:
1. Redirect to 'create' command
2. Suggest using new workflow

### Understanding Structure

Reference this skill when:
- Creating new documents
- Checking field meanings
- Understanding grade levels
- Writing acceptance criteria
- Choosing BS vs TC
- Using commands (help/create/doctor)

## Analysis Report Format

When analyzing business documents, use the standard report template.

See [REPORT_TEMPLATE.md](references/REPORT_TEMPLATE.md) for:
- Complete report structure
- Coverage calculation formulas
- Approach decision matrix
- Effort estimation guidelines
- Writing tips and best practices

**Quick Reference**:
- Coverage % = (Fully Met / Total) × 100
- Approach: 60-100% = Extend, 30-60% = Refactor, 0-30% = New
- Priority: P1 = High, P2 = Medium, P3 = Low
- Use ✅ ⚠️ ❌ for status indicators

## Integration

This skill is used by `business-doc-analyzer` agent for:
- Template generation (JSON documents)
- Document validation (structure & fields)
- Field interpretation & best practices
- Report generation (analysis output)
