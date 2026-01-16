import re
from datetime import datetime
from banks.parser_base import BaseParser

class HuaNanParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # HuaNan Bank pattern:
        # 金額 4,132 元,請於 11月07日 之前檢視帳戶餘額以利扣款
        print(f"[HuaNanParser] Attempting to extract from text (length: {len(text)})")
        
        # 1. Primary pattern from user
        # Handle potential spaces and commas
        pattern = r"金額\s*([\d,]+)\s*元,請於\s*(\d{1,2})月(\d{1,2})日\s*之前"
        match = re.search(pattern, text)
        
        if match:
            amount = float(match.group(1).replace(",", ""))
            month = match.group(2).zfill(2)
            day = match.group(3).zfill(2)
            
            # Since HuaNan only provides MM/DD, we assume the year from context.
            # Usually the current year, but if we are in January and the bill is for December, 
            # it might be tricky. However, most bills are current year.
            year = datetime.now().year
            due_date = f"{year}/{month}/{day}"
            
            print(f"[HuaNanParser] Matched specific pattern: Amount={amount}, Due={due_date}")
            return {
                "bank": self.bank_name,
                "amount": amount,
                "due_date": due_date,
                "currency": "TWD"
            }
            
        print("[HuaNanParser] Specific extraction failed. Falling back to generic patterns.")
        return super()._extract_info_from_text(text)
