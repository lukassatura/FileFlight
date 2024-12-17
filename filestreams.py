import io
import logging
import configparser
from tqdm import tqdm  # For progress bars

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from googleapiclient.http import MediaIoBaseDownload

from main import GoogleDriveService

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    handlers=[
        logging.FileHandler("migration.log", mode="a"),
        logging.StreamHandler()  # This outputs logs to the console
    ]
)

class S3Uploader:
    """Handles interactions with Amazon S3 for file uploads."""

    def __init__(self, config_file="config.ini"):
        self.config_data = configparser.ConfigParser()
        self.config_data.read(config_file)
        self.s3_config = self.config_data["aws_s3"]
        self.bucket_name = self.s3_config.get("bucket_name")
        self.s3_client = boto3.client(
            self.s3_config.get("name"),
            region_name=self.s3_config.get("region_name")
        )

    def check_object_exists(self, object_key):
        """Check if a file already exists in the S3 bucket."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logging.error(f"Error checking object existence in S3: {str(e)}")
            raise

    def upload_file(self, file_stream, object_key):
        """Uploads a file stream to S3 with the specified storage class."""
        file_size = len(file_stream.getvalue())
        file_stream.seek(0)  # Reset stream position for upload

        progress = tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Uploading {object_key}", leave=False)

        def upload_progress(bytes_transferred):
            progress.update(bytes_transferred)

        try:
            logging.info(f"Uploading file '{object_key}' to S3 bucket '{self.bucket_name}'...")
            self.s3_client.upload_fileobj(
                file_stream, 
                self.bucket_name, 
                object_key,
                ExtraArgs={"StorageClass": "GLACIER_IR"},
                Callback=upload_progress
            )
            progress.close()
            logging.info(f"File '{object_key}' uploaded successfully to S3.")
        except NoCredentialsError:
            logging.error("AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            logging.error(f"Failed to upload file '{object_key}'. Error: {str(e)}")
            progress.close()
            raise

class FileMigration:
    """Coordinates file migration from Google Drive to Amazon S3."""

    def __init__(self):
        self.drive_service = GoogleDriveService()
        self.s3_uploader = S3Uploader()

    def upload_file_from_drive(self, file_id, object_key):
        """Downloads a file from Google Drive and uploads it to S3."""
        request = self.drive_service.drive_service.files().get_media(fileId=file_id)
        file_metadata = self.drive_service.drive_service.files().get(fileId=file_id, fields="size").execute()
        file_size = int(file_metadata.get("size", 0))

        fh = io.BytesIO()
        progress = tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Downloading {object_key}", leave=False)
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            progress.update(int(status.resumable_progress) - progress.n)
        progress.close()

        fh.seek(0)
        self.s3_uploader.upload_file(fh, object_key)

    def migrate_files(self):
        """Migrates all files from Google Drive to S3."""
        folder_id = self.drive_service.config_data["gdrive"].get("folder_id")
        files_list = self.drive_service.list_files_in_folder(folder_id)

        total_files = len(files_list)
        file_progress = tqdm(total=total_files, desc="File Migration Progress", unit="file")

        for file_info in files_list:
            file_id = file_info["id"]
            object_key = file_info["path"]

            if self.s3_uploader.check_object_exists(object_key):
                logging.info(f"File already exists in S3, skipping: {object_key}")
                file_progress.update(1)
                continue

            try:
                self.upload_file_from_drive(file_id, object_key)
                file_progress.update(1)
            except Exception as e:
                logging.error(f"Error processing file '{object_key}': {e}")

        file_progress.close()
        logging.info("All files have been processed.")

if __name__ == "__main__":
    migrator = FileMigration()
    migrator.migrate_files()
