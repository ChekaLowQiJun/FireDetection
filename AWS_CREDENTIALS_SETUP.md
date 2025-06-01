# AWS Credentials Setup for FireDetection

## Option 1: Environment Variables (Temporary)
Run these commands in your terminal before starting the script:
```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="ap-southeast-2"
```

## Option 2: AWS Credentials File (Recommended)
Create or edit `~/.aws/credentials` (Linux/Mac) or `%UserProfile%\.aws\credentials` (Windows):
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = ap-southeast-2
```

## Option 3: Docker Environment Variables
If running in Docker, add to your `Dockerfile`:
```dockerfile
ENV AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
ENV AWS_DEFAULT_REGION=ap-southeast-2
```

## Option 4: .env File (For Development)
Create a `.env` file in your project root:
```bash
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
AWS_DEFAULT_REGION=ap-southeast-2
```

## Security Notes:
1. Never commit credentials to version control
2. For production, use IAM roles when running on AWS
3. Restrict permissions using IAM policies
4. Rotate credentials regularly
