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

# Set AWS credentials (should be passed as environment variables)
ENV AWS_ACCESS_KEY_ID="AKIA3F4BYIJ2MAPHOD5A"
ENV AWS_SECRET_ACCESS_KEY="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"
ENV AWS_DEFAULT_REGION="ap-southeast-2"

# Run the application
CMD ["python", "models/FireDetection.py"]
