import constants as keys
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import Responses as R
# from io import BytesIO
# from PIL import Image
# import data as data
# import random


print("Bot started...")
def start_command(update, context):
    update.message.reply_text("Lo siento ahora mismo estoy en mantenimiento, inténtalo más tarde.")

def handle_message(update, context):

    update.message.reply_text("Lo siento ahora mismo estoy en mantenimiento, inténtalo más tarde.")

def handle_photo(update, context):
    update.message.reply_text("Lo siento ahora mismo estoy en mantenimiento, inténtalo más tarde.")
    
def error(update, context):
    print(f'Update {update} caused error {context.error}')

def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()


main()