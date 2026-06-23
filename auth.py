import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def get_credentials():
    """Gets valid user credentials from storage.
    
    Checks environment variables first (for production), then falls back to local files.
    """
    creds = None
    
    # Check for token in environment variable
    if 'GOOGLE_TOKEN_JSON' in os.environ:
        token_info = json.loads(os.environ['GOOGLE_TOKEN_JSON'])
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    elif os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
                client_config = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            elif os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            else:
                raise FileNotFoundError("credentials.json is missing. Please download it from Google Cloud Console or set GOOGLE_CREDENTIALS_JSON.")
            
            # Use run_local_server with open_browser=False to avoid issues in headless environments
            # However, the user needs to visit the URL to authenticate. The URL will be printed
            # to the console. We avoid using input() or any terminal prompts.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) if not 'GOOGLE_CREDENTIALS_JSON' in os.environ else InstalledAppFlow.from_client_config(json.loads(os.environ['GOOGLE_CREDENTIALS_JSON']), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
            
        # Save the credentials for the next run if possible
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception:
            pass # Ignore if filesystem is read-only in production
            
    return creds

if __name__ == "__main__":
    print("Checking credentials...")
    creds = get_credentials()
    if creds and creds.valid:
        print("Success! token.json is valid and ready to use.")
    else:
        print("Failed to get valid credentials.")
