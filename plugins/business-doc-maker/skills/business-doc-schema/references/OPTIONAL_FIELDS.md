# Optional Fields Reference

Complete reference for all optional fields that can be added to business documents.

## Project Management Fields

### status
**Type**: String
**Values**: TODO, IN_PROGRESS, REVIEW, DONE, BLOCKED
**Description**: Current state of the work

**Workflow**:
```
TODO → IN_PROGRESS → REVIEW → DONE
         ↓
      BLOCKED (temporary state)
```

**Example**:
```json
{
  "status": "IN_PROGRESS"
}
```

### priority
**Type**: Number (1-5)
**Description**: Urgency level (1 = highest)
**Note**: Complements grade (importance)

**Guidelines**:
- P1 + priority 1 = Critical and urgent
- P1 + priority 3 = Critical but can wait
- P3 + priority 1 = Minor but urgent (quick win)

**Example**:
```json
{
  "grade": "P1",
  "priority": 1
}
```

### assignee
**Type**: String
**Description**: Person responsible for implementation

**Example**:
```json
{
  "assignee": "김철수"
}
```

### reviewer
**Type**: String
**Description**: Person reviewing the work

**Example**:
```json
{
  "reviewer": "박영희"
}
```

## Effort & Timeline Fields

### estimatedEffort
**Type**: String
**Format**: "{number}{unit}"
**Units**: h (hours), d (days), w (weeks)

**Examples**:
```json
{
  "estimatedEffort": "5d"     // 5 days
}
{
  "estimatedEffort": "2-3d"   // 2-3 days (range)
}
{
  "estimatedEffort": "1w"     // 1 week
}
```

### actualEffort
**Type**: String
**Format**: Same as estimatedEffort
**Description**: Actual time taken

**Example**:
```json
{
  "estimatedEffort": "5d",
  "actualEffort": "7d"
}
```

### dueDate
**Type**: String
**Format**: YYYY-MM-DD
**Description**: Target completion date

**Example**:
```json
{
  "dueDate": "2026-02-15"
}
```

### completedDate
**Type**: String
**Format**: YYYY-MM-DD
**Description**: Actual completion date (only when status=DONE)

**Example**:
```json
{
  "status": "DONE",
  "completedDate": "2026-02-20"
}
```

## Organization Fields

### module
**Type**: String
**Description**: Module or feature area

**Examples**:
- "auth" - Authentication module
- "payment" - Payment processing
- "reporting" - Reporting system
- "core" - Core infrastructure

**Example**:
```json
{
  "module": "auth"
}
```

### category
**Type**: String
**Description**: Broad category classification

**Examples**:
- "Security"
- "Performance"
- "User Experience"
- "Infrastructure"

**Example**:
```json
{
  "category": "Security"
}
```

### tags
**Type**: Array of strings
**Description**: Flexible classification tags

**Tag Categories**:
- Technical: "api", "database", "frontend", "backend"
- Domain: "payment", "user-management", "reporting"
- Type: "bug-fix", "refactoring", "new-feature"
- Quality: "tech-debt", "performance", "security"

**Example**:
```json
{
  "tags": ["api", "authentication", "security", "backend"]
}
```

### version
**Type**: String
**Description**: Target release version

**Example**:
```json
{
  "version": "1.2.0"
}
```

## Relationship Fields

### dependencies
**Type**: Array of strings (codes)
**Description**: Documents that must be completed first

**Example**:
```json
{
  "dependencies": ["BS-001", "BS-003"]
}
```

**Notes**:
- Only list direct blockers
- Don't include transitive dependencies
- Each code must exist in the project

### relatedItems
**Type**: Array of strings (codes)
**Description**: Related but not blocking documents

**Example**:
```json
{
  "relatedItems": ["TC-001", "BS-005"]
}
```

## Tracking Fields

### createdBy
**Type**: String
**Description**: Person who created the document

**Example**:
```json
{
  "createdBy": "홍길동"
}
```

### createdDate
**Type**: String
**Format**: ISO 8601 timestamp
**Description**: When the document was created

**Example**:
```json
{
  "createdDate": "2026-01-23T10:00:00Z"
}
```

### updatedBy
**Type**: String
**Description**: Person who last updated the document

**Example**:
```json
{
  "updatedBy": "김철수"
}
```

### updatedDate
**Type**: String
**Format**: ISO 8601 timestamp
**Description**: When the document was last updated

**Example**:
```json
{
  "updatedDate": "2026-01-24T15:30:00Z"
}
```

## Complete Example

All optional fields in use:

```json
{
  "code": "BS-001",
  "grade": "P1",
  "gradeDescription": "Critical",
  "itemName": "예외 처리 표준화",
  "scenario": "...",
  "persona": { ... },

  "status": "IN_PROGRESS",
  "priority": 1,
  "assignee": "김철수",
  "reviewer": "박영희",

  "estimatedEffort": "5d",
  "actualEffort": "7d",
  "dueDate": "2026-02-15",
  "completedDate": "2026-02-20",

  "module": "core",
  "category": "Infrastructure",
  "tags": ["exception", "error-handling", "logging"],
  "version": "1.0.0",

  "dependencies": ["BS-002"],
  "relatedItems": ["TC-001", "BS-005"],

  "createdBy": "홍길동",
  "createdDate": "2026-01-23T10:00:00Z",
  "updatedBy": "김철수",
  "updatedDate": "2026-01-24T15:30:00Z"
}
```

## Custom Fields

Projects may add custom fields beyond this list. Common custom fields:

```json
{
  "epic": "사용자 관리",
  "sprint": "2026-Q1-Sprint3",
  "storyPoints": 8,
  "testCoverage": 85,
  "reviewComments": "...",
  "implementationNotes": "..."
}
```

Best practices for custom fields:
- Use camelCase naming
- Document their purpose
- Validate their values
- Keep them consistent across documents
