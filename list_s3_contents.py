import boto3
import os

def test_s3_connection():
    try:
        s3 = boto3.client('s3',
                         region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1'))
        
        # Try listing all buckets to test connectivity
        response = s3.list_buckets()
        print("Successfully connected to AWS S3")
        print("Available buckets:")
        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")
            
        # Check specific bucket
        target_bucket = 'firedetectionbuckets'
        print(f"\nChecking bucket '{target_bucket}'...")
        try:
            s3.head_bucket(Bucket=target_bucket)
            print("Bucket exists and is accessible")
        except Exception as e:
            print(f"Error accessing bucket: {e}")
            
    except Exception as e:
        print(f"Failed to connect to AWS S3: {e}")

if __name__ == '__main__':
    test_s3_connection()
