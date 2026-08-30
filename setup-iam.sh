#!/bin/bash
# Setup IAM roles for ECS Fargate deployment

set -e

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${1:-us-east-1}

echo "Creating IAM roles for ECS Fargate..."

# Create task execution role
cat > /tmp/task-execution-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file:///tmp/task-execution-trust.json \
  --region $REGION || true

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
  --region $REGION

# Create task role (for application permissions)
cat > /tmp/task-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document file:///tmp/task-trust.json \
  --region $REGION || true

# Create policy for ECR, CloudWatch, etc.
cat > /tmp/task-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:CreateLogGroup"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name ecsTaskRole \
  --policy-name ECSTaskPermissions \
  --policy-document file:///tmp/task-policy.json \
  --region $REGION

echo "IAM roles created:"
echo "  - ecsTaskExecutionRole (for pulling images, logging)"
echo "  - ecsTaskRole (for application runtime permissions)"
echo ""
echo "Update task-def-*.json with your account ID:"
echo "  ACCOUNT_ID = $ACCOUNT_ID"
echo "  REGION = $REGION"