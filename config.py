import os
from dotenv import load_dotenv
from keyring_manager import KeyringManager

load_dotenv()

class Config:
    # Email settings
    EMAIL_USER = os.getenv("EMAIL_USER")
    # Fetch from Keyring first, then .env
    EMAIL_PASSWORD = KeyringManager.get_password("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD")
    IMAP_SERVER = "imap.gmail.com"

    # Telegram settings
    TELEGRAM_BOT_TOKEN = KeyringManager.get_password("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = KeyringManager.get_password("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

    # Bank credentials (for PDF decryption)
    ID_NUMBER = KeyringManager.get_password("ID_NUMBER") or os.getenv("ID_NUMBER")
    BIRTHDAY = KeyringManager.get_password("BIRTHDAY") or os.getenv("BIRTHDAY") # e.g. MMDD or YYYYMMDD

    # Database settings
    DB_PATH = os.path.join(os.getcwd(), "bills.db")

    # Gmail API settings
    USE_GMAIL_API = os.getenv("USE_GMAIL_API", "true").lower() == "true"
    CREDENTIALS_FILE = os.path.join(os.getcwd(), "credentials.json")
    TOKEN_FILE = os.path.join(os.getcwd(), "token.json")

    # Notification settings
    REMIND_DAYS_BEFORE = 3

    @staticmethod
    def get_bank_password(bank_id):
        key = f"{bank_id}_PASSWORD"
        return KeyringManager.get_password(key) or os.getenv(key) or Config.ID_NUMBER
