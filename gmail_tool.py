import base64
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from auth import get_credentials

def get_gmail_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def _create_message(to: str, subject: str, html_body: str, text_body: str) -> dict:
    """Helper to create a base64url encoded MIME multipart message."""
    message = MIMEMultipart('alternative')
    message['To'] = to
    message['Subject'] = subject
    
    # According to RFC 2046, the last part of a multipart/alternative is the one 
    # preferred by the sender. So we attach text first, then HTML.
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    
    message.attach(part1)
    message.attach(part2)
    
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': encoded_message}

def send_email(to: str, subject: str, html_body: str, text_body: str) -> dict:
    """Sends an email immediately."""
    service = get_gmail_service()
    msg = _create_message(to, subject, html_body, text_body)
    
    sent_message = service.users().messages().send(userId='me', body=msg).execute()
    return {
        "status": "success",
        "messageId": sent_message['id'],
        "message": f"Email sent to {to}"
    }

def create_draft(to: str, subject: str, html_body: str, text_body: str) -> dict:
    """Creates a draft without sending."""
    service = get_gmail_service()
    msg = _create_message(to, subject, html_body, text_body)
    
    draft_body = {'message': msg}
    draft = service.users().drafts().create(userId='me', body=draft_body).execute()
    return {
        "status": "success",
        "draftId": draft['id'],
        "message": f"Draft created for {to}"
    }
