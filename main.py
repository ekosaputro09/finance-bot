#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import gspread
from telegram import *
from telegram.ext import *
from dotenv import load_dotenv
# import responses
load_dotenv()


gc = gspread.service_account(filename=os.getenv("CREDENTIALS_FILE"))
sh = gc.open_by_key(os.getenv("SPREADSHEET_KEY"))
worksheet = sh.worksheet(os.getenv("SHEET_NAME"))


def start_command(update, context):
    update.message.reply_text('Silahkan ketikkan sesuatu untuk memulai')


def help_command(update, context):
    update.message.reply_text("Please type: \
                              \n\catat_keuangan Type#Date#Account#Amount#Notes#Category")


def handle_message(update, context):
    text = str(update.message.text).lower()
    # response = responses.sample_responses(text)
    # update.message.reply_text(response)


def catat_keuangan(update, context):
    note = context.args[:]
    if len(note) < 1:
        update.message.reply_text("Wrong format! Please type: \
                                  \n\catat_keuangan Type#Date#Account#Amount#Notes#Category")
    else:
        note = (' ').join(str(i) for i in note)
        notes = note.split('#')
        worksheet.append_row(notes)
        # responses.logic(notes)
        update.message.reply_text("sudah tercatat")


def error_message(update, context):
    print(f"Update {update} caused error {context.error}")


def main():

    updater = Updater(os.getenv("BOT_API_KEY"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("catat_keuangan", catat_keuangan))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error_message)

    updater.start_polling()
    updater.idle()


if __name__=="__main__":

    print("Bot has started ...")
    main()
