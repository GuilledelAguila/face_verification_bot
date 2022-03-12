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
    update.message.reply_text(f'Hola {name}, soy el Bot de verificación facial 🤖')
    update.message.reply_text('Para empezar a verificar manda:\
        \n\nUn selfie 🤳, a ser posible sin gafas ❌🤓 sin mascarilla ❌😷 expresion neutral y cara alineada con la camara 🙂 \
        \n\nUna foto de la parte frontal de tu DNI 📇 asegurate de que hay pocos reflejos en el documento. \
        \n\nSi quieres también puedes probar con fotos que no sean de DNI en ambientes mas informales.\
        \n\nAVISO 🚨 Tus fotos serán usadas únicamente para la verificación e inmediatamente ELIMINADAS. Tus fotos NO serán almacenadas NI VISTAS por NADIE.')
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
    update.message.reply_text(random.choice(['Bonita foto, vamos a procesarla ⏳', 'Muchas gracias, dame un momento ⏳', 'Genial, espera mientras la proceso ⏳', 'Wow! Dejame ver ⏳', 'Increible! dame un segundo ⏳']))
    # get reply for photo
    response = R.photo_responses(photo_file, chat_info)
    update.message.reply_text(response)
    if 'Todo correcto, verificando...' in response:
        time.sleep(1)
        result = data.verify_data(chat_info)
        if float(result) >= 50:
            update.message.reply_text(f'Resultado: {result}% de similitud ✅')
        if float(result) < 50:
            update.message.reply_text(f'Resultado: {result}% de similitud ❌')
        if float(result) > 99.6:
            update.message.reply_text('Parecen 2 fotos iguales 🤨')

        update.message.reply_text(f'¿Ha sido correcto el resultado de la verificación?\n\nResponde "S" en caso afirmativo o "N" en caso contrario\n\n')

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