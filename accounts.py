#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import pytz
import json
import gspread
import pandas as pd
import dataframe_image as dfi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
    elif trx_data['Type'] == "Pengeluaran":
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
    balance.drop(columns=['AccountType', 'InitialBalance', 'Income', 'InTransfer', 'AllIncomes', 'Expense', 'OutTransfer', 'AllExpenses'], axis=1, inplace=True)
    balance['CurrentBalance'] = balance['CurrentBalance'].map(lambda x: "Rp{:,}".format(int(x)))
    dfi.export(balance, os.getenv("BALANCE_PATH"), table_conversion="matplotlib")


def see_total_balance():
    balance = pd.DataFrame(worksheet.get(os.getenv("ACCOUNT_DATARANGE")), columns=json.loads(os.getenv("ACCOUNT_COLUMNS")))
    balance.rename(columns={'CurrentBalance': 'TotalBalance'}, inplace=True)

    balance['TotalBalance'] = balance['TotalBalance'].astype(int)
    total_balance = balance.groupby("AccountType").sum()[['TotalBalance']]
    total_balance["TotalBalance"] = total_balance["TotalBalance"].map(lambda x: x*(-1) if x < 0 else x*1)
    grand_total = total_balance['TotalBalance'].sum() - total_balance['TotalBalance']['KARTU KREDIT']
    total_balance['TotalBalance (%)'] = total_balance['TotalBalance'].map(lambda x: x/grand_total)

    total_balance.plot.pie(y='TotalBalance', figsize=(5,5), autopct='%1.0f%%', startangle=60, explode=(0.05, 0.05, 0.05, 0.05))
    plt.savefig(os.getenv("TOTAL_BALANCE_PLOT_PATH"))

    total_balance['TotalBalance'] = total_balance['TotalBalance'].map("Rp{:,}".format)
    total_balance['TotalBalance (%)'] = total_balance['TotalBalance (%)'].map("{:.2%}".format)
    dfi.export(total_balance, os.getenv("TOTAL_BALANCE_PATH"), table_conversion="matplotlib")

    return grand_total
