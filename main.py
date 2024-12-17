from __future__ import print_function
import httplib2
import io
import configparser

from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload

import auth

config_data = configparser.ConfigParser()
config_data.read("config.ini")

aws_s3 = config_data["aws_s3"]
gdrive = config_data["gdrive"]


def service_return():    
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    SCOPES = gdrive.get("scopes")
    CLIENT_SECRET_FILE = gdrive.get("client_secret_file")
    APPLICATION_NAME = gdrive.get("application_name")

    authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
    credentials = authInst.getCredentials()

    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)
    return drive_service


def downloadFile(file_id, filepath):
    drive_service = service_return()

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    
    downloader = MediaIoBaseDownload(fh, request)
    return downloader
    '''done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(filepath,'wb') as f:
        fh.seek(0)
        f.write(fh.read())'''


def get_fileID_with_prefix(folder_id, prefix=""):
    """
    Recursively retrieves files and their paths from Google Drive.

    Args:
        folder_id (str): The ID of the Google Drive folder to scan.
        prefix (str): The prefix path for the current folder (used for recursion).

    Returns:
        list: A list of dictionaries with file details (name, id, path).
    """
    drive_service = service_return()
    files = []

    page_token = None
    while True:
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()
        
        for file in results['files']:
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']

            if mime_type == 'application/vnd.google-apps.folder':
                # Recursively retrieve files from subfolders
                files.extend(get_fileID_with_prefix(file_id, prefix + file_name + "/"))
            else:
                # Add file with its full path as the key
                files.append({"id": file_id, "name": file_name, "path": prefix + file_name})

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return files # return file detail

    '''print(files)
    for file in files:
        file_id = file['id']
        file_name = file['name']
        downloadFile(file_id,"GDrive/"+file_name)'''