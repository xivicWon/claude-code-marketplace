# Validation Rules

## Required Field Validation

All documents MUST have:
- code
- grade
- gradeDescription
- itemName
- scenario
- persona (object with at least one user type)

Each persona MUST have:
- expectedResult (string)
- acceptanceCriteria (non-empty array)

## Format Validation

### code
- Pattern: `^(BS|TC)-\d{3}$`
- Examples: BS-001, TC-042, BS-123
- Invalid: BS001, BS-1, TC-1234

### grade
- Must be exactly: P1, P2, or P3
- Case-sensitive
- Invalid: p1, P4, High, Critical

### gradeDescription
- Must match grade:
  - P1 → "Critical"
  - P2 → "Major"
  - P3 → "Minor"
- Case-sensitive
- Invalid: "critical", "CRITICAL", "High"

### status (optional)
- If present, must be one of:
  - TODO
  - IN_PROGRESS
  - REVIEW
  - DONE
  - BLOCKED
- Case-sensitive
- Invalid: "todo", "In Progress", "Complete"

### priority (optional)
- If present, must be integer 1-5
- 1 = highest priority
- Invalid: 0, 6, "high", 1.5

### dueDate, completedDate (optional)
- If present, must be YYYY-MM-DD format
- Valid: "2026-01-23", "2026-12-31"
- Invalid: "2026/01/23", "01-23-2026", "2026-1-23"

## Business Logic Validation

### Uniqueness
- code must be unique across all documents in project
- Check existing documents before assigning new code

### Temporal Logic
- dueDate should be future date for incomplete items
- completedDate should only exist when status=DONE
- completedDate should be ≥ createdDate (if both present)

### Dependencies
- codes in dependencies array must reference existing documents
- Circular dependencies should be flagged (A depends on B, B depends on A)

## Error Messages

### Missing Required Field
```
❌ Validation Error: Missing required field

Field "grade" is required but not found.

Expected structure:
{
  "code": "BS-XXX",
  "grade": "P1|P2|P3",
  ...
}
```

### Invalid Code Format
```
❌ Validation Error: Invalid code format

Found: "BS001"
Expected: "BS-001"

Code must match pattern: (BS|TC)-XXX where XXX is 3 digits.
Examples: BS-001, TC-042
```

### Grade Mismatch
```
❌ Validation Error: gradeDescription doesn't match grade

Found: grade="P1", gradeDescription="High"
Expected: grade="P1", gradeDescription="Critical"

Valid mappings:
- P1 → "Critical"
- P2 → "Major"
- P3 → "Minor"
```

### Empty Acceptance Criteria
```
❌ Validation Error: Empty acceptanceCriteria

persona.normalUser.acceptanceCriteria is an empty array.

At least one acceptance criterion is required for each persona.
```

## Validation Checklist

Before processing a document, verify:

- [ ] All required fields present
- [ ] code matches ^(BS|TC)-\d{3}$
- [ ] grade is P1, P2, or P3
- [ ] gradeDescription matches grade
- [ ] persona is object with ≥1 user type
- [ ] Each persona has expectedResult (string)
- [ ] Each persona has non-empty acceptanceCriteria (array)
- [ ] status (if present) is valid enum value
- [ ] priority (if present) is 1-5
- [ ] dates (if present) are YYYY-MM-DD format
- [ ] dependencies (if present) reference existing codes
