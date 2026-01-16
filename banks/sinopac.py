import re
from banks.parser_base import BaseParser

class SinoPacParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def parse_email(self, msg_body, html=True):
        print(f"[SinoPacParser] Attempting to parse email body (html={html})...")
        return super().parse_email(msg_body, html)

    def _extract_info_from_text(self, text):
        # Normalize text: replace 台 with 臺 for consistency
        text_norm = text.replace("台幣", "臺幣").replace("台幣", "臺幣")
        
        amount = None
        due_date = None

        # 1. Target the specific sentence: 您的預定扣款金額 [金額] 元將於 [日期] ...
        # This is the most reliable one if it exists.
        sentence_pattern = r"您的預定扣款金額\s*(?:臺幣)?\s*([\d,]+)\s*元.*?將於\s*(\d{4}/\d{2}/\d{2})"
        match = re.search(sentence_pattern, text_norm, re.DOTALL)
        if match:
            amount = float(match.group(1).replace(",", ""))
            due_date = match.group(2)
            print(f"[SinoPacParser] Matched sentence pattern. Amount: {amount}, Due: {due_date}")
        else:
            # 2. Fallback: Search for amount and due date separately if sentence match fails
            # Search for Due Date: 您的繳款截止日YYYY/MM/DD
            date_match = re.search(r"您的繳款截止日\s*(\d{4}/\d{2}/\d{2})", text_norm)
            if date_match:
                due_date = date_match.group(1)
            
            # Search for Amount in the table: 臺幣 ... [金額] (last columns are 本期應繳總金額 and 本期最低應繳金額)
            # The log shows: 臺幣 300 300 1,353 0 0 1,353 500
            # We want the one before the last (本期應繳總金額)
            table_pattern = r"臺幣\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+([\d,.]+)\s+[\d,.]+"
            table_match = re.search(table_pattern, text_norm)
            if table_match:
                amount = float(table_match.group(1).replace(",", ""))
                print(f"[SinoPacParser] Matched table pattern. Amount: {amount}")

        if amount is not None and due_date:
            return {
                "bank": self.bank_name,
                "amount": amount,
                "due_date": due_date,
                "currency": "TWD"
            }
        
        print(f"[SinoPacParser] Specific extraction failed. Falling back to generic patterns.")
        return super()._extract_info_from_text(text)
