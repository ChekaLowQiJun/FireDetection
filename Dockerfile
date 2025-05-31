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
COPY demo/raw_videos/fire.mp4 demo/raw_videos/

# Set AWS credentials (should be passed as environment variables)
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_DEFAULT_REGION="ap-southeast-1"

# Run the application
CMD ["python", "models/FireDetection.py"]
