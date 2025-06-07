import boto3
import time
from datetime import datetime

def upload_video_to_kinesis():
    # Initialize clients
    kinesis_client = boto3.client('kinesisvideo', region_name='ap-southeast-2')
    
    # Get data endpoint
    endpoint = kinesis_client.get_data_endpoint(
        StreamName='FireDetectionStream',
        APIName='PUT_MEDIA'
    )['DataEndpoint']
    
    # Initialize media client with endpoint
    media_client = boto3.client('kinesis-video-media', endpoint_url=endpoint)
    
    # Open video file
    with open('fire.mkv', 'rb') as video_file:
        # Start putting media
        response = media_client.put_media(
            StreamName='FireDetectionStream',
            ContentType='video/x-matroska',
            Payload=video_file
        )
        
        # Process the response stream
        for event in response['Payload']:
            if 'AckEvent' in event:
                print(f"Acknowledgment: {event['AckEvent']}")
            elif 'ErrorEvent' in event:
                print(f"Error: {event['ErrorEvent']}")
    
    print("Video upload completed")

if __name__ == "__main__":
    upload_video_to_kinesis()
