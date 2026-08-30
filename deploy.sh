#!/bin/bash
# Simple ECS Deployment Script for t3.micro (Fargate)
# Usage: ./deploy.sh <aws-region> <ecr-repo-prefix>

set -e

AWS_REGION=${1:-us-east-1}
ECR_PREFIX=${2:-theme-analyser}
CLUSTER_NAME="theme-analyser-cluster"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "=== Deploying to AWS ECS (Fargate) ==="
echo "Region: $AWS_REGION"
echo "Account: $ACCOUNT_ID"
echo "ECR Prefix: $ECR_PREFIX"

# Create ECR repositories
echo "Creating ECR repositories..."
aws ecr create-repository --repository-name ${ECR_PREFIX}-fastapi --region $AWS_REGION || true
aws ecr create-repository --repository-name ${ECR_PREFIX}-springboot --region $AWS_REGION || true
aws ecr create-repository --repository-name ${ECR_PREFIX}-react --region $AWS_REGION || true

# Get login token
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build and push FastAPI
echo "Building FastAPI..."
cd app
docker build -t ${ECR_PREFIX}-fastapi .
docker tag ${ECR_PREFIX}-fastapi:latest ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_PREFIX}-fastapi:latest
docker push ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_PREFIX}-fastapi:latest
cd ..

# Build and push Spring Boot
echo "Building Spring Boot..."
cd backend
docker build -t ${ECR_PREFIX}-springboot .
docker tag ${ECR_PREFIX}-springboot:latest ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_PREFIX}-springboot:latest
docker push ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_PREFIX}-springboot:latest
cd ..

# Build and push React
echo "Building React..."
cd frontend
docker build -t ${ECR_PREFIX}-react .
docker tag ${ECR_PREFIX}-react:latest ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_PREFIX}-react:latest
docker push ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_PREFIX}-react:latest
cd ..

# Create ECS cluster
echo "Creating ECS cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION || true

# Register task definitions
echo "Registering task definitions..."
aws ecs register-task-definition --cli-input-json file://task-def-fastapi.json --region $AWS_REGION
aws ecs register-task-definition --cli-input-json file://task-def-springboot.json --region $AWS_REGION
aws ecs register-task-definition --cli-input-json file://task-def-react.json --region $AWS_REGION

# Create services
echo "Creating ECS services..."
aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name fastapi-service \
  --task-definition ${ECR_PREFIX}-fastapi \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region $AWS_REGION || true

aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name springboot-service \
  --task-definition ${ECR_PREFIX}-springboot \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region $AWS_REGION || true

aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name react-service \
  --task-definition ${ECR_PREFIX}-react \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region $AWS_REGION || true

echo "=== Deployment Complete ==="
echo "Update the subnet-xxx and sg-xxx in the script with your actual VPC subnet and security group IDs"