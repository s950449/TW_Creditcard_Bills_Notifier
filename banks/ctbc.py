import re
from banks.parser_base import BaseParser

class CTBCParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific pattern for CTBC Bank
        amount_pattern = r"\+\s*([\d,]+)"
        match = re.search(amount_pattern, text)
        
        if match:
            amount = float(match.group(1).replace(",", ""))
            print(f"[CTBCParser] Matched '+' amount pattern: {amount}")
            
            # Use BaseParser to find due date and other info
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
        
        # Fallback to generic patterns
        return super()._extract_info_from_text(text)
