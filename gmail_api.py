import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import Config

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailAPIFetcher:
    def __init__(self):
        self.creds = None
        self.service = None

    def authenticate(self):
        if os.path.exists(Config.TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(Config.TOKEN_FILE, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(Config.CREDENTIALS_FILE):
                    raise FileNotFoundError(f"{Config.CREDENTIALS_FILE} not found. Please download it from Google Cloud Console.")
                flow = InstalledAppFlow.from_client_secrets_file(Config.CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open(Config.TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def search_bills(self, subject_keyword, sender=None):
        from datetime import datetime, timedelta
        after_date = (datetime.now() - timedelta(days=60)).strftime("%Y/%m/%d")
        # Gmail search query: subject:(keyword) after:YYYY/MM/DD
        query = f'subject:({subject_keyword}) after:{after_date}'
        if sender:
            query = f'from:{sender} {query}'
            
        print(f"Searching Gmail with query: {query}")
        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            print(f"Found {len(messages)} messages.")
            return [m['id'] for m in messages]
        except Exception as e:
            print(f"Error searching Gmail: {e}")
            return []

    def get_message_content(self, msg_id):
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            content = {
                "subject": next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject"),
                "date": next((h['value'] for h in headers if h['name'] == 'Date'), ""),
                "body": "",
                "attachments": []
            }

            def parse_parts(parts):
                for part in parts:
                    mime_type = part.get('mimeType')
                    body_data = part.get('body', {}).get('data')
                    
                    if mime_type == 'text/html' and body_data:
                        content['body'] = base64.urlsafe_b64decode(body_data).decode()
                    elif mime_type == 'text/plain' and body_data and not content['body']:
                        content['body'] = base64.urlsafe_b64decode(body_data).decode()
                    elif part.get('filename') and part.get('body', {}).get('attachmentId'):
                        att_id = part['body']['attachmentId']
                        att_data = self.service.users().messages().attachments().get(
                            userId='me', messageId=msg_id, id=att_id).execute()
                        data = base64.urlsafe_b64decode(att_data['data'])
                        content['attachments'].append({
                            "name": part['filename'],
                            "content": data
                        })
                    
                    if 'parts' in part:
                        parse_parts(part['parts'])

            if 'parts' in payload:
                parse_parts(payload['parts'])
            else:
                body_data = payload.get('body', {}).get('data')
                if body_data:
                    content['body'] = base64.urlsafe_b64decode(body_data).decode()
            
            if not content['body']:
                print(f"[GmailAPI] Warning: No body found for message {msg_id}")
            
            return content
        except Exception as e:
            print(f"Error getting message content: {e}")
            return None
