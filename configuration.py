"""
Make sure to replace:
    <YOUR-AWS-REGION>
    <YOUR-BUCKET-NAME>
    <YOUR-GCP-APP-NAME>
    <YOUR-GDRIVE-FOLDER-ID> 
with your values.

AWS credentials are either exported from AWS such as `export aws_access_key_id=…` 
or may be deleted - boto3 will find them in ~/.aws/credentials.
"""
import os
import configparser
from dotenv import load_dotenv

load_dotenv()

class ConfigManager:
    """Handles configuration for AWS S3 and Google Drive."""

    def __init__(self):
        self.config = configparser.ConfigParser()

    def setup(self):
        """Set up configuration for AWS S3 and Google Drive."""
        self._setup_aws()
        self._setup_gdrive()

    def _setup_aws(self):
        """Set up AWS S3 configuration."""
        self.config.add_section("aws_s3")
        self.config.set("aws_s3", "name", "s3")
        self.config.set("aws_s3", "region_name", "<YOUR-AWS-REGION>")
        self.config.set("aws_s3", "bucket_name", "<YOUR-BUCKET-NAME>")
        self.config.set("aws_s3", "access_key", os.getenv("aws_access_key_id"))
        self.config.set("aws_s3", "access_secret", os.getenv("aws_secret_access_key"))

    def _setup_gdrive(self):
        """Set up Google Drive configuration."""
        self.config.add_section("gdrive")
        self.config.set("gdrive", "scopes", "https://www.googleapis.com/auth/drive")
        self.config.set("gdrive", "client_secret_file", "client_secret.json")
        self.config.set("gdrive", "application_name", "<YOUR-GCP-APP-NAME>")
        self.config.set("gdrive", "folder_id", "<YOUR-GDRIVE-FOLDER-ID>")

    def save_config(self, filename="config.ini"):
        """Save the configuration to a file."""
        with open(filename, "w") as configfile:
            self.config.write(configfile)

if __name__ == "__main__":
    config_manager = ConfigManager()
    config_manager.setup()
    config_manager.save_config()