import boto3
from ultralytics import YOLO
import cv2
import os
import tempfile

# Initialize AWS clients
kinesis = boto3.client('kinesisvideo')
s3 = boto3.client('s3')

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

# Process stream
with tempfile.TemporaryDirectory() as tmpdir:
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
        
        # Save results to S3
        for result in results:
            output_path = f"predictions/{result.path.split('/')[-1]}"
            s3.upload_file(result.path, 'firedetectionveq', output_path)
    
