FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY models/ models/

# AWS credentials should be passed as environment variables at runtime
ENV AWS_DEFAULT_REGION="ap-southeast-1"

# Run the application
CMD ["python", "models/FireDetection.py"]
