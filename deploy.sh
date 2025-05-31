#!/bin/bash

# Build Docker image
docker build -t fire-detection .

# Run container with AWS credentials and configuration
docker run -d \
  -e AWS_ACCESS_KEY_ID="your-access-key" \
  -e AWS_SECRET_ACCESS_KEY="your-secret-key" \
  -e AWS_DEFAULT_REGION="ap-southeast-1" \
  fire-detection
