#!/bin/bash
set -e

AWS_REGION=${AWS_REGION:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_TAG="recommendation-system:latest"
REPOSITORY_NAME="recommendation-system"

echo "Building Docker images..."

# Build base image
docker build -f infra/docker/Dockerfile.base -t "${IMAGE_TAG}" .

# Tag for ECR
docker tag "${IMAGE_TAG}" "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}:latest"

# Create ECR repository if not exists
aws ecr describe-repositories --repository-names ${REPOSITORY_NAME} --region ${AWS_REGION} || \
  aws ecr create-repository --repository-name ${REPOSITORY_NAME} --region ${AWS_REGION}

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Push to ECR
docker push "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}:latest"

echo "Deployment images pushed successfully!"
