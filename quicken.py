import xml.etree.ElementTree as ET
from transaction_db import Transaction
from decimal import Decimal
from datetime import datetime

def import_quicken_transactions(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    transactions = []

    for stmttrn in root.findall(".//STMTTRN"):

        trans = Transaction()

        date_str = date_str = stmttrn.findtext("DTPOSTED")
        # Strip the time zone offset if present
        date_str = date_str.split(".")[0]

        trans.id = None
        trans.vendor = str(stmttrn.findtext("NAME"))
        trans.amount = Decimal(str(stmttrn.findtext("TRNAMT")))
        trans.category = "uncategorized"
        trans.memo = str(stmttrn.findtext("MEMO"))
        trans.date = datetime.strptime(date_str, "%Y%m%d%H%M%S")

        transactions.append(trans)

    return transactions
