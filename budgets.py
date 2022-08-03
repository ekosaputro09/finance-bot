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
worksheet = sh.worksheet(os.getenv("CATEGORY_SHEET"))


def update_budget(transaction):

    trx_columns = json.loads(os.getenv("TRANSACTION_COLUMNS"))
    trx_data = dict(zip(trx_columns, transaction))

    category1, category2 = trx_data['Category1'], trx_data['Category2']
    date = trx_data['Date']
    amount = trx_data['Amount']

    if trx_data['Type'] != "Transfer":
        subcat = worksheet.find(category2).row
        this_month = worksheet.find('{0:%B} {0:%Y}'.format(datetime.strptime(date, '%Y-%m-%d %H:%M'))).col
        worksheet.update_cell(subcat, this_month, int(worksheet.cell(subcat, this_month).value) + int(amount))


def list_category():

    categories = pd.DataFrame(worksheet.get(os.getenv("CATEGORY_DATARANGE")), columns=json.loads(os.getenv("CATEGORY_COLUMNS")))
    dfi.export(categories, os.getenv("CATEGORIES_PATH"))


def invsout():

    this_month_col = worksheet.find('{0:%B} {0:%Y}'.format(datetime.now())).col

    data = pd.DataFrame(worksheet.get_all_values())    
    data = data[[0,this_month_col-1]]
    data.drop(labels=0, axis=0, inplace=True)
    data.rename(columns={0:'Type', this_month_col-1:'Amount'}, inplace=True)
    data['Amount'] = data['Amount'].astype(int)

    invsout = data.groupby("Type").sum()
    invsout['Amount'] = invsout['Amount'].map("Rp{:,}".format)
    dfi.export(invsout, os.getenv("INVSOUT_PATH"))
