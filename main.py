import os
import pickle
import re
import time
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from apiclient import errors
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
# TO UPDATE: set QUERY constant to any parameters with QUERY in functions
our_email = 'test@gmail.com'
QUERY = ''

def gmail_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            #searches for client secret file. By default contains client_secret_
            # UPDATED: Search for client secret file as long as it's in the folder
            # TO DO: further test if re.search() returns a string properly
            path_file = "C:\\Users\\katie\\OneDrive\\Documents\\Projects\\gmail-archiving\\client_secret\\"
            for filename in os.listdir(path_file):
                if re.match("client_secret+_[0-9]+-[a-z0-9]+.apps.googleusercontent.com.json+", filename):
                    flow = InstalledAppFlow.from_client_secrets_file(path_file+filename, SCOPES)
                    creds = flow.run_local_server(port=0)

        #credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds,token)
    return build('gmail', 'v1', credentials=creds)

# get Gmail APi service
service = gmail_authenticate()

def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
 #   print(f"Found {len(result)} emails.")
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        messages.extend(result['messages'])
        if len(messages) > 999:
            break
    return messages
    
def delete_messages(service, query):
    messages_to_delete = search_messages(service, query)
    # it's possible to delete a single message with the delete API, like this:
    # service.users().messages().delete(userId='me', id=msg['id'])
    # but it's also possible to delete all the selected messages with one query, batchDelete
    print(f"Deleting {len(messages_to_delete)} emails.")
    return service.users().messages().batchDelete(
      userId='me',
      body={
          'ids': [ msg['id'] for msg in messages_to_delete]
      }
    ).execute()

if __name__ == "__main__":
    service = gmail_authenticate()
    i = 0

    while i < 600:
        delete_messages(service, "from: noreply@ozbargain.com.au older_than:1y")
    else:
        print("None")
    i = i + 1
    time.sleep(5)
