#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import pytz
import json
import gspread
import pandas as pd
import dataframe_image as dfi
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


gc = gspread.service_account(filename=os.getenv("CREDENTIALS_FILE"))
sh = gc.open_by_key(os.getenv("SPREADSHEET_KEY"))
worksheet = sh.worksheet(os.getenv("ACCOUNT_SHEET"))
# rekening = pd.DataFrame(worksheet.get('A4:D22'), columns=json.loads(os.getenv("ACCOUNT_COLUMNS")))


def update_balance(transaction):

    trx_columns = json.loads(os.getenv("TRANSACTION_COLUMNS"))
    trx_data = dict(zip(trx_columns, transaction))

    if trx_data['Type'] == "Pemasukan":
        target_acc = trx_data['Account']
        amount = trx_data['Amount']

        balance = worksheet.find(target_acc)
        worksheet.update_cell(balance.row, balance.col+2, int(worksheet.cell(balance.row, balance.col+2).value) + int(amount))
    elif trx_data["Type"] == "Pengeluaran":
        source_acc = trx_data['Account']
        amount = trx_data['Amount']

        balance = worksheet.find(source_acc)
        worksheet.update_cell(balance.row, balance.col+2, int(worksheet.cell(balance.row, balance.col+2).value) - int(amount))
    elif trx_data['Type'] == "Transfer":
        amount = trx_data['Amount']

        source_acc = trx_data['Category1']
        source_balance = worksheet.find(source_acc)
        worksheet.update_cell(source_balance.row, source_balance.col+2, int(worksheet.cell(source_balance.row, source_balance.col+2).value) - int(amount))

        target_acc = trx_data['Category2']
        target_balance = worksheet.find(target_acc)
        worksheet.update_cell(target_balance.row, target_balance.col+2, int(worksheet.cell(target_balance.row, target_balance.col+2).value) + int(amount))


def see_balance():

    balance = pd.DataFrame(worksheet.get(os.getenv("ACCOUNT_DATARANGE")), columns=json.loads(os.getenv("ACCOUNT_COLUMNS")))
    balance.drop(columns=["Account Type", "Initial Balance"], axis=1, inplace=True)
    balance['Current Balance'] = ["Rp{:,}".format(int(nominal)) for nominal in balance['Current Balance']]
    dfi.export(balance, os.getenv("BALANCE_PATH"))
