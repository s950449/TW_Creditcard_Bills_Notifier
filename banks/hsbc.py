import re
from bs4 import BeautifulSoup
from banks.parser_base import BaseParser

class HSBCParser(BaseParser):
    def __init__(self, bank_name, password=None):
        super().__init__(bank_name, password)

    def parse_html_attachment(self, html_content):
        """
        Parse HSBC eBarCodeFullPay.html to extract amount.
        """
        # Decode content if it's bytes
        if isinstance(html_content, bytes):
            for enc in ['utf-8', 'big5', 'cp950']:
                try:
                    text = html_content.decode(enc)
                    break
                except:
                    continue
            else:
                text = html_content.decode('utf-8', errors='ignore')
        else:
            text = html_content

        print(f"[HSBCParser] Parsing HTML attachment (length: {len(text)})")
        soup = BeautifulSoup(text, 'html.parser')
        
        amount = None
        # Specific div class="amount" for HSBC
        amount_div = soup.find('div', class_='amount')
        if amount_div:
            amount_text = amount_div.get_text()
            amount_match = re.search(r"([\d,.]+)", amount_text)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
                print(f"[HSBCParser] Extracted amount from HTML: {amount}")

        return {
            "bank": self.bank_name,
            "amount": amount,
            "due_date": None, # Date will be fetched from PDF
            "currency": "TWD"
        }

    def _extract_info_from_text(self, text):
        # HSBC PDF search for due date
        # Specific pattern: 167 2026 01 14 , 716603XXXXX
        # (Amount Year Month Day)
        print(f"[HSBCParser] Searching for patterns in text (length: {len(text)})")
        # print(f"[HSBCParser] Raw text snippet: {text[:500]!r}")
        
        amount = None
        due_date = None
        
        # 1. Try the specific space-separated pattern
        # Handle potential commas or dots in amount, and be flexible with spaces
        space_pattern = r"([\d,.]+)\s+(\d{4})\s+(\d{2})\s+(\d{2})"
        match = re.search(space_pattern, text)
        if match:
            amount_str = match.group(1).replace(",", "")
            amount = float(amount_str)
            due_date = f"{match.group(2)}/{match.group(3)}/{match.group(4)}"
            print(f"[HSBCParser] Matched specific space pattern: Amount={amount}, Due={due_date}")
            return {
                "bank": self.bank_name,
                "amount": amount,
                "due_date": due_date,
                "currency": "TWD"
            }

        # 2. Fallback to other date patterns
        date_patterns = [
            r"繳款截止日[:：\s]*(\d{4}/\d{2}/\d{2})", # Priority to "繳款截止日"
            r"(?<!結帳日)[:：\s]*(\d{4}/\d{2}/\d{2})", # Avoid billing date if possible
            r"(\d{4}[年/]\d{2}[月/]\d{2}日?)"
        ]
        
        for p in date_patterns:
            match = re.search(p, text)
            if match:
                date_str = match.group(1).replace('年', '/').replace('月', '/').replace('日', '')
                due_date = date_str
                print(f"[HSBCParser] Found due date in PDF: {due_date}")
                break
        
        return {
            "bank": self.bank_name,
            "amount": None, # Amount will be fetched from HTML
            "due_date": due_date,
            "currency": "TWD"
        }
