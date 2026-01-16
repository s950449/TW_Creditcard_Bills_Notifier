import keyring
import argparse
from keyring.errors import NoKeyringError

SERVICE_NAME = "CreditcardBillNotifier"

class KeyringManager:
    @staticmethod
    def set_password(key, value):
        try:
            keyring.set_password(SERVICE_NAME, key, value)
        except NoKeyringError:
            print(f"[Keyring] Warning: No keyring backend found. Could not set {key}.")
        except Exception as e:
            print(f"[Keyring] Error setting {key}: {e}")

    @staticmethod
    def get_password(key):
        try:
            return keyring.get_password(SERVICE_NAME, key)
        except NoKeyringError:
            print(f"[Keyring] Warning: No keyring backend found. Falling back to other sources for {key}.")
            return None
        except Exception as e:
            print(f"[Keyring] Error getting {key}: {e}")
            return None

    @staticmethod
    def delete_password(key):
        try:
            keyring.delete_password(SERVICE_NAME, key)
            return True
        except keyring.errors.PasswordDeleteError:
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage credentials in gnome-keyring")
    parser.add_argument("action", choices=["set", "get", "delete"], help="Action to perform")
    parser.add_argument("key", help="The credential key (e.g., EMAIL_PASSWORD)")
    parser.add_argument("value", nargs="?", help="The value to set (only for 'set' action)")

    args = parser.parse_args()

    if args.action == "set":
        if not args.value:
            print("Error: Value is required for 'set' action")
        else:
            KeyringManager.set_password(args.key, args.value)
            print(f"Successfully set {args.key}")
    elif args.action == "get":
        val = KeyringManager.get_password(args.key)
        print(f"{args.key}: {val}")
    elif args.action == "delete":
        if KeyringManager.delete_password(args.key):
            print(f"Successfully deleted {args.key}")
        else:
            print(f"Failed to delete {args.key} (might not exist)")
