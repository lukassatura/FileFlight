# FileFlight

## Overview
FileFlight is a streamlined solution for migrating files from Google Drive to an Amazon S3 bucket. Designed with cost-efficiency and simplicity in mind, FileFlight automates the transfer process, allowing users to organize their cloud storage while minimizing manual intervention. It is based on the blog post [Migration between Google Drive and S3 Bucket](https://medium.com/@krish.joshi.02/migration-between-google-drive-and-s3-bucket-c3ddd0b7b507).

## Motivation
Managing files across multiple cloud platforms can be challenging and expensive. FileFlight was born out of the need to reduce cloud storage costs by taking advantage of S3's flexible pricing and efficient storage solutions, such as Glacier Instant Retrieval. With a touch of wit and practicality, FileFlight soars through your file migration tasks with ease!

## Features
- **Automated Migration**: Transfers all files from a specified Google Drive folder (including subfolders) to an Amazon S3 bucket.
- **Progress Tracking**: Displays detailed progress bars for both downloads and uploads.
- **Resume Capability**: Skips files already present in S3 to avoid redundant uploads.
- **Error Handling**: Logs errors and ensures traceability in the migration process.
- **Modular Design**: Easily extend or adapt the functionality to suit your needs.

## Prerequisites
1. Python 3.7+
2. AWS CLI configured with access to the target S3 bucket.
3. Google Cloud credentials for accessing the Google Drive API.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lukassatura/FileFlight.git
   cd FileFlight
   ```
2. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Google Cloud credentials:
   - Download your `client_secret.json` file from the Google Cloud Console following the [tutorial of the blog post](https://medium.com/@krish.joshi.02/migration-between-google-drive-and-s3-bucket-c3ddd0b7b507).
   - Place the file in the project root directory.
4. Set up AWS credentials:
   - Configure your `.env` file with the following keys:
     ```env
     aws_access_key_id=<Your AWS Access Key>
     aws_secret_access_key=<Your AWS Secret Access Key>
     ```

## Configuration

Edit the `configuration.py` file to match your environment and project names; replace:
```python
<YOUR-AWS-REGION>
<YOUR-BUCKET-NAME>
<YOUR-GCP-APP-NAME>
<YOUR-GDRIVE-FOLDER-ID> 
```
with correct values.

After running `python configuration.py`, the `config.ini` is created, such as:

```ini
[aws_s3]
name = s3
region_name = <Your Region>
bucket_name = <Your Bucket Name>

[gdrive]
scopes = https://www.googleapis.com/auth/drive
client_secret_file = client_secret.json
application_name = FileFlight
folder_id = <Your Google Drive Folder ID>
```

## Usage

Run the migration script:
```bash
python filestreams.py
```

The script will:
1. Retrieve all files from the specified Google Drive folder.
2. Check for each file's existence in the S3 bucket.
3. Download files from Google Drive and upload them to S3.

Progress and logs are displayed in real-time and saved to `migration.log`.

## How It Works

1. **Google Drive Integration**: FileFlight uses the Google Drive API to fetch file metadata and content.
2. **Amazon S3 Integration**: Files are uploaded to the specified S3 bucket using the Boto3 library.
3. **File Path Preservation**: Files retain their folder structure from Google Drive when uploaded to S3.

## Modular Structure
- `filestreams.py`: Orchestrates the file migration process.
- `auth.py`: Handles Google API authentication.
- `config.ini`: Stores configuration settings.
- `main.py`: Contains logic for file downloads and uploads. Lists the files in GDrive

## Running on EC2 and Monitoring with tmux

Copy the files `auth.py`, `main.py`, `filestreams.py`, `config.ini` (once it is generated) as well as your `client_secret.json` and the `.credentials` directory to your EC2 instance, such as:
```bash
scp -i myKeyPair.pem auth.py main.py filestreams.py config.ini client_secret.json .credentials ec2-user@<your-ec2-public-DNS>:~
```

To ensure the script runs uninterrupted on an EC2 instance, use `tmux` to manage the session:

```bash
tmux new -s fileflight
```

Run the migration script inside tmux:

```bash
python filestreams.py
```

Monitor logs in a split terminal. Split the tmux window vertically by pressing `Ctrl+b`, then just `%`. In the new pane, run:
```bash
tail -f migration.log
```

Switch between panes by pressing `Ctrl+b` followed by arrow keys to navigate between the panes.

Detach from the tmux session, i.e. leave the tmux session running in the background by pressing `Ctrl+b`, then just `d`

Reattach to the tmux session later:
```bash
tmux attach -t fileflight
```

After the script finishes, you can terminate the tmux session:
```bash
tmux kill-session -t fileflight
```

The script run provides nice progress of your migration job:
![A screenshot of the migration job.](/img/upload_progress.png)

