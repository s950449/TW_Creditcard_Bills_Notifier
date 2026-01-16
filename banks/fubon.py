import re
from banks.parser_base import BaseParser

class FubonParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific pattern for Fubon Bank
        print(f"[FubonParser] Attempting to extract from text (length: {len(text)})")
        
        # 1. Look for amount
        amount = None
        # Try finding non-zero amounts first
        amount_matches = re.findall(r"(?:應繳總額|應繳金額)\s*(?:NT\$)?\s*([\d,]+)\s*元", text)
        if amount_matches:
            for val_str in amount_matches:
                val = float(val_str.replace(",", ""))
                if val > 0:
                    amount = val
                    print(f"[FubonParser] Matched non-zero amount: {amount}")
                    break
            if not amount:
                amount = float(amount_matches[0].replace(",", ""))

        # 2. Look for due date with specific prefix
        due_date = None
        date_match = re.search(r"繳款期限\s*(\d{3}/\d{2}/\d{2})", text)
        if not date_match:
            # Fallback to any Minguo date if prefix search fails
            date_match = re.search(r"(\d{3}/\d{2}/\d{2})", text)
            
        if date_match:
            due_date_raw = date_match.group(1)
            parts = due_date_raw.split('/')
            due_date = f"{int(parts[0])+1911}/{parts[1]}/{parts[2]}"
            print(f"[FubonParser] Matched specific due date: {due_date}")

        if amount is not None and due_date:
            return {
                "bank": self.bank_name,
                "amount": amount,
                "due_date": due_date,
                "currency": "TWD"
            }
            
        print("[FubonParser] Specific extraction failed. Falling back to generic patterns.")
        return super()._extract_info_from_text(text)
