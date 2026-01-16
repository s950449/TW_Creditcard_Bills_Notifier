import re
from banks.parser_base import BaseParser

class SCSBParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific pattern for Shanghai Bank (SCSB)
        text_norm = text.replace("新台幣", "新臺幣")
        

        amount_pattern = r"本期自動扣繳款為新[臺台]幣\s*([\d,]+)\s*元"
        match = re.search(amount_pattern, text_norm)
        
        if match:
            amount = float(match.group(1).replace(",", ""))
            
            # Search for specific Date pattern:
            date_pattern = r"將於\s*(\d{2,3}/\d{2}/\d{2})(?:自您指定之帳號)?"
            date_match = re.search(date_pattern, text_norm)
            
            if date_match:
                due_date_raw = date_match.group(1)
                parts = due_date_raw.split('/')
                due_date = f"{int(parts[0])+1911}/{parts[1]}/{parts[2]}"
                print(f"[SCSBParser] Matched specific date pattern. Amount: {amount}, Due: {due_date}")
                return {
                    "bank": self.bank_name,
                    "amount": amount,
                    "due_date": due_date,
                    "currency": "TWD"
                }
            
            # Fallback for date if specific pattern fails but amount was found
            result = super()._extract_info_from_text(text)
            if result:
                result['amount'] = amount
                return result
            else:
                # Manual date search as last resort if amount was found
                date_match = re.search(r"繳款截止日[:\s]*(\d{2,4}/\d{2}/\d{2})", text_norm)
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
        
        # Fallback to generic patterns
        return super()._extract_info_from_text(text)
