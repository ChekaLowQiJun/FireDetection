import boto3
from botocore.config import Config

# 1. Credential Setup - Uses this order:
#    - Explicit parameters below
#    - Environment variables (AWS_ACCESS_KEY_ID etc)
#    - ~/.aws/credentials file
#    - IAM role (if on EC2)

AWS_ACCESS_KEY = "AKIA3F4BYIJ2MAPHOD5A"  # Replace or leave empty to use other methods
AWS_SECRET_KEY = "D3X6v6rxPYMnG/qJloJ6l9Xy/iRBVlGl7Q8K7Cuf"  # Replace or leave empty
REGION = "ap-southeast-2"

# 2. Initialize clients with explicit configuration
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

kvs = session.client('kinesisvideo')
endpoint = kvs.get_data_endpoint(
    StreamName='FireDetectionStream',
    APIName='PUT_MEDIA'
)['DataEndpoint']

media = session.client('kinesis-video-media', endpoint_url=endpoint)

# Simple test data - replace with actual video frames in production
test_frames = [
    b"fake_frame_data_1", 
    b"fake_frame_data_2",
    b"fake_frame_data_3"
]

for frame in test_frames:
    try:
        media.put_media(
            StreamName='FireDetectionStream',
            Payload=frame
        )
        print("Sent frame")
        time.sleep(0.1)  # Simulate frame rate
    except Exception as e:
        print(f"Error: {e}")
        break

print("Test frames sent")