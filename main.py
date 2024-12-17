import httplib2
import io
import logging
import configparser

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload

from auth import Auth

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GoogleDriveService:
    """Handles Google Drive API interactions."""

    def __init__(self, config_file="config.ini"):
        self.config_data = configparser.ConfigParser()
        self.config_data.read(config_file)
        self.drive_service = self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Drive API service."""
        gdrive = self.config_data["gdrive"]
        auth_instance = Auth(
            scopes=gdrive.get("scopes"),
            client_secret_file=gdrive.get("client_secret_file"),
            application_name=gdrive.get("application_name")
        )
        credentials = auth_instance.get_credentials()
        http = credentials.authorize(httplib2.Http())
        return discovery.build("drive", "v3", http=http)

    def download_file(self, file_id, filepath):
        """Download a file from Google Drive to the specified local filepath."""
        request = self.drive_service.files().get_media(fileId=file_id)
        with io.FileIO(filepath, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f"Download {int(status.progress() * 100)}% complete.")

    def list_files_in_folder(self, folder_id, prefix=""):
        """Recursively list all files in a Google Drive folder."""
        files = []
        page_token = None

        while True:
            response = self.drive_service.files().list(
                q=f"'{folder_id}' in parents",
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token
            ).execute()

            for file in response["files"]:
                file_id = file["id"]
                file_name = file["name"]
                mime_type = file["mimeType"]

                if mime_type == "application/vnd.google-apps.folder":
                    files.extend(self.list_files_in_folder(file_id, prefix + file_name + "/"))
                else:
                    files.append({"id": file_id, "name": file_name, "path": prefix + file_name})

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return files

if __name__ == "__main__":
    drive_service = GoogleDriveService()
    folder_id = drive_service.config_data["gdrive"].get("folder_id")
    files = drive_service.list_files_in_folder(folder_id)

    for file in files:
        logging.info(f"Found file: {file['path']} with ID: {file['id']}")
