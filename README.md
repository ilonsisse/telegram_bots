# Что делать, чтобы боты работали:

1. Создать виртуальное окружение, пишем в терминале:
> cd имя_папки

> python -m venv venv

> .venv\Scripts\activate(Windows)

> source venv/bin/activate(macOS, Linux)

2. Установить зависимости:
> pip install -r requirements.txt

3. Ввести значения переменных в template.env в виде:
> KEY=value

API_KEY – ключ, который выдает BotFather;

API_ID, API_HASH, PHONE нужны для 8 бота-парсера. Чтобы их получить, нужно перейти по ссылке:
> https://my.telegram.org/apps

4. Меняем название template.env на просто .env