#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import gspread
from telegram import *
from telegram.ext import *
from dotenv import load_dotenv
import accounts
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
        update.message.reply_text("Please type:\n\input_trx %s \n\nexample:\n\input_trx %s"
                               % (('#').join(str(column) for column in json.loads(os.getenv("TRANSACTION_COLUMNS"))),
                                  "Pemasukan#2022-01-01 10:00#Bank Mandiri#10000000#Gaji#Gaji Eko#Gaji Januari Eko"))
    else:
        transaction = (' ').join(str(i) for i in transaction).split('#')
        worksheet.append_row(transaction)
        accounts.update_balance(transaction)
        update.message.reply_text("Transaction has been recorded")


def see_balance(update, context):
    accounts.see_balance()
    update.message.reply_photo(open(os.getenv("BALANCE_PATH"), "rb"))


def list_category(update, context):
    accounts.list_category()
    update.message.reply_photo(open(os.getenv("CATEGORIES_PATH"), "rb"))


def error_message(update, context):
    print(f"Update {update} caused error {context.error}")


def main():

    updater = Updater(os.getenv("BOT_API_KEY"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("input_trx", transactions))
    dp.add_handler(CommandHandler("balance", see_balance))
    dp.add_handler(CommandHandler("categories", list_category))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error_message)

    updater.start_polling()
    updater.idle()


if __name__=="__main__":

    print("Bot has started ...")
    main()
