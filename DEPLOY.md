# Theme Analyser - AWS ECS Deployment Guide

## Architecture Overview

This is a 3-service microservices application:
- **FastAPI** (port 8000) - Python backend for document processing, OCR, vector search, Q&A
- **Spring Boot** (port 8080) - Java middleware for RAG pipeline, verification, evaluation
- **React** (port 3000) - Frontend UI

All services communicate internally. No API keys required (empty strings used).

## Local Testing (No AWS)

```bash
# Start all services locally
docker-compose -f docker-compose.local.yml up -d

# Test all endpoints
./test-endpoints.sh

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop
docker-compose -f docker-compose.local.yml down
```

## AWS ECS Deployment (Fargate on t3.micro equivalent)

### Prerequisites
- AWS CLI configured with credentials
- Docker installed
- VPC with public subnets and security group allowing ports 8000, 8080, 3000

### Quick Deploy

```bash
# Make scripts executable
chmod +x deploy.sh test-endpoints.sh

# Deploy to AWS (replace with your region and desired prefix)
./deploy.sh us-east-1 theme-analyser
```

**Important**: Before running, update these in `deploy.sh`:
- `subnet-xxx` → Your public subnet ID
- `sg-xxx` → Your security group ID

Also update task definition JSON files:
- `ACCOUNT_ID` → Your AWS account ID
- `REGION` → Your AWS region (e.g., us-east-1)

### Manual Steps (if script fails)

1. **Create ECR repos:**
   ```bash
   aws ecr create-repository --repository-name theme-analyser-fastapi --region us-east-1
   aws ecr create-repository --repository-name theme-analyser-springboot --region us-east-1
   aws ecr create-repository --repository-name theme-analyser-react --region us-east-1
   ```

2. **Build & Push:**
   ```bash
   # Get login
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   
   # FastAPI
   cd app && docker build -t theme-analyser-fastapi . && cd ..
   docker tag theme-analyser-fastapi:latest <account>.dkr.ecr.us-east-1.amazonaws.com/theme-analyser-fastapi:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/theme-analyser-fastapi:latest
   
   # Spring Boot
   cd backend && docker build -t theme-analyser-springboot . && cd ..
   docker tag theme-analyser-springboot:latest <account>.dkr.ecr.us-east-1.amazonaws.com/theme-analyser-springboot:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/theme-analyser-springboot:latest
   
   # React
   cd frontend && docker build -t theme-analyser-react . && cd ..
   docker tag theme-analyser-react:latest <account>.dkr.ecr.us-east-1.amazonaws.com/theme-analyser-react:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/theme-analyser-react:latest
   ```

3. **Create ECS Cluster:**
   ```bash
   aws ecs create-cluster --cluster-name theme-analyser-cluster --region us-east-1
   ```

4. **Register Task Definitions:**
   ```bash
   # Update task-def-*.json with your ACCOUNT_ID and REGION first
   aws ecs register-task-definition --cli-input-json file://task-def-fastapi.json --region us-east-1
   aws ecs register-task-definition --cli-input-json file://task-def-springboot.json --region us-east-1
   aws ecs register-task-definition --cli-input-json file://task-def-react.json --region us-east-1
   ```

5. **Create Services:**
   ```bash
   aws ecs create-service \
     --cluster theme-analyser-cluster \
     --service-name fastapi-service \
     --task-definition theme-analyser-fastapi \
     --desired-count 1 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
     --region us-east-1
   # Repeat for springboot-service and react-service
   ```

## Endpoints to Test

### FastAPI (port 8000)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get document |
| POST | `/api/v1/upload` | Upload document |
| GET | `/api/v1/search` | Semantic search |
| GET | `/api/v1/ask` | Q&A |
| POST | `/api/v1/evaluate/retrieval` | Retrieval eval |
| POST | `/api/v1/evaluate/generation` | Generation eval |
| POST | `/api/v1/test/setup` | Add test data |

### Spring Boot (port 8080)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root |
| GET | `/actuator/health` | Health check |
| GET | `/api/documents` | List documents |
| POST | `/api/upload` | Upload document |
| GET | `/api/search` | Search |
| GET | `/api/ask` | Ask question |
| GET | `/api/rag/ask` | RAG ask |
| GET | `/api/rag/search` | RAG search |
| POST | `/api/rag/evaluate/generation` | RAG generation eval |
| POST | `/api/verify` | Verify answer |
| POST | `/api/evaluate/retrieval` | Retrieval eval |
| POST | `/api/evaluate/generation` | Generation eval |
| GET | `/api/documents/{id}` | Get document |
| DELETE | `/api/documents/{id}` | Delete document |
| DELETE | `/api/clear-all` | Clear all |

### React (port 3000)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend app |

## Testing on AWS

After deployment, get the public IPs of each task:

```bash
# Get task ARNs
aws ecs list-tasks --cluster theme-analyser-cluster --service-name fastapi-service --region us-east-1

# Get task details (includes public IP)
aws ecs describe-tasks --cluster theme-analyser-cluster --tasks <task-arn> --region us-east-1
```

Then test:
```bash
FASTAPI_URL=http://<fastapi-public-ip>:8000 \
SPRINGBOOT_URL=http://<springboot-public-ip>:8080 \
REACT_URL=http://<react-public-ip>:3000 \
./test-endpoints.sh
```

## Cost Optimization for t3.micro

- Use Fargate Spot (50-70% cheaper)
- Set CPU/memory to minimum: FastAPI 256/512, Spring Boot 512/1024, React 256/512
- Use single AZ deployment
- Enable auto-scaling with min=0 for dev

## Troubleshooting

1. **Services not starting**: Check CloudWatch logs (`/ecs/theme-analyser-*`)
2. **Health checks failing**: Increase `startPeriod` in task definitions
3. **Spring Boot can't reach FastAPI**: Use service discovery names (`fastapi-service:8000`)
4. **Out of memory**: Increase memory in task definitions
5. **Database persistence**: Add EFS volume for SQLite data

## Cleanup

```bash
# Delete services
aws ecs delete-service --cluster theme-analyser-cluster --service fastapi-service --force --region us-east-1
aws ecs delete-service --cluster theme-analyser-cluster --service springboot-service --force --region us-east-1
aws ecs delete-service --cluster theme-analyser-cluster --service react-service --force --region us-east-1

# Delete cluster
aws ecs delete-cluster --cluster theme-analyser-cluster --region us-east-1

# Delete ECR repos
aws ecr delete-repository --repository-name theme-analyser-fastapi --force --region us-east-1
aws ecr delete-repository --repository-name theme-analyser-springboot --force --region us-east-1
aws ecr delete-repository --repository-name theme-analyser-react --force --region us-east-1
```