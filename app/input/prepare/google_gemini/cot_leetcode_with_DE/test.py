import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import pprint
import google.generativeai as genai


SCOPES = ['https://www.googleapis.com/auth/generative-language.tuning']

def load_creds():
    """Converts `oauth-client-id.json` to a credential object.

    This function caches the generated tokens to minimize the use of the
    consent screen.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth-client-id.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

creds = load_creds()

genai.configure(credentials=creds)

print()
print('Available base models:', [m.name for m in genai.list_tuned_models()])
print('My tuned models:', [m.name for m in genai.list_tuned_models()])