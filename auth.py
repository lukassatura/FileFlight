import os
import logging

from oauth2client import client, tools
from oauth2client.file import Storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="migration.log", filemode="a")

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

class Auth:
    """Handles Google Drive OAuth2 authentication."""

    def __init__(self, scopes, client_secret_file, application_name):
        self.scopes = scopes
        self.client_secret_file = client_secret_file
        self.application_name = application_name

    def get_credentials(self):
        """
        Retrieves valid user credentials from storage or generates new ones via OAuth2 flow.

        Returns:
            credentials: The obtained credentials object.
        """
        credential_dir = os.path.join(os.getcwd(), '.credentials')
        os.makedirs(credential_dir, exist_ok=True)
        credential_path = os.path.join(credential_dir, 'google-drive-credentials.json')

        store = Storage(credential_path)
        credentials = store.get()
        
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            flow.user_agent = self.application_name
            credentials = tools.run_flow(flow, store, flags) if flags else tools.run(flow, store)
            print(f'Storing credentials to {credential_path}')
        
        return credentials
