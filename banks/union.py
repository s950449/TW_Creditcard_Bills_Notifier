import re
from banks.parser_base import BaseParser

class UnionParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def _extract_info_from_text(self, text):
        # Specific pattern for Union Bank
        # Amount: 總計 638
        print(f"[UnionParser] Attempting to extract from text (length: {len(text)})")
        
        # 1. Look for amount using "總計"
        amount = None
        # Pattern: 總計 638 or 總計: 638
        amount_match = re.search(r"總計\s*[:：]?\s*([\d,]+)", text)
        if amount_match:
            amount = float(amount_match.group(1).replace(",", ""))
            print(f"[UnionParser] Matched specific amount pattern: {amount}")

        if amount is not None:
            # Use BaseParser to find due date and other info
            result = super()._extract_info_from_text(text)
            if result:
                result['amount'] = amount
                return result
            else:
                # Basic fallback if due date not found by BaseParser
                return {
                    "bank": self.bank_name,
                    "amount": amount,
                    "due_date": None,
                    "currency": "TWD"
                }
            
        print("[UnionParser] Specific extraction failed. Falling back to generic patterns.")
        return super()._extract_info_from_text(text)
