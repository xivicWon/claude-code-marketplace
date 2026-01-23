# Common Patterns

Reusable patterns for common scenarios.

## Authentication & Authorization

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "안전하고 쉬운 로그인",
      "acceptanceCriteria": [
        "이메일/비밀번호로 로그인할 수 있다",
        "로그인 실패 시 명확한 에러 메시지가 표시된다",
        "비밀번호 재설정 링크를 받을 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "사용자 권한 관리 및 감사",
      "acceptanceCriteria": [
        "관리자는 사용자 역할을 변경할 수 있다",
        "모든 권한 변경이 감사 로그에 기록된다",
        "로그인 실패 패턴을 모니터링할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- User login/logout
- Role-based access control (RBAC)
- Permission management
- OAuth integration
- Two-factor authentication

## API Endpoints

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "빠르고 안정적인 API 응답",
      "acceptanceCriteria": [
        "API가 1초 이내에 응답한다",
        "에러 발생 시 적절한 HTTP 상태 코드를 반환한다",
        "API 문서를 통해 사용법을 확인할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "API 모니터링 및 문제 진단",
      "acceptanceCriteria": [
        "모든 API 호출이 로깅된다",
        "API 응답 시간 메트릭을 대시보드에서 확인할 수 있다",
        "에러 발생 시 스택 트레이스를 조회할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- REST API endpoints
- GraphQL resolvers
- WebSocket connections
- Webhook handlers
- API rate limiting

## Data Processing

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "정확한 데이터 처리 결과",
      "acceptanceCriteria": [
        "데이터 처리 진행률을 확인할 수 있다",
        "처리 완료 시 알림을 받는다",
        "처리 결과를 다운로드할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "데이터 처리 모니터링 및 오류 추적",
      "acceptanceCriteria": [
        "처리 실패한 데이터를 조회할 수 있다",
        "재처리를 수동으로 실행할 수 있다",
        "처리 성능 메트릭을 확인할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- Batch processing
- Data import/export
- ETL pipelines
- Report generation
- File uploads

## Search & Filtering

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "빠르고 정확한 검색 결과",
      "acceptanceCriteria": [
        "검색어 입력 시 1초 이내 결과가 표시된다",
        "검색 결과를 정렬할 수 있다",
        "검색 결과를 필터링할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "검색 품질 모니터링",
      "acceptanceCriteria": [
        "검색어별 결과 수를 확인할 수 있다",
        "검색 성능 메트릭을 대시보드에서 확인할 수 있다",
        "검색 인덱스를 재구축할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- Full-text search
- Faceted search
- Auto-complete
- Advanced filters
- Search analytics

## Notifications & Alerts

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "적시에 알림 수신",
      "acceptanceCriteria": [
        "중요 이벤트 발생 시 알림을 받는다",
        "알림 채널을 선택할 수 있다",
        "알림 설정을 변경할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "알림 시스템 관리",
      "acceptanceCriteria": [
        "알림 발송 이력을 조회할 수 있다",
        "알림 템플릿을 관리할 수 있다",
        "발송 실패 건을 재시도할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- Email notifications
- Push notifications
- SMS alerts
- In-app messages
- System alerts

## Reporting & Analytics

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "이해하기 쉬운 리포트",
      "acceptanceCriteria": [
        "리포트를 차트로 시각화할 수 있다",
        "리포트를 PDF/Excel로 다운로드할 수 있다",
        "기간을 선택하여 조회할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "상세 데이터 분석",
      "acceptanceCriteria": [
        "Raw 데이터를 조회할 수 있다",
        "커스텀 쿼리를 실행할 수 있다",
        "리포트 생성 이력을 확인할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- Business reports
- Usage analytics
- Performance dashboards
- Audit logs
- Custom reports

## File Management

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "쉬운 파일 업로드/다운로드",
      "acceptanceCriteria": [
        "드래그 앤 드롭으로 파일을 업로드할 수 있다",
        "업로드 진행률을 확인할 수 있다",
        "파일을 다운로드할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "파일 스토리지 관리",
      "acceptanceCriteria": [
        "전체 파일 목록을 조회할 수 있다",
        "스토리지 사용량을 확인할 수 있다",
        "오래된 파일을 정리할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- File uploads
- Document management
- Image galleries
- Attachment handling
- Storage quotas

## User Profile & Settings

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "개인 정보 관리",
      "acceptanceCriteria": [
        "프로필 정보를 수정할 수 있다",
        "비밀번호를 변경할 수 있다",
        "알림 설정을 변경할 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "사용자 관리 및 감사",
      "acceptanceCriteria": [
        "모든 사용자 목록을 조회할 수 있다",
        "사용자 정보 변경 이력을 확인할 수 있다",
        "계정을 비활성화할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- User profiles
- Account settings
- Preferences management
- Privacy settings
- Account deletion

## Form Validation

### Pattern

```json
{
  "persona": {
    "normalUser": {
      "expectedResult": "명확한 입력 가이드",
      "acceptanceCriteria": [
        "필수 필드가 표시된다",
        "입력 오류 시 구체적인 메시지가 표시된다",
        "입력 형식 예시가 제공된다"
      ]
    },
    "operationUser": {
      "expectedResult": "검증 규칙 관리",
      "acceptanceCriteria": [
        "검증 실패 로그를 확인할 수 있다",
        "검증 규칙을 수정할 수 있다",
        "검증 통과율을 모니터링할 수 있다"
      ]
    }
  }
}
```

### Use Cases
- Form submissions
- Data validation
- Input sanitization
- Business rule validation
- Cross-field validation
