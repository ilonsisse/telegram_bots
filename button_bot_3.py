import config
import telebot
from telebot import types
import random


bot = telebot.TeleBot(config.token)

with open('facts.txt', 'r', encoding='UTF-8') as facts:
    facts = facts.read().split('\n')

with open('thinks.txt', 'r', encoding='UTF-8') as thinks:
    thinks = thinks.read().split('\n')

@bot.message_handler(commands=["start"])
def start(m, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Новость")
    item2 = types.KeyboardButton("Афоризм")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(m.chat.id, 'Нажми: \nНовость - для получения сегодняшних новостей'
                                '\nАфоризм — для получения лучших афоризмов всех времён',
    reply_markup = markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Новость':
        answer = random.choice(facts)
    elif message.text.strip() == 'Афоризм':
        answer = random.choice(thinks)

    bot.send_message(message.chat.id, answer)

bot.polling(none_stop=True, interval=0)