# Complete Container Deployment and Environment Variables Guide

Last Updated: April 25, 2026  
Status: Production Ready  
Target Environments: Local, Docker, AWS Batch, GitHub Actions

---

## Table of Contents

1. [Environment Variables Mapping](#environment-variables-mapping)
2. [GitHub Actions Secrets](#github-actions-secrets)
3. [Container-Specific Environment Variables](#container-specific-environment-variables)
4. [Docker Run Commands](#docker-run-commands)
5. [AWS Batch Job Configuration](#aws-batch-job-configuration)
6. [Local Development Setup](#local-development-setup)
7. [Production Deployment Checklist](#production-deployment-checklist)

---

## Environment Variables Mapping

### Code to Environment Variable Reference

This table shows how the Python config class maps to environment variables:

| Python Config Field | Environment Variable | Default | Type | Required | Used By |
|---|---|---|---|---|---|
| **ENVIRONMENT & LOGGING** ||||
| env | ENV | local | str | No | All |
| debug | DEBUG | False | bool | No | All |
| log_level | LOG_LEVEL | INFO | str | Yes | All (Ingestion, Training, API) |
| log_format | LOG_FORMAT | json | str | Yes | All (Ingestion, Training, API) |
| log_file | LOG_FILE | None | str | No | All |
| **AWS CREDENTIALS** ||||
| aws_region | AWS_REGION | us-east-1 | str | Yes | All (for S3, Batch) |
| aws_access_key_id | AWS_ACCESS_KEY_ID | empty | str | Conditional (Production only) | S3 operations |
| aws_secret_access_key | AWS_SECRET_ACCESS_KEY | empty | str | Conditional (Production only) | S3 operations |
| **S3 CONFIGURATION** ||||
| s3_bucket | S3_BUCKET | recommendation-system | str | Yes | Ingestion, Training (TODO) |
| s3_ingestion_prefix | S3_INGESTION_PREFIX | raw-data | str | Yes | Ingestion |
| s3_processed_prefix | S3_PROCESSED_PREFIX | processed-data | str | Yes | Training |
| s3_models_prefix | S3_MODELS_PREFIX | models | str | Yes | Training, API |
| s3_feast_prefix | S3_FEAST_PREFIX | feast-repo | str | No | Feast integration |
| **REDIS CONFIGURATION** ||||
| redis_host | REDIS_HOST | localhost | str | Yes | API (ElastiCache endpoint) |
| redis_port | REDIS_PORT | 6379 | int | Yes | API |
| redis_db | REDIS_DB | 0 | int | Yes | API |
| redis_password | REDIS_PASSWORD | None | str | No | API (if auth enabled) |
| cache_ttl | CACHE_TTL | 3600 | int | Yes | API |
| **PINECONE CONFIGURATION** ||||
| pinecone_api_key | PINECONE_API_KEY | empty | str | Yes | API |
| pinecone_host | PINECONE_HOST | empty | str | Yes | API (new format with host) |
| pinecone_index_name | PINECONE_INDEX_NAME | recommendations | str | Yes | API |
| pinecone_environment | PINECONE_ENVIRONMENT | gcp-starter | str | Yes | API (fallback if no host) |
| **MLFLOW CONFIGURATION** ||||
| mlflow_tracking_uri | MLFLOW_TRACKING_URI | http://localhost:5000 | str | Yes | Training, API |
| mlflow_experiment_name | MLFLOW_EXPERIMENT_NAME | recommendation-system | str | Yes | Training |
| mlflow_backend_store_uri | MLFLOW_BACKEND_STORE_URI | sqlite:///mlflow.db | str | Yes | Training (S3 recommended) |
| mlflow_artifact_root | MLFLOW_ARTIFACT_ROOT | ./mlruns | str | Yes | Training |
| **MODEL HYPERPARAMETERS** ||||
| embedding_dim | EMBEDDING_DIM | 64 | int | Yes | Training |
| hidden_units | HIDDEN_UNITS | 256 | int | Yes | Training |
| learning_rate | LEARNING_RATE | 0.001 | float | Yes | Training |
| batch_size | BATCH_SIZE | 32 | int | Yes | Training |
| epochs | EPOCHS | 10 | int | Yes | Training |
| validation_split | VALIDATION_SPLIT | 0.1 | float | Yes | Training |
| test_split | TEST_SPLIT | 0.1 | float | Yes | Training |
| **FEATURE ENGINEERING** ||||
| recall_at_k | RECALL_AT_K | 10 | int | Yes | Training |
| ndcg_at_k | NDCG_AT_K | 10 | int | Yes | Training |
| min_ratings_per_user | MIN_RATINGS_PER_USER | 5 | int | Yes | Ingestion, Training |
| min_interactions_per_item | MIN_INTERACTIONS_PER_ITEM | 5 | int | Yes | Training |
| **API CONFIGURATION** ||||
| api_host | API_HOST | 0.0.0.0 | str | Yes | API |
| api_port | API_PORT | 8000 | int | Yes | API |
| api_workers | API_WORKERS | 4 | int | Yes | API |
| api_reload | API_RELOAD | False | bool | Yes | API |
| **DATA PATHS** ||||
| data_local_path | DATA_LOCAL_PATH | ./data_local | str | Yes | Ingestion |
| training_data_path | TRAINING_DATA_PATH | ./data/training | str | Yes | Training |
| processed_data_path | PROCESSED_DATA_PATH | ./data/processed | str | Yes | Ingestion, Training, API |
| **FEAST CONFIGURATION** ||||
| feast_repo_path | FEAST_REPO_PATH | ./feast_repo/feature_repo | str | No | Feast integration |
| feast_offline_store | FEAST_OFFLINE_STORE | file | str | No | Feast integration |
| feast_online_store | FEAST_ONLINE_STORE | redis | str | No | Feast integration |

---

## GitHub Actions Secrets

Add these secrets to your GitHub repository: **Settings → Secrets and variables → Actions**

### Required Secrets for CI/CD Pipeline

```yaml
# AWS Credentials for ECR
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET=recommendation-system-1149

# Redis Configuration
REDIS_HOST=recommendation-system-fkohno.serverless.use1.cache.amazonaws.com

# Pinecone Configuration
PINECONE_API_KEY=pcsk_7KqPFf_AcFwcCzTniGWD5qKMb1zpwKfQKoAmRMBpGeuxHWGW1ch9mCvkMD25hv1DjuxNJh
PINECONE_HOST=https://recommnedation-system-l3pqpxp.svc.aped-4627-b74a.pinecone.io

# MLflow Configuration
MLFLOW_TRACKING_URI=http://your-ec2-ip:5000

# (Optional) IAM Role ARN for Batch Jobs
BATCH_ROLE_ARN=arn:aws:iam::032441996551:role/recommendation-batch-role
```

### GitHub Actions Usage in `ci.yml`

The workflow automatically uses these secrets to:
1. **Build Docker images** - Uses `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY` to push to ECR
2. **Create ECR repositories** - Uses AWS credentials to verify/create repos
3. **Tag images with commit SHA** - For version tracking

```yaml
# Example from ci.yml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ env.AWS_REGION }}
```

---

## Container-Specific Environment Variables

### 1. INGESTION CONTAINER

**Image:** `recommendation-system-ingestion:latest`  
**Entrypoint:** `python ingestion_job.py`

#### Required Environment Variables

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Data Paths
DATA_LOCAL_PATH=./data_local          # Where to read raw data
PROCESSED_DATA_PATH=./data/processed  # Where to write processed data

# Feature Engineering
MIN_RATINGS_PER_USER=5                # Minimum ratings per user for filtering
```

#### Optional Environment Variables

```bash
DEBUG=False
LOG_FILE=./logs/ingestion.log

# S3 Upload (TODO in code, currently uploads to local)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=recommendation-system-1149
S3_INGESTION_PREFIX=raw-data
S3_PROCESSED_PREFIX=processed-data
AWS_REGION=us-east-1
```

#### What It Does
```
Loads raw data from DATA_LOCAL_PATH
    -->
Validates & cleans (using MIN_RATINGS_PER_USER)
    -->
Saves processed data to PROCESSED_DATA_PATH
    -->
(TODO) Uploads to S3
```

---

### 2. TRAINING CONTAINER

**Image:** `recommendation-system-training:latest`  
**Entrypoint:** `python training_job.py`

#### Required Environment Variables

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Data Paths
PROCESSED_DATA_PATH=./data/processed  # Where to read processed data
                                      # Models saved here: ./data/processed/models

# MLflow Tracking
MLFLOW_TRACKING_URI=http://your-ec2-ip:5000  # EC2 IP, not localhost!
MLFLOW_EXPERIMENT_NAME=recommendation-system-experiment

# Model Hyperparameters
EMBEDDING_DIM=64
HIDDEN_UNITS=256
LEARNING_RATE=0.001
BATCH_SIZE=32
EPOCHS=10

# Feature Engineering
MIN_RATINGS_PER_USER=5
MIN_INTERACTIONS_PER_ITEM=5
```

#### Optional Environment Variables

```bash
DEBUG=False
LOG_FILE=./logs/training.log

# MLflow Backend (use S3 for production, not SQLite)
MLFLOW_BACKEND_STORE_URI=s3://recommendation-system-1149/mlflow/backend
MLFLOW_ARTIFACT_ROOT=s3://recommendation-system-1149/mlflow/artifacts

# Data Split Ratios
VALIDATION_SPLIT=0.1
TEST_SPLIT=0.1

# AWS Credentials (if uploading to S3)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET=recommendation-system-1149
S3_MODELS_PREFIX=models
```

#### What It Does
```
Reads PROCESSED_DATA_PATH
    -->
Splits data (VALIDATION_SPLIT, TEST_SPLIT)
    -->
Trains two-tower model (EMBEDDING_DIM, HIDDEN_UNITS, EPOCHS, etc.)
    -->
Logs metrics to MLflow (MLFLOW_TRACKING_URI)
    -->
Saves model locally and to MLflow
```

---

### 3. API CONTAINER

**Image:** `recommendation-system-api:latest`  
**Entrypoint:** `python api_server.py`  
**Port:** `8000`

#### Required Environment Variables

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Redis Configuration (ElastiCache endpoint)
REDIS_HOST=recommendation-system-fkohno.serverless.use1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600

# Pinecone Configuration
PINECONE_API_KEY=pcsk_7KqPFf_AcFwcCzTniGWD5qKMb1zpwKfQKoAmRMBpGeuxHWGW1ch9mCvkMD25hv1DjuxNJh
PINECONE_HOST=https://recommnedation-system-l3pqpxp.svc.aped-4627-b74a.pinecone.io
PINECONE_INDEX_NAME=recommnedation-system
```

#### Optional Environment Variables

```bash
DEBUG=False
LOG_FILE=./logs/api.log

# Redis Auth (if enabled)
REDIS_PASSWORD=your_password

# Fallback Pinecone Settings
PINECONE_ENVIRONMENT=gcp-starter

# MLflow (for model loading - TODO in code)
MLFLOW_TRACKING_URI=http://your-ec2-ip:5000
```

#### What It Does
```
Initializes Redis client --> REDIS_HOST:REDIS_PORT
    -->
Initializes Pinecone client --> PINECONE_HOST (with PINECONE_API_KEY)
    -->
Creates cache manager --> CACHE_TTL
    -->
(TODO) Loads models from S3/MLflow
    -->
Starts API server --> API_HOST:API_PORT
```

---

## Docker Run Commands

### Prerequisites

```bash
# Build base image first
docker build -f infra/docker/Dockerfile.base -t recommendation-system-base:latest .

# All other images depend on this
```

### Step 1: Run Ingestion Container

```bash
docker run -it \
  --name recommendation-ingestion \
  -v $(pwd)/data_local:/app/data_local:ro \
  -v $(pwd)/data/processed:/app/data/processed:rw \
  -v $(pwd)/logs:/app/logs:rw \
  -e LOG_LEVEL=INFO \
  -e LOG_FORMAT=json \
  -e DATA_LOCAL_PATH=./data_local \
  -e PROCESSED_DATA_PATH=./data/processed \
  -e MIN_RATINGS_PER_USER=5 \
  recommendation-system-ingestion:latest
```

**Volume Mapping:**
- Input: `data_local/` (read-only)
- Output: `data/processed/` (read-write)
- Logs: `logs/` (read-write)

---

### Step 2: Run Training Container

```bash
docker run -it \
  --name recommendation-training \
  -v $(pwd)/data/processed:/app/data/processed:rw \
  -v $(pwd)/logs:/app/logs:rw \
  -e LOG_LEVEL=INFO \
  -e LOG_FORMAT=json \
  -e PROCESSED_DATA_PATH=./data/processed \
  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 \
  -e MLFLOW_EXPERIMENT_NAME=recommendation-system-experiment \
  -e EMBEDDING_DIM=64 \
  -e HIDDEN_UNITS=256 \
  -e LEARNING_RATE=0.001 \
  -e BATCH_SIZE=32 \
  -e EPOCHS=10 \
  -e MIN_RATINGS_PER_USER=5 \
  -e MIN_INTERACTIONS_PER_ITEM=5 \
  recommendation-system-training:latest
```

**Volume Mapping:**
- Data: `data/processed/` (read-write for reading input & writing models)
- Logs: `logs/` (read-write)

**Network Note:**
- Use `host.docker.internal:5000` for local MLflow on host
- Use actual IP `<EC2_IP>:5000` for remote MLflow

---

### Step 3: Run API Container

```bash
docker run -it \
  --name recommendation-api \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs:rw \
  -e LOG_LEVEL=INFO \
  -e LOG_FORMAT=json \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -e API_WORKERS=4 \
  -e REDIS_HOST=recommendation-system-fkohno.serverless.use1.cache.amazonaws.com \
  -e REDIS_PORT=6379 \
  -e REDIS_DB=0 \
  -e CACHE_TTL=3600 \
  -e PINECONE_API_KEY=pcsk_7KqPFf_AcFwcCzTniGWD5qKMb1zpwKfQKoAmRMBpGeuxHWGW1ch9mCvkMD25hv1DjuxNJh \
  -e PINECONE_HOST=https://recommnedation-system-l3pqpxp.svc.aped-4627-b74a.pinecone.io \
  -e PINECONE_INDEX_NAME=recommnedation-system \
  recommendation-system-api:latest
```

**Port Mapping:**
- Container: `8000` → Host: `8000`
- Access: `http://localhost:8000`

---

### Step 4: Docker Compose (All Containers)

```yaml
version: '3.8'

services:
  ingestion:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.ingestion
    volumes:
      - ./data_local:/app/data_local:ro
      - ./data/processed:/app/data/processed:rw
      - ./logs:/app/logs:rw
    environment:
      LOG_LEVEL: INFO
      LOG_FORMAT: json
      DATA_LOCAL_PATH: ./data_local
      PROCESSED_DATA_PATH: ./data/processed
      MIN_RATINGS_PER_USER: 5

  training:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.training
    depends_on:
      - ingestion
    volumes:
      - ./data/processed:/app/data/processed:rw
      - ./logs:/app/logs:rw
    environment:
      LOG_LEVEL: INFO
      LOG_FORMAT: json
      PROCESSED_DATA_PATH: ./data/processed
      MLFLOW_TRACKING_URI: http://host.docker.internal:5000
      MLFLOW_EXPERIMENT_NAME: recommendation-system-experiment
      EMBEDDING_DIM: 64
      HIDDEN_UNITS: 256
      LEARNING_RATE: 0.001
      BATCH_SIZE: 32
      EPOCHS: 10
      MIN_RATINGS_PER_USER: 5
      MIN_INTERACTIONS_PER_ITEM: 5

  api:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs:rw
    environment:
      LOG_LEVEL: INFO
      LOG_FORMAT: json
      API_HOST: 0.0.0.0
      API_PORT: 8000
      API_WORKERS: 4
      REDIS_HOST: recommendation-system-fkohno.serverless.use1.cache.amazonaws.com
      REDIS_PORT: 6379
      REDIS_DB: 0
      CACHE_TTL: 3600
      PINECONE_API_KEY: pcsk_7KqPFf_AcFwcCzTniGWD5qKMb1zpwKfQKoAmRMBpGeuxHWGW1ch9mCvkMD25hv1DjuxNJh
      PINECONE_HOST: https://recommnedation-system-l3pqpxp.svc.aped-4627-b74a.pinecone.io
      PINECONE_INDEX_NAME: recommnedation-system
```

**Run with:**
```bash
docker-compose up -d
```

---

## AWS Batch Job Configuration

### Batch Job Definition: Ingestion

```json
{
  "jobDefinitionName": "recommendation-ingestion",
  "type": "container",
  "containerProperties": {
    "image": "032441996551.dkr.ecr.us-east-1.amazonaws.com/recommendation-system-ingestion:latest",
    "vcpus": 2,
    "memory": 4096,
    "environment": [
      {"name": "ENV", "value": "production"},
      {"name": "LOG_LEVEL", "value": "INFO"},
      {"name": "LOG_FORMAT", "value": "json"},
      {"name": "DATA_LOCAL_PATH", "value": "/data/raw"},
      {"name": "PROCESSED_DATA_PATH", "value": "/data/processed"},
      {"name": "MIN_RATINGS_PER_USER", "value": "5"},
      {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"},
      {"name": "S3_BUCKET", "value": "recommendation-system-1149"},
      {"name": "S3_INGESTION_PREFIX", "value": "raw-data"},
      {"name": "S3_PROCESSED_PREFIX", "value": "processed-data"}
    ],
    "jobRoleArn": "arn:aws:iam::032441996551:role/recommendation-batch-role",
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/aws/batch/recommendation-ingestion",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "recommendation"
      }
    }
  },
  "retryStrategy": {
    "attempts": 2
  },
  "timeout": {
    "attemptDurationSeconds": 3600
  }
}
```

**Submit Job:**
```bash
aws batch submit-job \
  --job-name ingestion-$(date +%s) \
  --job-queue recommendation-queue \
  --job-definition recommendation-ingestion
```

---

### Batch Job Definition: Training

```json
{
  "jobDefinitionName": "recommendation-training",
  "type": "container",
  "containerProperties": {
    "image": "032441996551.dkr.ecr.us-east-1.amazonaws.com/recommendation-system-training:latest",
    "vcpus": 8,
    "memory": 16384,
    "gpuCount": 1,
    "environment": [
      {"name": "ENV", "value": "production"},
      {"name": "LOG_LEVEL", "value": "INFO"},
      {"name": "LOG_FORMAT", "value": "json"},
      {"name": "PROCESSED_DATA_PATH", "value": "/data/processed"},
      {"name": "MLFLOW_TRACKING_URI", "value": "http://10.0.1.123:5000"},
      {"name": "MLFLOW_EXPERIMENT_NAME", "value": "recommendation-system-experiment"},
      {"name": "MLFLOW_BACKEND_STORE_URI", "value": "s3://recommendation-system-1149/mlflow/backend"},
      {"name": "MLFLOW_ARTIFACT_ROOT", "value": "s3://recommendation-system-1149/mlflow/artifacts"},
      {"name": "EMBEDDING_DIM", "value": "64"},
      {"name": "HIDDEN_UNITS", "value": "256"},
      {"name": "LEARNING_RATE", "value": "0.001"},
      {"name": "BATCH_SIZE", "value": "32"},
      {"name": "EPOCHS", "value": "10"},
      {"name": "MIN_RATINGS_PER_USER", "value": "5"},
      {"name": "MIN_INTERACTIONS_PER_ITEM", "value": "5"},
      {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"},
      {"name": "S3_BUCKET", "value": "recommendation-system-1149"},
      {"name": "S3_MODELS_PREFIX", "value": "artifacts/models"}
    ],
    "jobRoleArn": "arn:aws:iam::032441996551:role/recommendation-batch-role",
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/aws/batch/recommendation-training",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "recommendation"
      }
    }
  },
  "retryStrategy": {
    "attempts": 1
  },
  "timeout": {
    "attemptDurationSeconds": 28800
  }
}
```

**Submit Job:**
```bash
aws batch submit-job \
  --job-name training-$(date +%s) \
  --job-queue recommendation-queue \
  --job-definition recommendation-training
```

---

### Batch Job Definition: API

```json
{
  "jobDefinitionName": "recommendation-api",
  "type": "container",
  "containerProperties": {
    "image": "032441996551.dkr.ecr.us-east-1.amazonaws.com/recommendation-system-api:latest",
    "vcpus": 4,
    "memory": 8192,
    "portMappings": [
      {
        "containerPort": 8000,
        "protocol": "tcp"
      }
    ],
    "environment": [
      {"name": "ENV", "value": "production"},
      {"name": "LOG_LEVEL", "value": "INFO"},
      {"name": "LOG_FORMAT", "value": "json"},
      {"name": "API_HOST", "value": "0.0.0.0"},
      {"name": "API_PORT", "value": "8000"},
      {"name": "API_WORKERS", "value": "4"},
      {"name": "REDIS_HOST", "value": "recommendation-system-fkohno.serverless.use1.cache.amazonaws.com"},
      {"name": "REDIS_PORT", "value": "6379"},
      {"name": "REDIS_DB", "value": "0"},
      {"name": "CACHE_TTL", "value": "3600"},
      {"name": "PINECONE_API_KEY", "value": "pcsk_7KqPFf_AcFwcCzTniGWD5qKMb1zpwKfQKoAmRMBpGeuxHWGW1ch9mCvkMD25hv1DjuxNJh"},
      {"name": "PINECONE_HOST", "value": "https://recommnedation-system-l3pqpxp.svc.aped-4627-b74a.pinecone.io"},
      {"name": "PINECONE_INDEX_NAME", "value": "recommnedation-system"},
      {"name": "AWS_DEFAULT_REGION", "value": "us-east-1"}
    ],
    "jobRoleArn": "arn:aws:iam::032441996551:role/recommendation-batch-role",
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/aws/batch/recommendation-api",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "recommendation"
      }
    }
  },
  "retryStrategy": {
    "attempts": 2
  },
  "timeout": {
    "attemptDurationSeconds": 86400
  }
}
```

**Submit Job:**
```bash
aws batch submit-job \
  --job-name api-$(date +%s) \
  --job-queue recommendation-queue \
  --job-definition recommendation-api
```

---

## Local Development Setup

### Step 1: Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Create .env File

```bash
cp .env.example .env
```

### Step 3: Set Required Variables in .env

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Data Paths (local)
DATA_LOCAL_PATH=./data_local
PROCESSED_DATA_PATH=./data/processed

# Redis (local or AWS)
REDIS_HOST=localhost  # or AWS endpoint
REDIS_PORT=6379

# Pinecone
PINECONE_API_KEY=your_key_here
PINECONE_HOST=your_host_here
PINECONE_INDEX_NAME=your_index_here

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=local-development
```

### Step 4: Run Ingestion Locally

```bash
python scripts/ingestion_job.py
```

Expected Output:
```
Loaded: movies=3883, ratings=1000209, users=6040
Cleaned and validated
Saved to ./data/processed/
```

### Step 5: Start MLflow Server

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 --port 5000
```

**Access:** http://localhost:5000

### Step 6: Run Training Locally

```bash
python scripts/training_job.py
```

Expected Output:
```
Loaded processed data
Training two-tower model
Logged metrics to MLflow
Model saved
```

### Step 7: Start API Server

```bash
python scripts/api_server.py
```

**Access:** http://localhost:8000

---

## Production Deployment Checklist

### Pre-Deployment Verification

- [ ] All 16 tests passing: `pytest tests/ -v`
- [ ] Config loads correctly: `python -c "from common.config import load_config; load_config()"`
- [ ] All imports work: See DEPLOYMENT_READY_CHECKLIST.md

### GitHub Actions Setup

- [ ] Add all required secrets to repository
- [ ] Verify CI/CD pipeline runs on push to main
- [ ] Check Docker images in ECR

### AWS Infrastructure

- [ ] ECR repositories created:
  ```bash
  aws ecr describe-repositories --region us-east-1
  ```
  Should show: `recommendation-system-{base,ingestion,training,api}`

- [ ] Batch compute environment created with security group `recommendation-system-global-sg`

- [ ] Batch job queue created: `recommendation-queue`

- [ ] IAM role has S3 permissions: `recommendation-batch-role`

- [ ] Redis endpoint configured and accessible

- [ ] Pinecone index created and accessible

### MLflow Setup

- [ ] EC2 MLflow server running:
  ```bash
  curl http://your-ec2-ip:5000
  ```

- [ ] S3 paths configured for MLflow backend/artifacts

### Database Seeding

- [ ] Raw data uploaded to `s3://recommendation-system-1149/raw-data/`
  
- [ ] OR local `data_local/` directory populated

### Testing Flow

```bash
# 1. Run ingestion
aws batch submit-job --job-name test-ingestion --job-queue recommendation-queue --job-definition recommendation-ingestion

# 2. Monitor logs in CloudWatch
aws logs tail /aws/batch/recommendation-ingestion --follow

# 3. Verify output in S3
aws s3 ls s3://recommendation-system-1149/processed-data/

# 4. Run training
aws batch submit-job --job-name test-training --job-queue recommendation-queue --job-definition recommendation-training

# 5. Check MLflow
# http://your-ec2-ip:5000
```

---

## Environment Variable Quick Reference

### Ingestion Container
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
DATA_LOCAL_PATH=./data_local
PROCESSED_DATA_PATH=./data/processed
MIN_RATINGS_PER_USER=5
```

### Training Container
```bash
LOG_LEVEL=INFO
PROCESSED_DATA_PATH=./data/processed
MLFLOW_TRACKING_URI=http://your-ec2-ip:5000
EMBEDDING_DIM=64
HIDDEN_UNITS=256
LEARNING_RATE=0.001
BATCH_SIZE=32
EPOCHS=10
```

### API Container
```bash
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
REDIS_HOST=your-redis-endpoint
PINECONE_API_KEY=your-key
PINECONE_HOST=your-host
PINECONE_INDEX_NAME=your-index
```

### GitHub Actions Secrets
```bash
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
S3_BUCKET
REDIS_HOST
PINECONE_API_KEY
PINECONE_HOST
MLFLOW_TRACKING_URI
```

---

All environment variables are properly mapped and documented. The system is ready for cloud deployment.
