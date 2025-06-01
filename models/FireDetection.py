import boto3
from ultralytics import YOLO
import cv2
import os
import tempfile
import time
import json
from botocore.exceptions import ClientError

# Set YOLO config to use /tmp instead of /root
os.makedirs('/tmp/.config/Ultralytics', exist_ok=True)
os.environ['YOLO_CONFIG_DIR'] = '/tmp/.config/Ultralytics'

def ensure_stream_exists(kinesis_client, stream_name, region):
    """Ensure Kinesis video stream exists with proper credentials"""
    try:
        # Check if stream exists
        kinesis_client.describe_stream(StreamName=stream_name)
        print(f"Stream {stream_name} exists")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Creating stream {stream_name}")
            kinesis_client.create_stream(
                StreamName=stream_name,
                DataRetentionInHours=24
            )
            # Wait for stream to become active
            while True:
                try:
                    desc = kinesis_client.describe_stream(StreamName=stream_name)
                    if desc['StreamInfo']['Status'] == 'ACTIVE':
                        break
                    time.sleep(5)
                except ClientError:
                    time.sleep(5)
        else:
            raise

def check_aws_credentials():
    """Check for AWS credentials in standard locations"""
    # Check environment variables
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("Using AWS credentials from environment variables")
        return True
    
    # Check for credentials file
    if os.path.exists(os.path.expanduser('~/.aws/credentials')):
        print("Using AWS credentials from ~/.aws/credentials")
        return True
    
    # Check if running on EC2 with IAM role
    try:
        boto3.client('sts').get_caller_identity()
        print("Using AWS credentials from IAM role")
        return True
    except:
        pass
    
    return False

# Check credentials before proceeding
if not check_aws_credentials():
    print("ERROR: No AWS credentials found")
    print("Please configure credentials using one of these methods:")
    print("1. Environment variables:")
    print("   export AWS_ACCESS_KEY_ID='your_access_key'")
    print("   export AWS_SECRET_ACCESS_KEY='your_secret_key'")
    print("   export AWS_DEFAULT_REGION='ap-southeast-2'")
    print("\n2. ~/.aws/credentials file:")
    print("   [default]")
    print("   aws_access_key_id = your_access_key")
    print("   aws_secret_access_key = your_secret_key")
    print("   region = ap-southeast-2")
    print("\n3. IAM role if running on AWS EC2")
    exit(1)

# Initialize AWS clients
try:
    kinesis = boto3.client('kinesisvideo',
                          region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-2'))
    s3 = boto3.client('s3',
                     region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-2'))
    
    # Initialize stream
    ensure_stream_exists(kinesis, "FireDetectionStream", os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-2'))
except Exception as e:
    print(f"AWS initialization failed: {e}")
    exit(1)

# Get Kinesis video stream endpoint
response = kinesis.get_data_endpoint(
    StreamName='FireDetectionStream',
    APIName='GET_MEDIA'
)
endpoint = response['DataEndpoint']

# Initialize media client
media = boto3.client('kinesis-video-media', endpoint_url=endpoint)

# Get media stream
stream = media.get_media(
    StreamName='FireDetectionStream',
    StartSelector={'StartSelectorType': 'NOW'}
)

# Initialize YOLO model
model = YOLO("models/best (1).pt")

# Process stream continuously
while True:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Get fresh media stream
            response = kinesis.get_data_endpoint(
                StreamName='FireDetectionStream',
                APIName='GET_MEDIA'
            )
            endpoint = response['DataEndpoint']
            media = boto3.client('kinesis-video-media', endpoint_url=endpoint)
            stream = media.get_media(
                StreamName='FireDetectionStream',
                StartSelector={'StartSelectorType': 'NOW'}
            )
            
            while True:
                # Read frame from stream
                frame = stream['Payload'].read(1024*1024)
                if not frame:
                    break
                    
                # Save frame to temp file
                frame_path = os.path.join(tmpdir, 'frame.jpg')
                with open(frame_path, 'wb') as f:
                    f.write(frame)
                    
                # Run prediction
                results = model.predict(frame_path, save=False, show=False)
                
                # Save results to S3 as JSON
                for result in results:
                    # Convert results to JSON
                    json_data = result.tojson()
                    # Create temp JSON file
                    json_path = os.path.join(tmpdir, 'prediction.json')
                    with open(json_path, 'w') as f:
                        f.write(json_data)
                    # Upload to S3
                    output_path = f"predictions/{int(time.time())}.json"
                    s3.upload_file(json_path, 'firedetectionveq', output_path)
                    
    except Exception as e:
        print(f"Error processing stream: {e}")
        time.sleep(5)  # Wait before retrying
