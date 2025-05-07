# Bedrock Flows REST API

이 프로젝트는 Amazon Bedrock Flows를 사용하여 채팅 기능을 제공하는 REST API를 구현합니다.

## 구조

- `qna_flows_rest_api.py`: Lambda 핸들러 함수
- `dispatch/bedrock_flows_router.py`: Bedrock Flows와 통신하는 라우터 클래스
- `dispatch/utils.py`: 유틸리티 함수
- `tests/`: 단위 테스트 디렉토리

## 설정

이 애플리케이션을 실행하기 위해서는 다음 환경 변수가 필요합니다:

- `BEDROCK_FLOW_ID`: 사용할 Amazon Bedrock Flow의 ID

## API 사용법

### 요청 형식

```json
{
  "sessionId": "사용자 세션 ID (선택 사항)",
  "message": "사용자 메시지",
  "metadata": {
    "filter": "문서 필터링을 위한 메타데이터 (선택 사항)"
  }
}
```

### 응답 형식

```json
{
  "sessionId": "세션 ID",
  "message": "Bedrock Flow의 응답 메시지",
  "citations": [
    {
      "url": "인용 URL",
      "title": "인용 제목"
    }
  ]
}
```

## 테스트

단위 테스트를 실행하려면:

```bash
python -m unittest discover tests
```

## 배포

AWS Lambda 함수로 배포하고 API Gateway와 연결하여 REST API로 노출할 수 있습니다.

## 라이선스

Amazon Software License (ASL)