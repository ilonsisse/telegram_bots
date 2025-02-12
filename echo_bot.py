import config
import telebot


bot = telebot.TeleBot(config.token)

# Функция, обрабатывающая /start.
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Бот запущен. Начните общение с ним.')

# Получение сообщений.
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, 'Вы написали: ' + message.text)

# Запуск бота.
bot.polling(none_stop=True, interval=0)
