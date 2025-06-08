from ultralytics import YOLO
import os
import tempfile
import boto3
import time
import json
from botocore.exceptions import ClientError

def get_aws_client(service_name):
    """Initialize AWS client with proper credentials and error handling"""
    try:
        return boto3.client(service_name,
                          region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1'))
    except Exception as e:
        print(f"Error initializing AWS {service_name} client: {e}")
        raise

def ensure_stream_exists(kinesis_client, stream_name, region):
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

# Usage:
# Set YOLO config directory to writable location
yolo_config_dir = os.path.join(tempfile.gettempdir(), '.config/Ultralytics')
os.makedirs(yolo_config_dir, exist_ok=True)
os.environ['YOLO_CONFIG_DIR'] = yolo_config_dir

# Initialize AWS clients first
try:
    kinesis = get_aws_client('kinesisvideo')
    s3 = get_aws_client('s3')
except Exception as e:
    print(f"Failed to initialize AWS clients: {e}")
    exit(1)

# Initialize stream
ensure_stream_exists(kinesis, "veq-cam-2", os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1'))

# Get Kinesis video stream endpoint
response = kinesis.get_data_endpoint(
    StreamName='veq-cam-2',
    APIName='GET_MEDIA'
)
endpoint = response['DataEndpoint']

# Initialize media client
media = boto3.client('kinesis-video-media', endpoint_url=endpoint)

# Get media stream
stream = media.get_media(
    StreamName='veq-cam-2',
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
                StreamName='veq-cam-2',
                APIName='GET_MEDIA'
            )
            endpoint = response['DataEndpoint']
            media = boto3.client('kinesis-video-media', endpoint_url=endpoint)
            stream = media.get_media(
                StreamName='veq-cam-2',
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
                    
                # Run prediction and convert to JSON
                results = model.predict(frame_path, save=False, show=False)
                
                # Save JSON results to S3
                for result in results:
                    json_data = result.tojson()
                    timestamp = int(time.time())
                    output_path = f"predictions/json/{timestamp}.json"
                    s3.put_object(
                        Bucket='firedetectionbuckets',
                        Key=output_path,
                        Body=json_data,
                        ContentType='application/json'
                    )
                    
    except Exception as e:
        print(f"Error processing stream: {e}")
        time.sleep(5)  # Wait before retrying
