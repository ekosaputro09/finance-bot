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
    dfi.export(categories, os.getenv("CATEGORIES_PATH"), table_conversion="matplotlib")


def invsout():

    months = json.loads(os.getenv("MONTHS"))
    years = json.loads(os.getenv("YEARS"))

    data = pd.DataFrame(worksheet.get_all_values())
    data.columns=data.iloc[2].tolist()
    data.drop(labels=[0,1,2], axis=0, inplace=True)
    data_columns = list(set(data.columns))

    column_name = [month + " " + year for month in months for year in years]
    column_name = [column for column in column_name if column in data_columns]

    data = data[['Type'] + column_name]
    data[column_name] = data[column_name].astype(int)

    invsout = data.groupby("Type").sum()
    for column in column_name:
        invsout[column] = invsout[column].map("Rp{:,}".format)
    dfi.export(invsout, os.getenv("INVSOUT_PATH"), table_conversion="matplotlib")


def expense(period):

    data = pd.DataFrame(worksheet.get_all_values())
    data.columns=data.iloc[2].tolist()
    data.drop(labels=[0,1,2], axis=0, inplace=True)

    data = data[json.loads(os.getenv("CATEGORY_COLUMNS")) + [period]]
    data[period] = data[period].astype(int)

    expenses = data[data['Type'] == "Pengeluaran"]
    revenues = data[data['Type'] == "Pemasukan"]

    expenses.sort_values(by=period, ascending=False, inplace=True)
    expenses.reset_index(drop=True, inplace=True)
    expenses.drop(columns=["Type"], inplace=True)
    expenses[period] = expenses[period].map("Rp{:,}".format)
    dfi.export(expenses, os.getenv("EXPENSES_PATH"), table_conversion="matplotlib")

    revenues.sort_values(by=period, ascending=False, inplace=True)
    revenues.reset_index(drop=True, inplace=True)
    revenues.drop(columns=["Type"], inplace=True)
    revenues[period] = revenues[period].map("Rp{:,}".format)
    dfi.export(revenues, os.getenv("REVENUES_PATH"), table_conversion="matplotlib")
