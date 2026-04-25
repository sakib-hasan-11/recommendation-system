#!/bin/bash
set -e

AWS_REGION=${AWS_REGION:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Registering AWS Batch job definitions..."

# Register ingestion job
aws batch register-job-definition \
  --cli-input-json file://infra/aws_batch/ingestion_job.json \
  --region ${AWS_REGION}

# Register training job
aws batch register-job-definition \
  --cli-input-json file://infra/aws_batch/training_job.json \
  --region ${AWS_REGION}

# Register feature materialization job
aws batch register-job-definition \
  --cli-input-json file://infra/aws_batch/feature_materialization_job.json \
  --region ${AWS_REGION}

echo "Job definitions registered successfully!"
