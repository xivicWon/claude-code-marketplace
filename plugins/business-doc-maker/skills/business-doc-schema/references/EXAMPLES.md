# Document Examples

## Example 1: User Feature (P2, Major)

```json
{
  "code": "BS-002",
  "grade": "P2",
  "gradeDescription": "Major",
  "itemName": "사용자 알림 시스템",
  "scenario": "사용자에게 중요 이벤트와 시스템 상태를 실시간으로 알립니다. 이메일, SMS, 푸시 알림 등 다양한 채널을 지원하며, 사용자별 알림 설정을 관리할 수 있어야 합니다.",

  "persona": {
    "normalUser": {
      "expectedResult": "1. 실시간 알림 수신\n2. 알림 채널 선택 가능 (이메일/SMS/푸시)\n3. 알림 on/off 설정",
      "acceptanceCriteria": [
        "중요 이벤트 발생 시 5분 이내 알림 수신",
        "설정 페이지에서 알림 채널을 선택할 수 있다",
        "알림을 끌 수 있다"
      ]
    },
    "operationUser": {
      "expectedResult": "1. 알림 발송 이력 조회\n2. 알림 템플릿 관리\n3. 발송 실패 모니터링 및 재시도",
      "acceptanceCriteria": [
        "관리자 페이지에서 모든 알림 발송 이력을 조회할 수 있다",
        "알림 템플릿을 생성/수정/삭제할 수 있다",
        "발송 실패 시 자동 재시도되며 3회 실패 시 관리자에게 알림된다"
      ]
    }
  },

  "status": "TODO",
  "priority": 2,
  "dependencies": ["BS-001"],
  "tags": ["notification", "user-experience"]
}
```

## Example 2: Test Case (P2, Major)

```json
{
  "code": "TC-001",
  "grade": "P2",
  "gradeDescription": "Major",
  "itemName": "로그인 기능 테스트",
  "scenario": "사용자 로그인 기능의 정상/비정상 케이스를 검증합니다. 올바른 인증 정보 입력 시 로그인 성공, 잘못된 정보 입력 시 적절한 에러 처리를 확인합니다.",

  "persona": {
    "normalUser": {
      "expectedResult": "1. 올바른 계정으로 로그인 성공\n2. 잘못된 비밀번호 시 에러 메시지 표시",
      "acceptanceCriteria": [
        "올바른 이메일/비밀번호 입력 시 메인 페이지로 리다이렉트된다",
        "잘못된 비밀번호 입력 시 '비밀번호가 올바르지 않습니다' 메시지가 표시된다",
        "존재하지 않는 이메일 입력 시 '가입되지 않은 이메일입니다' 메시지가 표시된다"
      ]
    },
    "operationUser": {
      "expectedResult": "1. 로그인 시도 이력 기록\n2. 실패한 로그인 모니터링",
      "acceptanceCriteria": [
        "모든 로그인 시도가 감사 로그에 기록된다",
        "5회 연속 실패 시 계정이 잠기고 관리자에게 알림된다",
        "로그인 성공 시 세션 정보가 기록된다"
      ]
    }
  },

  "status": "TODO",
  "priority": 2,
  "relatedItems": ["BS-002"]
}
```

## Example 3: API Feature (P2, Major)

```json
{
  "code": "BS-003",
  "grade": "P2",
  "gradeDescription": "Major",
  "itemName": "REST API 표준화",
  "scenario": "모든 API 엔드포인트가 일관된 요청/응답 구조를 따르도록 표준화합니다. HTTP 메서드, 상태 코드, 에러 응답 포맷을 통일하여 API 사용성을 개선합니다.",

  "persona": {
    "normalUser": {
      "expectedResult": "1. 예측 가능한 API 동작\n2. 명확한 에러 메시지\n3. 일관된 응답 구조",
      "acceptanceCriteria": [
        "모든 성공 응답은 200-299 범위의 상태 코드를 반환한다",
        "모든 에러 응답은 {code, message, details} 구조를 따른다",
        "API 문서가 Swagger/OpenAPI 형식으로 제공된다"
      ]
    },
    "operationUser": {
      "expectedResult": "1. API 호출 모니터링\n2. 성능 메트릭 수집\n3. 에러율 추적",
      "acceptanceCriteria": [
        "모든 API 호출이 응답 시간과 함께 로깅된다",
        "엔드포인트별 에러율을 대시보드에서 확인할 수 있다",
        "응답 시간 95 percentile 메트릭을 확인할 수 있다"
      ]
    }
  }
}
```

## Example 4: Data Feature (P1, Critical)

```json
{
  "code": "BS-004",
  "grade": "P1",
  "gradeDescription": "Critical",
  "itemName": "데이터 백업 및 복구",
  "scenario": "정기적인 데이터 백업과 재해 복구 시스템을 구축하여 데이터 손실을 방지합니다. 자동 백업 스케줄링, 증분 백업, 복구 테스트를 포함합니다.",

  "persona": {
    "normalUser": {
      "expectedResult": "1. 데이터 안전성 보장\n2. 삭제된 데이터 복구 가능",
      "acceptanceCriteria": [
        "실수로 삭제한 데이터를 7일 이내 복구할 수 있다",
        "데이터 복구 시 일관성이 보장된다"
      ]
    },
    "operationUser": {
      "expectedResult": "1. 자동 백업 스케줄러\n2. 백업 상태 모니터링\n3. 원클릭 복구 기능",
      "acceptanceCriteria": [
        "매일 자동으로 전체 백업이 수행된다",
        "백업 성공/실패 상태를 대시보드에서 확인할 수 있다",
        "백업 데이터로부터 1시간 이내 복구 가능하다",
        "백업 데이터는 암호화되어 저장된다"
      ]
    }
  },

  "priority": 1,
  "tags": ["infrastructure", "data-safety", "compliance"]
}
```

## Example 5: Performance Feature (P3, Minor)

```json
{
  "code": "BS-005",
  "grade": "P3",
  "gradeDescription": "Minor",
  "itemName": "캐싱 전략 구현",
  "scenario": "자주 조회되는 데이터를 캐싱하여 응답 속도를 개선하고 데이터베이스 부하를 감소시킵니다. Redis를 활용한 분산 캐시를 구현합니다.",

  "persona": {
    "normalUser": {
      "expectedResult": "1. 빠른 페이지 로딩\n2. 부드러운 사용 경험",
      "acceptanceCriteria": [
        "자주 조회되는 페이지의 로딩 시간이 50% 이상 개선된다",
        "캐시 적용 후 페이지 로딩이 1초 이내로 완료된다"
      ]
    },
    "operationUser": {
      "expectedResult": "1. 캐시 히트율 모니터링\n2. 캐시 무효화 제어\n3. 메모리 사용량 추적",
      "acceptanceCriteria": [
        "캐시 히트율을 대시보드에서 확인할 수 있다",
        "특정 키의 캐시를 수동으로 무효화할 수 있다",
        "캐시 메모리 사용량이 80%를 초과하면 알림이 발송된다"
      ]
    }
  },

  "priority": 3,
  "estimatedEffort": "3d",
  "tags": ["performance", "optimization"]
}
```
