from gmail_api import GmailAPIFetcher
import os

def diagnose():
    fetcher = GmailAPIFetcher()
    try:
        fetcher.authenticate()
        print("Authenticated successfully.")
        
        # List messages matching '信用卡' or '帳單'
        query = '信用卡 OR 帳單'
        print(f"Searching for query: {query}")
        results = fetcher.service.users().messages().list(userId='me', q=query, maxResults=30).execute()
        messages = results.get('messages', [])
        
        print(f"Found {len(messages)} messages:")
        for m in messages:
            msg = fetcher.service.users().messages().get(userId='me', id=m['id'], format='full').execute()
            headers = msg.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            print(f"- {subject}")
            
    except Exception as e:
        print(f"Diagnosis failed: {e}")

if __name__ == "__main__":
    diagnose()
