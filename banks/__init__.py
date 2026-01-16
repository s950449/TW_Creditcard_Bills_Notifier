from banks.parser_base import BaseParser
from banks.sinopac import SinoPacParser
from banks.scsb import SCSBParser
from banks.taishin import TaishinParser
from banks.cathay import CathayParser
from banks.ctbc import CTBCParser
from banks.esun import ESUNParser
from banks.fubon import FubonParser
from banks.dbs import DBSParser
from banks.union import UnionParser
from banks.hsbc import HSBCParser
from banks.huanan import HuaNanParser
from config import Config

class GenericBankParser(BaseParser):
    def __init__(self, bank_name, password):
        super().__init__(bank_name, password)

class ParserFactory:
    BANKS = {
        "Taishin": {
            "keyword": "台新 信用卡 電子帳單", 
            "name_tw": "台新銀行",
            "sender": "webmaster@bhurecv.taishinbank.com.tw",
            "pdf_name": "TSB_Creditcard_Estatement"
        },
        "Cathay": {
            "keyword": "國泰世華 信用卡 帳單", 
            "name_tw": "國泰世華",
            "sender": "service@pxbillrc01.cathaybk.com.tw",
            "pdf_name": "信用卡電子帳單消費明細"
        },
        "CTBC": {
            "keyword": "中國信託 信用卡 電子帳單", 
            "name_tw": "中國信託",
            "sender": "ebill@estats.ctbcbank.com",
            "pdf_name": "CTBC_card_Estatement"
        },
        "ESUN": {
            "keyword": "玉山銀行 信用卡 電子帳單", 
            "name_tw": "玉山銀行",
            "sender": "estatement@esunbank.com.tw",
            "pdf_name": "ESUN_Estatement"
        },
        "SinoPac": {
            "keyword": "永豐銀行信用卡", 
            "name_tw": "永豐銀行",
            "sender": "ebillservice@newebill.banksinopac.com.tw",
            "pdf_name": "永豐銀行信用卡帳單"
        },
        "HuaNan": {
            "keyword": "華南銀行 信用卡 電子帳單", 
            "name_tw": "華南銀行",
            "sender": "service@ebmail.hncb.com.tw",
            "pdf_name": "CREDITA"
        },
        "HSBC_LivePlus": {
            "keyword": "滙豐Live+現金回饋卡信用卡帳單", 
            "name_tw": "滙豐Live+",
            "sender": "cards@estatements.hsbc.com.tw",
            "pdf_name": "eStatement"
        },
        "HSBC_Cashback_Titanium": {
            "keyword": "滙豐匯鑽卡信用卡帳單", 
            "name_tw": "滙豐匯鑽",
            "sender": "cards@estatements.hsbc.com.tw",
            "pdf_name": "eStatement"
        },
        "HSBC_TravelOne": {
            "keyword": "滙豐旅人輕旅卡信用卡帳單", 
            "name_tw": "滙豐旅人",
            "sender": "cards@estatements.hsbc.com.tw",
            "pdf_name": "eStatement"
        },
        "Union": {
            "keyword": "聯邦銀行 信用卡 電子帳單", 
            "name_tw": "聯邦銀行",
            "sender": "estatement@ebillv2.card.ubot.com.tw",
            "pdf_name": "UBOT_Estatement"
        },
        "Fubon": {
            "keyword": "台北富邦銀行 信用卡 帳單", 
            "name_tw": "台北富邦",
            "sender": "rs@cf.taipeifubon.com.tw",
            "pdf_name": "信用卡帳單"
        },
        "DBS": {
            "keyword": "星展銀行(台灣)信用卡電子對帳單", 
            "name_tw": "星展銀行",
            "sender": "eservicetw@dbs.com",
            "pdf_name": "CBGCC-DAILYSTMT"
        },
        "SCSB": {
            "keyword": "上海商銀信用卡對帳單", 
            "name_tw": "上海商銀",
            "sender": "service1@scsb.com.tw",
            "pdf_name": "上海商銀信用卡對帳單"
        },
    }

    @staticmethod
    def get_parser(bank_id):
        bank_info = ParserFactory.BANKS.get(bank_id)
        if bank_info:
            password = Config.get_bank_password(bank_id)
            if bank_id == "SinoPac":
                return SinoPacParser(bank_info["name_tw"], password)
            if bank_id == "SCSB":
                return SCSBParser(bank_info["name_tw"], password)
            if bank_id == "Taishin":
                return TaishinParser(bank_info["name_tw"], password)
            if bank_id == "Cathay":
                return CathayParser(bank_info["name_tw"], password)
            if bank_id == "CTBC":
                return CTBCParser(bank_info["name_tw"], password)
            if bank_id == "ESUN":
                return ESUNParser(bank_info["name_tw"], password)
            if bank_id == "Fubon":
                return FubonParser(bank_info["name_tw"], password)
            if bank_id == "DBS":
                return DBSParser(bank_info["name_tw"], password)
            if bank_id == "Union":
                return UnionParser(bank_info["name_tw"], password)
            if bank_id == "HuaNan":
                return HuaNanParser(bank_info["name_tw"], password)
            if bank_id.startswith("HSBC_"):
                return HSBCParser(bank_info["name_tw"], password)
            return GenericBankParser(bank_info["name_tw"], password)
        return None

    @staticmethod
    def get_all_bank_info():
        return ParserFactory.BANKS
