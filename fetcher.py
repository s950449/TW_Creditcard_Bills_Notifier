import imaplib
import email
from email.header import decode_header
from config import Config

class EmailFetcher:
    def __init__(self):
        self.user = Config.EMAIL_USER
        self.password = Config.EMAIL_PASSWORD
        self.server = Config.IMAP_SERVER

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.server)
        self.mail.login(self.user, self.password)
        self.mail.select("inbox")

    def search_bills(self, subject_keyword, sender=None):
        # Search for emails from the last 30 days
        # Using the subject keyword to filter
        search_query = f'SUBJECT "{subject_keyword}"'
        if sender:
            search_query = f'FROM "{sender}" {search_query}'
            
        status, messages = self.mail.search(None, search_query)
        
        if status != "OK":
            return []
    
            message_ids = messages[0].split()
            return message_ids

    def get_message_content(self, msg_id):
        status, data = self.mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            return None

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        content = {
            "subject": self._decode_subject(msg["Subject"]),
            "date": msg["Date"],
            "body": "",
            "attachments": []
        }

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/html":
                    content["body"] = part.get_payload(decode=True).decode()
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        content["attachments"].append({
                            "name": filename,
                            "content": part.get_payload(decode=True)
                        })
        else:
            content["body"] = msg.get_payload(decode=True).decode()

        return content

    def _decode_subject(self, subject):
        decoded, encoding = decode_header(subject)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding or "utf-8")
        return decoded

    def logout(self):
        self.mail.close()
        self.mail.logout()
