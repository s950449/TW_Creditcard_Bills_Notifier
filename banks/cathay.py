import re
from banks.parser_base import BaseParser

class CathayParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific pattern for Cathay Bank (國泰世華)
        # Search for amount: 本期應繳總金額 [金額]
        amount_pattern = r"本期應繳總金額\s*([\d,]+)"
        match = re.search(amount_pattern, text)
        
        if match:
            amount = float(match.group(1).replace(",", ""))
            print(f"[CathayParser] Matched specific amount pattern: {amount}")
            
            result = super()._extract_info_from_text(text)
            if result:
                result['amount'] = amount
                return result
            else:
                # Basic date fallback
                date_match = re.search(r"繳款截止日[:\s]*(\d{2,4}/\d{2}/\d{2})", text)
                if date_match:
                    due_date_raw = date_match.group(1)
                    parts = due_date_raw.split('/')
                    if len(parts[0]) <= 3: # Minguo
                        due_date = f"{int(parts[0])+1911}/{parts[1]}/{parts[2]}"
                    else:
                        due_date = due_date_raw
                    
                    return {
                        "bank": self.bank_name,
                        "amount": amount,
                        "due_date": due_date,
                        "currency": "TWD"
                    }
        
        return super()._extract_info_from_text(text)
