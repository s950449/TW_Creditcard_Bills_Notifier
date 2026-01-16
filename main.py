import argparse
from datetime import datetime, timedelta
from config import Config
from fetcher import EmailFetcher
from database import Database
from notifier import Notifier
from banks import ParserFactory

from gmail_api import GmailAPIFetcher

def run_fetch():
    db = Database()
    
    if Config.USE_GMAIL_API:
        print("Connecting to Gmail API...")
        fetcher = GmailAPIFetcher()
        try:
            fetcher.authenticate()
        except Exception as e:
            print(f"Gmail API Authentication failed: {e}")
            print("Falling back to IMAP...")
            fetcher = EmailFetcher()
            fetcher.connect()
    else:
        print("Connecting to Gmail via IMAP...")
        fetcher = EmailFetcher()
        fetcher.connect()
    
    bank_infos = ParserFactory.get_all_bank_info()
    
    for bank_id, info in bank_infos.items():
        keyword = info["keyword"]
        sender = info.get("sender")
        pdf_name_filter = info.get("pdf_name")
        
        print(f"Searching for {bank_id} bills...")
        # Gmail API and IMAPFetcher have slightly different signatures for search_bills
        if Config.USE_GMAIL_API and isinstance(fetcher, GmailAPIFetcher):
            msg_ids = fetcher.search_bills(keyword, sender=sender)
        else:
            msg_ids = fetcher.search_bills(keyword, sender=sender)
            
        for msg_id in msg_ids:
            content = fetcher.get_message_content(msg_id)
            if not content:
                continue
                
            parser = ParserFactory.get_parser(bank_id)
            bill_info = None
            
            # 1. Try parsing HTML body
            bill_info = parser.parse_email(content["body"])
            
            # 2. If incomplete or missing, try parsing PDF/HTML attachments
            if (not bill_info or not bill_info.get("amount") or not bill_info.get("due_date")) and (content["body"] or content["attachments"]):
                print(f"[{bank_id}] Body parse incomplete. Checking attachments for missing info...")
                
                # Start with what we have from the body
                current_bill_info = bill_info if bill_info else {}
                
                for att in content["attachments"]:
                    att_name_lower = att["name"].lower()
                    att_info = None
                    if att_name_lower.endswith(".pdf"):
                        # If pdf_name is specified, filter by it
                        if pdf_name_filter and pdf_name_filter not in att["name"]:
                            print(f"[{bank_id}] Skipping PDF {att['name']} (doesn't match {pdf_name_filter})")
                            continue
                        att_info = parser.parse_pdf(att["content"])
                    elif att_name_lower.endswith(".html") or att_name_lower.endswith(".htm"):
                        print(f"[{bank_id}] Attempting to parse HTML attachment: {att['name']}")
                        att_info = parser.parse_html_attachment(att["content"])
                    
                    if att_info:
                        # Merge into current_bill_info
                        for k, v in att_info.items():
                            if v is not None:
                                current_bill_info[k] = v
                                
                if current_bill_info and current_bill_info.get("amount") is not None:
                    bill_info = current_bill_info

            if bill_info:
                # Ensure we have a due date; if not, use a fallback from email date
                if not bill_info.get("due_date"):
                    bill_info["due_date"] = content["date"].split(' ')[0].replace('-', '/')
                    print(f"[{bank_id}] Warning: Missing due date, using email date fallback: {bill_info['due_date']}")

                # Create a unique ID for the bill to avoid duplicates
                bill_id = f"{bill_info['bank']}_{bill_info['due_date'].replace('/', '')}"
                bill_info["id"] = bill_id
                bill_info["bill_date"] = content["date"]
                
                db.upsert_bill(bill_info)
                print(f"✅ Found {bill_info['bank']} bill: {bill_info['amount']} due on {bill_info['due_date']}")

    if isinstance(fetcher, EmailFetcher):
        fetcher.logout()
        print("Logout")

def run_notify():
    db = Database()
    notifier = Notifier()
    
    # Check bills due in Config.REMIND_DAYS_BEFORE days
    target_date = (datetime.now() + timedelta(days=Config.REMIND_DAYS_BEFORE)).strftime("%Y/%m/%d")
    
    # Look for bills in the DB that match the target date and hasn't been notified
    bills = list(db.db["bills"].rows_where("due_date = ? AND notified = 0", [target_date]))
    
    for bill in bills:
        print(f"Sending notification for {bill['bank']}...")
        if notifier.send_notification(bill["bank"], bill["amount"], bill["due_date"]):
            db.mark_as_notified(bill["id"])
            print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Credit Card Bill Notifier")
    parser.add_argument("--fetch", action="store_true", help="Fetch new bills from email")
    parser.add_argument("--notify", action="store_true", help="Send upcoming notifications")
    parser.add_argument("--test-notify", action="store_true", help="Send a test notification")
    parser.add_argument("--get-group-id", action="store_true", help="Get group chat ID")
    parser.add_argument("--get-user-id", action="store_true", help="Get user chat ID")
    
    args = parser.parse_args()
    
    if args.fetch:
        run_fetch()
    elif args.notify:
        run_notify()
    elif args.test_notify:
        Notifier().send_notification("測試銀行", 1234.56, "2026/01/17")
    elif args.get_group_id:
        Notifier().get_GroupChatID()
    elif args.get_user_id:
        Notifier().getUserChatID()
    else:
        parser.print_help()
