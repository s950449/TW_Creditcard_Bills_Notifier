import re
from banks.parser_base import BaseParser

class DBSParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific patterns for DBS Bank

        print(f"[DBSParser] Attempting to extract from text (length: {len(text)})")
        
        # 1. Look for amount
        amount = None
        amount_match = re.search(r"將自動扣繳\s*([\d,]+)\s*元", text)
        if amount_match:
            amount = float(amount_match.group(1).replace(",", ""))
            print(f"[DBSParser] Matched specific amount pattern: {amount}")

        # 2. Look for due date
        due_date = None

        date_match = re.search(r"繳交截止日[:：]\s*(\d{4})[年/](\d{2})[月/](\d{2})日?", text)
        if date_match:
            due_date = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}"
            print(f"[DBSParser] Matched specific due date: {due_date}")

        if amount is not None and due_date:
            return {
                "bank": self.bank_name,
                "amount": amount,
                "due_date": due_date,
                "currency": "TWD"
            }
            
        print("[DBSParser] Specific extraction failed. Falling back to generic patterns.")
        return super()._extract_info_from_text(text)
