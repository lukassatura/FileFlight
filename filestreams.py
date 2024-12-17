import io
import logging
import configparser
from tqdm import tqdm  # For progress bars

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from googleapiclient.http import MediaIoBaseDownload

from main import get_fileID_with_prefix, service_return

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    handlers=[
        logging.FileHandler("migration.log", mode="a"),
        logging.StreamHandler()  # This outputs logs to the console
    ]
    )

config_data = configparser.ConfigParser()
config_data.read("config.ini")

aws_s3 = config_data["aws_s3"]
gdrive = config_data["gdrive"]

drive_service = service_return()


def check_s3_object_exists(bucket_name, object_key):
    """
    Check if a file already exists in the S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The S3 object key (path in the bucket).

    Returns:
        bool: True if the object exists, False otherwise.
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            logging.error(f"Error checking object existence in S3: {str(e)}")
            raise


def upload_to_s3(bucket_name, file_stream, object_key):
    """
    Uploads a file stream to S3 with the specified storage class.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        file_stream (BytesIO): The file stream to upload.
        object_key (str): The S3 object key (path in the bucket).
    """
    # ACCESS_SECRET = aws_s3.get("access_secret")
    # ACCESS_KEY = aws_s3.get("access_key")
    
    s3_client = boto3.client(
        aws_s3.get("name"), 
        region_name=aws_s3.get("region_name"), 
        #  aws_access_key_id=aws_s3.get("access_key"),
        #  aws_secret_access_key=aws_s3.get("access_secret")
    )
    file_size = len(file_stream.getvalue())  # Get file size
    file_stream.seek(0)  # Reset stream position for upload

    progress = tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Uploading {object_key}", leave=False)

    def upload_progress(bytes_transferred):
        progress.update(bytes_transferred)
    
    logging.info(f"Uploading file '{object_key}' to S3 bucket '{bucket_name}'...")
    
    try:
        # Generate a unique object key based on the file name
        s3_client.upload_fileobj(
            file_stream, 
            bucket_name, 
            object_key,
            ExtraArgs={"StorageClass": "GLACIER_IR"},
            Callback=upload_progress
            )
        progress.close()
        logging.info(f'File {object_key} uploaded to Amazon S3 with Glacier Instant Retrieval storage class.')
        
    except NoCredentialsError:
        logging.error("AWS credentials not found. Please configure AWS credentials.")
        raise
    except Exception as e:
        logging.error(f"Failed to upload file '{object_key}'. Error: {str(e)}")
        progress.close()
        raise

# Example usage
bucket_name = aws_s3.get("bucket_name")

def upload_file_from_drive(file_id, object_key):
    """
    Downloads a file from Google Drive and uploads it to S3 with the specified object key.

    Args:
        file_id (str): The Google Drive file ID.
        object_key (str): The key for the object in the S3 bucket.
    """
    request = drive_service.files().get_media(fileId=file_id)
    file_metadata = drive_service.files().get(fileId=file_id, fields="size").execute()
    file_size = int(file_metadata.get("size", 0))  # Get file size from metadata

    fh = io.BytesIO()
    progress = tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Downloading {object_key}", leave=False)

    downloader = MediaIoBaseDownload(fh, request)

    # Download the file from Google Drive and save it in the file stream
    done = False
    while not done:
        status, done = downloader.next_chunk()
        progress.update(int(status.resumable_progress) - progress.n)

    progress.close()
    # Set the file stream position to the beginning for uploading
    fh.seek(0)
    # Upload the file stream to Amazon S3 using the original file name
    upload_to_s3(bucket_name, fh, object_key)

# Usage example
folder_id = gdrive.get("folder_id")
files_list = get_fileID_with_prefix(folder_id)

# Initialize tqdm progress bar for the total number of files
total_files = len(files_list)
file_progress = tqdm(total=total_files, desc="File Migration Progress", unit="file")

for file_info in files_list:
    
    file_id = file_info['id']
    object_key = file_info['path']

    if check_s3_object_exists(bucket_name, object_key):
        logging.info(f"File already exists in S3, skipping: {object_key}")
        file_progress.update(1)
        continue
    try:
        upload_file_from_drive(file_id, object_key)
        file_progress.update(1)  # Increment progress by 1 file
    except Exception as e:
        logging.error(f"Error processing file '{file_info['path']}': {e}")
    finally:
        file_progress.update(1)

file_progress.close()
logging.info("All files have been processed.")