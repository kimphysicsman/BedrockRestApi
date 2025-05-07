# GitHub 저장소 설정 가이드

이 가이드는 GitHub 저장소를 설정하고 AWS Lambda에 자동 배포하기 위한 단계를 설명합니다.

## 1. GitHub 저장소 생성

1. GitHub에 로그인하고 새 저장소를 생성합니다.
2. 로컬 프로젝트를 저장소에 연결합니다:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/사용자명/저장소명.git
git push -u origin main
```

## 2. GitHub Secrets 설정

GitHub Actions가 AWS 리소스에 접근하려면 다음 비밀 값들을 설정해야 합니다:

1. GitHub 저장소 페이지에서 **Settings** > **Secrets and variables** > **Actions**로 이동합니다.
2. **New repository secret** 버튼을 클릭하고 다음 비밀 값들을 추가합니다:

   - `AWS_ACCESS_KEY_ID`: AWS IAM 사용자의 액세스 키 ID
   - `AWS_SECRET_ACCESS_KEY`: AWS IAM 사용자의 비밀 액세스 키
   - `AWS_REGION`: Lambda 함수가 위치한 AWS 리전 (예: `ap-northeast-2`)
   - `LAMBDA_FUNCTION_NAME`: 배포할 Lambda 함수 이름
   - `BEDROCK_FLOW_ID`: 사용할 Amazon Bedrock Flow의 ID

## 3. IAM 권한 설정

GitHub Actions가 사용하는 IAM 사용자에게 다음 권한이 필요합니다:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration"
            ],
            "Resource": "arn:aws:lambda:*:*:function:YOUR_LAMBDA_FUNCTION_NAME"
        }
    ]
}
```

## 4. 자동 배포 확인

설정이 완료되면:

1. 코드를 수정하고 `main` 브랜치에 푸시합니다.
2. GitHub 저장소의 **Actions** 탭에서 워크플로우 실행 상태를 확인합니다.
3. 워크플로우가 성공적으로 완료되면 AWS Lambda 콘솔에서 함수가 업데이트되었는지 확인합니다.