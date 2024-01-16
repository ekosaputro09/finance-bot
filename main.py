#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import gspread
import traceback
import pandas as pd
import dataframe_image as dfi
from telegram import *
from telegram.ext import *
from datetime import datetime
from dotenv import load_dotenv
import accounts
import budgets
load_dotenv()


gc = gspread.service_account(filename=os.getenv("CREDENTIALS_FILE"))
sh = gc.open_by_key(os.getenv("SPREADSHEET_KEY"))
worksheet = sh.worksheet(os.getenv("TRANSACTION_SHEET"))


def start_command(update, context):
    update.message.reply_text('Silahkan ketikkan sesuatu untuk memulai')


def help_command(update, context):
    file = open("help_text.txt")
    texts = file.read().splitlines()
    file.close()

    update.message.reply_text(('\n').join(text for text in texts))


def handle_message(update, context):
    text = str(update.message.text).lower()
    # response = responses.sample_responses(text)
    # update.message.reply_text(response)


def transactions(update, context):
    transaction = context.args[:]
    if len(transaction) < 1:
        update.message.reply_text("Please type:\n/input_trx %s \n\nexample:\n/input_trx %s"
                               % (('#').join(str(column) for column in json.loads(os.getenv("TRANSACTION_COLUMNS"))),
                                  "Pengeluaran#2022-01-01 10:00#Dompet Novi#50000#Makan Minum#Jajan#es krim"))
    else:
        transaction = (' ').join(str(i) for i in transaction).split('#')
        transaction[3] = int(transaction[3])
        last_row = worksheet.findall("2100-01-01 01:00")[0].row
        worksheet.update('A%s' % str(last_row), [transaction])
        # worksheet.append_row(transaction)
        try:
            # accounts.update_balance(transaction)
            # budgets.update_budget(transaction)
            update.message.reply_text("Transaction has been recorded")
        except:
            traceback.print_exc()
            update.message.reply_text("Something is Wrong. Please check!")


def search_transactions(update, context):
    queries = context.args[:]
    if len(queries) < 1:
        update.message.reply_text("Please type:\n/search_trx %s \n\nexample:\n/search_trx %s"
                               % ("column_name(Type,Date,Account,Amount,Category1,Category2,Notes)#query#last trx amount",
                                  "Account#Dompet Novi#10"))
    else:
        queries = (' ').join(i for i in queries).split('#')
        col_name, query, length = str(queries[0]), str(queries[1]), int(queries[2])

        trx = pd.DataFrame(worksheet.get_all_values(), columns=json.loads(os.getenv("TRANSACTION_COLUMNS")))
        trx.drop(labels=0, axis=0, inplace=True)
        trx.query("%s == @query" % col_name, inplace=True)
        trx['Date'] = trx['Date'].map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))
        trx.sort_values(by=['Date'], ascending=False, inplace=True)
        trx.reset_index(drop=True, inplace=True)
        if len(trx) >= length:
            trx = trx[:length]
        else:
            trx
        dfi.export(trx, os.getenv("TRANSACTION_PATH"), table_conversion="matplotlib")
        update.message.reply_photo(open(os.getenv("TRANSACTION_PATH"), "rb"))


def see_balance(update, context):
    accounts.see_balance()
    update.message.reply_photo(open(os.getenv("BALANCE_PATH"), "rb"))


def see_total_balance(update, context):
    grand_total = accounts.see_total_balance()
    update.message.reply_photo(open(os.getenv("TOTAL_BALANCE_PATH"), "rb"))
    update.message.reply_photo(open(os.getenv("TOTAL_BALANCE_PLOT_PATH"), "rb"))
    update.message.reply_text("Grand Total = Rp{:,}".format(int(grand_total)))


def list_category(update, context):
    budgets.list_category()
    update.message.reply_photo(open(os.getenv("CATEGORIES_PATH"), "rb"))


def invsout(update, context):
    budgets.invsout()
    update.message.reply_photo(open(os.getenv("INVSOUT_PATH"), "rb"))


def expense_details(update, context):
    period = context.args[:]
    if len(period) < 1:
        update.message.reply_text("Please type:\n/expense %s \n\nexample:\n/expense %s"
                               % ("month-year", "07-22"))
    else:
        date = "01-" + ('').join(period)
        period = '{0:%B} {0:%Y}'.format(datetime.strptime(date, '%d-%m-%y'))
        budgets.expense(period)
        update.message.reply_photo(open(os.getenv("REVENUES_PATH"), "rb"))
        update.message.reply_photo(open(os.getenv("EXPENSES_PATH"), "rb"))


def error_message(update, context):
    print(f"Update {update} caused error {context.error}")
    update.message.reply_text(f"Oops, there is an error: \n{context.error}")


def main():

    updater = Updater(os.getenv("BOT_API_KEY"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("input_trx", transactions))
    dp.add_handler(CommandHandler("search_trx", search_transactions))
    dp.add_handler(CommandHandler("balance", see_balance))
    dp.add_handler(CommandHandler("total_balance", see_total_balance))
    dp.add_handler(CommandHandler("categories", list_category))
    dp.add_handler(CommandHandler("invsout", invsout))
    dp.add_handler(CommandHandler("expense", expense_details))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error_message)

    updater.start_polling()
    updater.idle()


if __name__=="__main__":

    print("Bot has started ...")
    main()
