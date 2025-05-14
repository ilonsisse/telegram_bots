from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from google.cloud import dialogflow
from google.api_core.exceptions import InvalidArgument
import os
from google.colab import drive
from telegram.ext.callbackcontext import CallbackContext

# Монтирование Google Диска
drive.mount('/content/gdrive')

# Укажи правильный путь к своему .json-файлу с ключами
credential_path = "/content/gdrive/MyDrive/credentials.json"  # <= ВСТАВЬ СВОЙ ПУТЬ К ФАЙЛУ
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# Укажи свой ID проекта Dialogflow
DIALOGFLOW_PROJECT_ID = 'your-dialogflow-project-id'  # <= ВСТАВЬ СВОЙ ID ПРОЕКТА
DIALOGFLOW_LANGUAGE_CODE = 'en'
SESSION_ID = 'current-user-id'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! I am a bot with Google Dialogflow")

def echo(update: Update, context: CallbackContext):
    text_to_be_analyzed = update.message.text
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

    text_input = dialogflow.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
        update.message.reply_text(response.query_result.fulfillment_text)
    except InvalidArgument:
        update.message.reply_text('Invalid Argument error occurred.')
    except Exception as e:
        update.message.reply_text(f'Error: {e}')

def main():
    # Укажи свой токен Telegram-бота
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # <= ВСТАВЬ СВОЙ ТОКЕН
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()