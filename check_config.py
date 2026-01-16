from config import Config
import os

def check_config():
    print(f"EMAIL_USER: {'Set' if Config.EMAIL_USER else 'NOT SET'}")
    print(f"EMAIL_PASSWORD: {'Set' if Config.EMAIL_PASSWORD else 'NOT SET'}")
    print(f"TELEGRAM_BOT_TOKEN: {'Set' if Config.TELEGRAM_BOT_TOKEN else 'NOT SET'}")
    print(f"TELEGRAM_CHAT_ID: {'Set' if Config.TELEGRAM_CHAT_ID else 'NOT SET'}")
    print(f"ID_NUMBER: {'Set' if Config.ID_NUMBER else 'NOT SET'}")
    if Config.ID_NUMBER:
        print(f"ID_NUMBER starts with: {Config.ID_NUMBER[0] if Config.ID_NUMBER else ''} (Len: {len(Config.ID_NUMBER)})")
    print(f"USE_GMAIL_API: {Config.USE_GMAIL_API}")
    print(f"Database Path: {Config.DB_PATH}")

if __name__ == "__main__":
    check_config()
