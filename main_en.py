import constants as keys
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import Responses as R
from io import BytesIO
from PIL import Image
import data as data
import random
import time


print("Bot started...")

def start_command(update, context):
    chat_info = update['message']['chat']
    name = chat_info['first_name']
    update.message.reply_text(f"Hi {name}, I'm a facial verification bot 🤖")
    update.message.reply_text("To start please send:\
        \n\nA selfie 🤳, preferably without glasses ❌🤓 without a face mask ❌😷 with a neutral expression and face aligned with the camera 🙂 \
        \n\nA picture of the front side of your ID 📇 \
        \n\nYou can also try comparing other types of pictures in more unconstrained environments.\
        \n\nNOTICE 🚨 YOUR PICTURES WON'T BE STORED OR SEEN BY ANYBODY.")
    update.message.reply_text('/start')

def help_command(update, context):
    update.message.reply_text('Look for help on google')

def handle_message(update, context):
    text = str(update.message.text).lower()
    chat_info = update['message']['chat']

    response = R.sample_responses(text, chat_info)
    update.message.reply_text(response)
    
def handle_photo(update, context):
    # Get chat info
    chat_info = update['message']['chat']
    # Get photo file
    photo_file = context.bot.get_file(update.message.photo[-1].file_id)
    # Text reply
    update.message.reply_text(random.choice(['Nice picture, let me process it ⏳', 'Thanks! give me a sec ⏳', 'Great! wait while I process it ⏳', 'Wow! let me take a look ⏳', 'Amazing! just a moment ⏳']))
    # get reply for photo
    response = R.photo_responses(photo_file, chat_info)
    update.message.reply_text(response)
    if "Okay, let's start verifying..." in response:
        time.sleep(1)
        result = data.verify_data(chat_info)
        if float(result) >= 50:
            update.message.reply_text(f'{result}% similarity ✅')
        if float(result) < 50:
            update.message.reply_text(f'{result}% similarity ❌')
        if float(result) > 99.6:
            update.message.reply_text('Looks like you sent the same pic twice 🤨')

        update.message.reply_text(f'Were the people in the pictures the same person?\n\nReply "Y" if yes or "N" if no\n\n')

def error(update, context):
    print(f'Update {update} caused error {context.error}')

def main():
    #keys.API_KEY
    
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start_command))
    # dp.add_handler(CommandHandler('help', help_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


main()