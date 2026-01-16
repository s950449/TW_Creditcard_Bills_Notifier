import re
from banks.parser_base import BaseParser

class ESUNParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific pattern for E.SUN Bank
        print(f"[ESUNParser] Attempting to extract from text (length: {len(text)})")
        
        # 1. Primary: TWD pattern (usually in the summary table)
        # Handle potential newlines/spaces between label and amount
        twd_pattern = r"本期應繳總金額[：:]?\s*TWD\s*([\d,.]+)"
        matches = re.findall(twd_pattern, text, re.IGNORECASE | re.DOTALL)
        
        amount = None
        if matches:
            # Pick the first non-zero match, or the last match if all are same
            for m in matches:
                val = float(m.replace(",", ""))
                if val > 0:
                    amount = val
                    print(f"[ESUNParser] Matched non-zero TWD pattern: {amount}")
                    break
            if amount is None:
                amount = float(matches[0].replace(",", ""))
                print(f"[ESUNParser] Matched TWD pattern (zero or fallback): {amount}")

        # 2. Secondary: Sentence pattern (from previous iteration)
        if amount is None:
            sentence_pattern = r"※本行將於\s*(\d{1,2})日\s*依您的約定帳號:.*?扣款\s*([\d,]+)\s*元"
            match = re.search(sentence_pattern, text, re.DOTALL)
            if match:
                amount = float(match.group(2).replace(",", ""))
                print(f"[ESUNParser] Matched sentence pattern. Amount: {amount}")

        # 3. Tertiary: Table-based pattern (generic columns skip)
        if amount is None:
            table_pattern = r"本期應繳總金額[：:]?\s*(?:[^\s]+\s+){3,6}TWD\s+([\d,.]+)"
            match = re.search(table_pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                amount = float(match.group(1).replace(",", ""))
                print(f"[ESUNParser] Matched table column skip pattern: {amount}")

        if amount is not None:
            # 1. Try to find due date near "繳款截止日" first (Highest priority)
            date_patterns = [
                r"繳款截止日[:\s：]*(\d{2,4}/\d{2}/\d{2})",
                r"(\d{3}/\d{2}/\d{2})" # Specific 3-digit year pattern for Minguo
            ]
            
            due_date = None
            for p in date_patterns:
                date_match = re.search(p, text)
                if date_match:
                    due_date_raw = date_match.group(1)
                    parts = due_date_raw.split('/')
                    if len(parts[0]) <= 3: # Minguo
                        due_date = f"{int(parts[0])+1911}/{parts[1]}/{parts[2]}"
                    else:
                        due_date = due_date_raw
                    print(f"[ESUNParser] Matched specific due date: {due_date}")
                    break

            if amount is not None and due_date:
                return {
                    "bank": self.bank_name,
                    "amount": amount,
                    "due_date": due_date,
                    "currency": "TWD"
                }

            # Fallback to BaseParser if specific date search failed
            result = super()._extract_info_from_text(text)
            if result:
                result['amount'] = amount
                return result
        
        print(f"[ESUNParser] Specific extraction failed. Falling back to generic patterns.")
        return super()._extract_info_from_text(text)
