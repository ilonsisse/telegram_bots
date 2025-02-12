import config
import telebot
import time


bot = telebot.TeleBot(config.token)
CHANNEL_NAME = '@bbi2202_bot_channel'

with open('jokes.txt', 'r', encoding='UTF-8') as file:
    jokes = file.read().split('\n')

for joke in jokes:
    bot.send_message(CHANNEL_NAME, joke)
    time.sleep(30)

bot.send_message(CHANNEL_NAME, 'Шутки кончились.')