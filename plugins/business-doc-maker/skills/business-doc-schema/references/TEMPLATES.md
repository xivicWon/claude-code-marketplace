# Document Templates

## Extended Template (All Tracking Fields)

Complete template with all optional project management and tracking fields:

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
  },

  "status": "TODO",
  "priority": 1,
  "assignee": "",
  "reviewer": "",
  "estimatedEffort": "5d",
  "actualEffort": "",
  "dueDate": "2026-MM-DD",
  "completedDate": "",

  "module": "",
  "category": "",
  "tags": [],
  "version": "1.0.0",

  "dependencies": [],
  "relatedItems": [],

  "createdBy": "",
  "createdDate": "",
  "updatedBy": "",
  "updatedDate": ""
}
```

## Template Selection Guide

**Minimal**: Use for quick requirement capture, early planning, spikes
**Standard**: Use for typical development work with basic tracking
**Extended**: Use for enterprise projects requiring full traceability
