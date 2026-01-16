import requests
from config import Config

class Notifier:
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}/"
    def get_GroupChatID(self):
        response = requests.get(self.api_url + "getUpdates")
        updates = response.json()
        print(updates)
        for update in updates["result"]:
            if update["message"]["chat"]["type"] == "group":
                return update["message"]["chat"]["id"]
        return None
    def getUserChatID(self):
        response = requests.get(self.api_url + "getUpdates")
        updates = response.json()
        print(updates)
        for update in updates["result"]:
            if update["message"]["chat"]["type"] == "private":
                return update["message"]["chat"]["id"]
        return None
    def send_notification(self, bank, amount, due_date, currency="TWD"):
        message = (
            f"🔔 *信用卡繳費提醒*\n\n"
            f"🏦 銀行：{bank}\n"
            f"💰 金額：{currency} {amount:,.0f}\n"
            f"📅 截止日期：{due_date}\n\n"
            f"請記得在三天前完成繳款喔！"
        )
        
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }


        
        try:
            response = requests.post(self.api_url + "sendMessage", json=payload)
            print(response.json())
            response.raise_for_status()
            return True
        except Exception as e:
            # Fallback: Try to fetch updates to auto-detect chat ID if missing
            try:
                response = requests.get(self.api_url + "getUpdates")
                updates = response.json()
                print(f"Debug Updates: {updates}")
                
                new_chat_id = None
                if "result" in updates:
                    for update in updates["result"]:
                        # Check for 'message'
                        if "message" in update and "chat" in update["message"]:
                            chat = update["message"]["chat"]
                            if chat.get("type") == "private":
                                new_chat_id = chat["id"]
                                break # Found a private chat, use it
                        # Check for 'my_chat_member' (bot added to group)
                        elif "my_chat_member" in update and "chat" in update["my_chat_member"]:
                             chat = update["my_chat_member"]["chat"]
                             new_chat_id = chat["id"]
                             break

                if new_chat_id:
                    print(f"Auto-detected Chat ID: {new_chat_id}")
                    self.chat_id = new_chat_id
                    # Retry sending with the new chat ID
                    payload["chat_id"] = self.chat_id
                    response = requests.post(self.api_url + "sendMessage", json=payload)
                    response.raise_for_status()
                    return True

            except Exception as inner_e:
                print(f"Auto-detection failed: {inner_e}")

            print(f"Failed to send Telegram notification: {e}")
            return False
