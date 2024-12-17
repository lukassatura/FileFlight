from __future__ import print_function
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
    
class auth:
    def __init__(self, SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        self.APPLICATION_NAME = APPLICATION_NAME

    def getCredentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        cwd_dir = os.getcwd() 
        credential_dir = os.path.join(cwd_dir, '.credentials') # Creating Sub-directory .credentials where api credentials will be stored
        
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                    'google-drive-credentials.json')

        store = Storage(credential_path)
        credentials = store.get() # get credentials from folder
        
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES) 
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials