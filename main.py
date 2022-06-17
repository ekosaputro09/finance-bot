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
    update.message.reply_text("Please type: \n\input_trx %s" 
                           % ('#').join(str(column) for column in json.loads(os.getenv("TRANSACTION_COLUMNS"))))


def handle_message(update, context):
    text = str(update.message.text).lower()
    # response = responses.sample_responses(text)
    # update.message.reply_text(response)


def transactions(update, context):
    transaction = context.args[:]
    if len(transaction) < 1:
        update.message.reply_text("Wrong format! Please type: \n\input_trx %s"
                               % ('#').join(str(column) for column in json.loads(os.getenv("TRANSACTION_COLUMNS"))))
    else:
        transaction = (' ').join(str(i) for i in transaction).split('#')
        worksheet.append_row(transaction)
        accounts.update_balance(transaction)
        update.message.reply_text("Transaction has been recorded")


def error_message(update, context):
    print(f"Update {update} caused error {context.error}")


def main():

    updater = Updater(os.getenv("BOT_API_KEY"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("input_trx", transactions))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error_message)

    updater.start_polling()
    updater.idle()


if __name__=="__main__":

    print("Bot has started ...")
    main()
