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
    balance['Current Balance'] = balance['Current Balance'].map(lambda x: "Rp{:,}".format(int(x)))
    dfi.export(balance, os.getenv("BALANCE_PATH"))


def see_total_balance():
    balance = pd.DataFrame(worksheet.get(os.getenv("ACCOUNT_DATARANGE")), columns=json.loads(os.getenv("ACCOUNT_COLUMNS")))
    balance.rename(columns={'Current Balance': 'Total Balance'}, inplace=True)

    balance['Total Balance'] = balance['Total Balance'].astype(int)
    total_balance = balance.groupby("Account Type").sum()[['Total Balance']]
    grand_total = total_balance['Total Balance'].sum()
    total_balance['Total Balance (%)'] = total_balance['Total Balance'].map(lambda x: x/grand_total)
 
    total_balance['Total Balance'] = total_balance['Total Balance'].map("Rp{:,}".format)
    total_balance['Total Balance (%)'] = total_balance['Total Balance (%)'].map("{:.2%}".format)
    dfi.export(total_balance, os.getenv("TOTAL_BALANCE_PATH"))

    return grand_total
