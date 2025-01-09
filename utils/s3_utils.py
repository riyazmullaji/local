# utils/s3_utils.py

import boto3
from botocore.exceptions import NoCredentialsError

# Initialize the S3 client
def get_s3_client():
    """Create and return an S3 client."""
    return boto3.client('s3')

def upload_file_to_s3(local_file_path, bucket_name, s3_file_name):
    """Upload a file to S3 bucket."""
    s3 = get_s3_client()
    try:
        s3.upload_file(local_file_path, bucket_name, s3_file_name)
        print(f"File uploaded successfully: {s3_file_name}")
        return True
    except FileNotFoundError:
        print(f"File {local_file_path} not found.")
        return False
    except NoCredentialsError:
        print("Credentials not available.")
        return False
