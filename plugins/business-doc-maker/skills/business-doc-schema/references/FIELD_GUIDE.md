# Field Writing Guide

Complete guide for writing effective business document fields.

## code

**Format**: `{PREFIX}-{NUMBER}`
- Prefix: BS (Business Scenario) or TC (Test Case)
- Number: Zero-padded 3 digits

**Best Practices**:
- Use sequential numbering (BS-001, BS-002, BS-003)
- Don't skip numbers unless specific reason
- BS for features/requirements, TC for testing

**Examples**:
- ✅ BS-001, TC-042, BS-123
- ❌ BS001, BS-1, BUS-001

## itemName

**Length**: 3-8 words
**Style**: Noun phrases, specific, descriptive

**Good Examples**:
- "예외 처리 표준화"
- "사용자 로그인 API 구현"
- "실시간 알림 시스템"

**Bad Examples**:
- "개선" (too vague)
- "작업" (too generic)
- "사용자가 로그인하고 데이터를 조회하며 결과를 확인하는 기능" (too long)

## scenario

**Length**: 2-5 sentences
**Content**: Context + Why (not just What)

**Structure**:
1. What is being built/tested
2. Business justification
3. Key requirements or constraints

**Good Example**:
```
시스템 전반에 걸쳐 일관된 예외 처리 메커니즘을 구현하여 에러 추적 및
디버깅을 용이하게 합니다. 비즈니스 로직 오류, 유효성 검증 실패, 시스템
오류 등을 명확히 구분하고, 각 예외 유형에 대한 적절한 HTTP 상태 코드와
에러 메시지를 반환합니다.
```

**Bad Example**:
```
예외 처리를 한다.
```

## expectedResult

**Format**: Numbered list or paragraph
**Focus**: Outcomes, not implementation
**Persona-specific**: Different for each user type

**normalUser Example**:
```
1. 이해하기 쉬운 에러 메시지
2. 에러 코드를 통한 문제 식별
3. 문제 해결을 위한 가이드 제공
```

**operationUser Example**:
```
1. 계층화된 예외 클래스 구조
2. 글로벌 예외 핸들러를 통한 통합 처리
3. 일관된 에러 응답 포맷
4. 상세한 스택 트레이스 로깅
5. 에러 발생 통계 및 모니터링
```

**Key Principles**:
- Describe WHAT users get, not HOW it's built
- Be specific and measurable
- Focus on value delivered to that persona

## acceptanceCriteria

**Requirements**:
- Must be testable
- Clear and unambiguous
- Action-oriented
- Include positive AND negative cases
- Atomic (one thing per criterion)

### Writing Style

**Use Given-When-Then** (when applicable):
```
Given a logged-in user
When they click logout
Then they are redirected to the login page
```

**Or simple declarative** (for Korean):
```
에러 발생 시 사용자가 이해할 수 있는 한글 메시지가 표시된다
```

### Good Examples

✅ **Testable**:
- "올바른 이메일/비밀번호 입력 시 메인 페이지로 리다이렉트된다"
- "API 응답 시간이 95 percentile 기준 500ms 이하이다"
- "파일 업로드 크기는 10MB로 제한된다"
- "잘못된 비밀번호 입력 시 401 에러를 반환한다"

✅ **Specific**:
- "모든 API 호출이 JSON 형식으로 로깅된다"
- "5회 연속 로그인 실패 시 계정이 30분간 잠긴다"
- "관리자는 사용자 역할을 ADMIN/USER/OPERATOR 중 하나로 변경할 수 있다"

✅ **Observable Behavior**:
- "에러 발생 시 한글 메시지가 표시된다"
- "데이터 처리 진행률을 퍼센트로 확인할 수 있다"
- "운영자 대시보드에서 에러 발생 추이를 확인할 수 있다"

### Bad Examples

❌ **Not Testable**:
- "에러 처리가 잘 된다"
- "성능이 좋다"
- "사용자 경험 개선"
- "안정적으로 동작한다"

❌ **Too Vague**:
- "빠른 응답"
- "적절한 에러 메시지"
- "필요한 정보 제공"

❌ **Implementation Details** (should be in expectedResult or scenario):
- "Redis 캐시를 사용한다"
- "JWT 토큰으로 인증한다"
- "Spring Boot의 @RestControllerAdvice를 사용한다"

### Negative Cases

Always include negative/error cases:

**Login Example**:
- ✅ "올바른 계정 정보 입력 시 로그인 성공"
- ✅ "잘못된 비밀번호 입력 시 '비밀번호가 올바르지 않습니다' 메시지 표시"
- ✅ "존재하지 않는 이메일 입력 시 '가입되지 않은 이메일입니다' 메시지 표시"

**API Example**:
- ✅ "정상 요청 시 200 OK와 데이터 반환"
- ✅ "인증되지 않은 요청 시 401 Unauthorized 반환"
- ✅ "잘못된 파라미터 시 400 Bad Request와 에러 상세 반환"

### Atomicity

Each criterion should test ONE thing:

❌ Bad (multiple things):
```
"로그인 성공 시 메인 페이지로 이동하고 세션이 생성되며 환영 메시지가 표시된다"
```

✅ Good (atomic):
```
- "로그인 성공 시 메인 페이지로 리다이렉트된다"
- "로그인 성공 시 세션이 생성된다"
- "로그인 성공 시 '환영합니다' 메시지가 표시된다"
```

## Optional Fields Best Practices

### status
Use consistent workflow:
- TODO → IN_PROGRESS → REVIEW → DONE
- Use BLOCKED for dependencies or issues

### priority
Complement grade with urgency:
- P1 + priority 1 = Critical and urgent
- P1 + priority 3 = Critical but can wait
- P3 + priority 1 = Minor but urgent (quick win)

### tags
Use for cross-cutting concerns:
```json
{
  "tags": ["api", "authentication", "security", "backend"]
}
```

Good tag categories:
- Technical: "api", "database", "frontend", "backend"
- Domain: "payment", "user-management", "reporting"
- Type: "bug-fix", "refactoring", "new-feature"
- Quality: "tech-debt", "performance", "security"

### dependencies
List blocking requirements:
```json
{
  "dependencies": ["BS-001", "BS-003"]
}
```

Only include direct blockers, not transitive.

### estimatedEffort
Use consistent format:
- "3h" = 3 hours
- "2d" = 2 days
- "1w" = 1 week
- "2-3d" = range

Be realistic, include testing time.
