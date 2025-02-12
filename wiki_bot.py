import config
import telebot
import wikipedia
import re


bot = telebot.TeleBot(config.token)
wikipedia.set_lang('ru')


def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext = ny.content[:1000] # Получаем первую тысячу символов
        wikimas = wikitext.split('.') # Разбиваем, считая точку разделителем
        wikimas = wikimas[:-1] # Отбрасываем всё после последней точки
        wikitext2 = '' # Создаем пустую переменную для текста
        for x in wikimas: # Проходимся по строкам, где нет знаков "равно"
            if not ('==' in x) and len((x.strip())) > 3:
                '''Если в строке осталось больше трех символов, добавляем ее к нашей переменной 
                и возвращаем утерянные при разделении строк точки на место.'''
                wikitext2 = wikitext2 + x + '.'
            else:
                break

        # Теперь при помощи регулярных выражений убираем разметку.
        wikitext2 = re.sub(r'\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub(r'\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub(r'\{[^\{\}]*\}', '', wikitext2)

        return wikitext2

    except Exception as e:
        return 'В энциклопедии нет информации об этом'


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Введите любое слово, чтобы узнать, что это такое!')


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, getwiki(message.text))

# Запускаем бота
bot.polling(none_stop=True, interval=0)