import pikepdf
import re
import io
import pdfplumber
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class BaseParser(ABC):
    def __init__(self, bank_name, password=None):
        self.bank_name = bank_name
        self.password = password

    def parse_email(self, msg_body, html=True):
        if html:
            soup = BeautifulSoup(msg_body, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
        else:
            text = msg_body
        
        return self._extract_info_from_text(text)

    def parse_pdf(self, pdf_content):
        """Decrypts PDF and extracts text using pdfplumber."""
        from config import Config
        # Generate password candidates
        passwords = [self.password] # self.password is Config.ID_NUMBER by default
        
        # Identity variations
        if self.password and len(self.password) >= 6:
            passwords.append(self.password.upper())
            passwords.append(self.password.lower())
            
            id_last_2 = self.password[-2:]
            id_last_4 = self.password[-4:]
            id_last_6 = self.password[-6:]
            
            passwords.append(id_last_6) # SCSB style
            passwords.append(id_last_4)
            passwords.append(id_last_2)

        # Birthday variations
        if Config.BIRTHDAY:
            # If YYYYMMDD, get MMDD
            mmdd = Config.BIRTHDAY[-4:] if len(Config.BIRTHDAY) >= 4 else Config.BIRTHDAY
            passwords.append(Config.BIRTHDAY)
            passwords.append(mmdd)
            
            if self.password and len(self.password) >= 4:
                id_last_2 = self.password[-2:]
                id_last_4 = self.password[-4:]
                
                passwords.append(f"{id_last_2}{mmdd}") # Taishin style
                passwords.append(f"{id_last_4}{mmdd}") # DBS style
                
                # Reverse variations just in case
                passwords.append(f"{mmdd}{id_last_2}")
                passwords.append(f"{mmdd}{id_last_4}")

        # Remove duplicates while preserving order
        passwords = [p for p in dict.fromkeys(passwords) if p]

        decrypted_pdf = None
        for pwd in passwords:
            try:
                with pikepdf.open(io.BytesIO(pdf_content), password=pwd) as pdf:
                    out_pdf = io.BytesIO()
                    pdf.save(out_pdf)
                    decrypted_pdf = out_pdf
                    # print(f"[{self.bank_name}] Decrypted with password variation.")
                    break
            except pikepdf.PasswordError:
                continue
            except Exception as e:
                print(f"[{self.bank_name}] PDF Error during decryption: {e}")
                break

        if not decrypted_pdf:
            print(f"[{self.bank_name}] PDF Error: All password variations failed.")
            return None

        try:
            decrypted_pdf.seek(0)
            text = ""
            with pdfplumber.open(decrypted_pdf) as plum:
                for page in plum.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if not text.strip():
                 print(f"[{self.bank_name}] Warning: pdfplumber extracted empty text.")
            return self._extract_info_from_text(text)
        except Exception as e:
            print(f"[{self.bank_name}] PDF Extract Error: {e}")
            return None

    def _extract_info_from_text(self, text):
        """Generic regex extraction for common bill formats."""
        # Replace common OCR errors or spacing
        text = re.sub(r'\s+', ' ', text)
        
        amount = None
        due_date = None
        
        # Patterns for Amount
        amount_patterns = [
            r"本期應繳總額[:\s]*NT\$?\s*([\d,]+)",
            r"應繳總額[:\s]*NT\$?\s*([\d,]+)",
            r"本期應繳金額[:\s]*NT\$?\s*([\d,]+)",
            r"應繳總金額[:\s]*NT\$?\s*([\d,]+)",
            r"最低應繳金額[:\s]*NT\$?\s*([\d,]+)",
            r"應繳金額[:\s]*NT\$?\s*([\d,]+)",
            r"應付總額[:\s]*NT\$?\s*([\d,]+)",
            r"應繳款[:\s]*NT\$?\s*([\d,]+)",
            r"New Balance[:\s]*\$?\s*([\d,.]+)",
            r"Payment Amount[:\s]*\$?\s*([\d,.]+)",
            r"Total[:\s]*NT\$?\s*([\d,]+)",
            r"TWD ([\d,]+)",
            r"NT\$ ([\d,]+)",
            r"臺幣 ([\d,]+)",
            r"台幣[\$ ]+([\d,]+)",
            r"Balance[:\s]*\$?\s*([\d,.]+)",
            r"(\d{2,4}/\d{2}/\d{2})\s+([\d,]+)" # Date followed by amount
        ]
        
        # Patterns for Due Date
        date_patterns = [
            r"繳款截止日[:\s]*(\d{4}/\d{2}/\d{2})",
            r"截止日期[:\s]*(\d{4}/\d{2}/\d{2})",
            r"Due Date[:\s]*(\d{4}/\d{2}/\d{2})",
            r"繳款截止(日|日期)[:\s]*(\d{2,4}/\d{2}/\d{2})",
            r"(\d{4}/\d{2}/\d{2})",
            r"(\d{3}/\d{2}/\d{2})"
        ]

        for p in amount_patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                amount_str = match.groups()[-1].replace(",", "").replace(" ", "")
                # Handle potential decimal part
                try:
                    amount = float(amount_str.split('.')[0])
                    break
                except ValueError:
                    continue
        
        for p in date_patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                due_date_raw = match.groups()[-1]
                parts = due_date_raw.split('/')
                if len(parts[0]) <= 3: # Minguo
                    due_date = f"{int(parts[0])+1911}/{parts[1]}/{parts[2]}"
                else:
                    due_date = due_date_raw
                break
        
        if amount is not None and due_date:
            return {
                "bank": self.bank_name,
                "amount": amount,
                "due_date": due_date,
                "currency": "TWD"
            }
        
        return None
    def parse_html_attachment(self, html_content):
        """
        To be overridden by bank-specific parsers
        """
        return None
