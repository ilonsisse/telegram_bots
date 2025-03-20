import logging
import sqlite3
import gspread
import random
import asyncio
import os
from google.oauth2.service_account import Credentials
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ========== НАСТРОЙКИ ==========
API_TOKEN = os.getenv('API_KEY')
GOOGLE_DRIVE_FOLDER_ID = '18qsymyQnLPegs-Xt4DvHLGzNJ2X66TqJ'  # ID папки Google Диска
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Ключ сервисного аккаунта

# Логирование
logging.basicConfig(level=logging.INFO)

# Авторизация Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Файл базы данных
DB_FILE = "orders.db"

# Подключение к боту
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ========== ФУНКЦИИ РАБОТЫ С GOOGLE DRIVE ==========
def download_db():
    """Скачивает базу данных с Google Диска."""
    try:
        drive_service = client.auth.service
        file_list = drive_service.files().list(q=f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents").execute()
        for file in file_list.get('files', []):
            if file['name'] == DB_FILE:
                file_id = file['id']
                request = drive_service.files().get_media(fileId=file_id)
                with open(DB_FILE, 'wb') as f:
                    f.write(request.execute())
                print("✅ База данных загружена!")
                return
    except Exception as e:
        print(f"Ошибка при загрузке БД: {e}")

def upload_db():
    """Загружает базу данных обратно в Google Диск."""
    try:
        drive_service = client.auth.service
        file_list = drive_service.files().list(q=f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents").execute()
        for file in file_list.get('files', []):
            if file['name'] == DB_FILE:
                drive_service.files().delete(fileId=file['id']).execute()
        file_metadata = {"name": DB_FILE, "parents": [GOOGLE_DRIVE_FOLDER_ID]}
        drive_service.files().create(body=file_metadata, media_body=DB_FILE).execute()
        print("✅ База данных обновлена!")
    except Exception as e:
        print(f"Ошибка при загрузке БД: {e}")

# Загрузка БД
download_db()
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Создание таблицы, если её нет
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    messages TEXT,
    order_details TEXT,
    recommended_cars TEXT
)
''')
conn.commit()

# ========== ДАННЫЕ ОБ АВТОМОБИЛЯХ ==========
cars_db = {
    "Седан": {
        "Бензиновый": ["Toyota Camry", "Honda Accord", "Hyundai Sonata", "BMW 3", "Mercedes C-Class", "Kia K5", "Audi A4", "Mazda 6", "Lexus ES", "Volkswagen Passat"],
        "Дизельный": ["BMW 5", "Mercedes E-Class", "Audi A6", "Volvo S60", "Jaguar XE", "Peugeot 508", "Hyundai Elantra", "Ford Mondeo", "Renault Talisman", "Citroen C5"],
        "Электро": ["Tesla Model 3", "BMW i4", "Porsche Taycan", "Audi e-tron GT", "Polestar 2", "Mercedes EQE", "Lucid Air", "Nissan Leaf", "Hyundai Ioniq", "BYD Han"],
        "Гибрид": ["Toyota Prius", "Hyundai Ioniq Hybrid", "Honda Insight", "Ford Fusion Hybrid", "Lexus ES Hybrid", "Kia Niro Hybrid", "BMW 330e", "Audi A3 e-tron", "Mercedes C300e", "Volvo S90 Hybrid"]
    },
    "Внедорожник": {
        "Бензиновый": ["Toyota Land Cruiser", "Jeep Grand Cherokee", "Ford Explorer", "BMW X5", "Mercedes GLE", "Honda CR-V", "Hyundai Santa Fe", "Mazda CX-9", "Lexus RX", "Volkswagen Touareg"],
        "Дизельный": ["Land Rover Defender", "Toyota Prado", "BMW X3", "Audi Q7", "Mercedes G-Class", "Volkswagen Tiguan", "Jeep Wrangler", "Ford Everest", "Hyundai Palisade", "Kia Sorento"],
        "Электро": ["Tesla Model X", "Audi Q8 e-tron", "Mercedes EQC", "BMW iX", "Hyundai Ioniq 5", "Rivian R1S", "Ford Mustang Mach-E", "Jaguar I-PACE", "BYD Tang", "Volkswagen ID.4"],
        "Гибрид": ["Toyota RAV4 Hybrid", "Honda CR-V Hybrid", "Ford Escape Hybrid", "Lexus NX Hybrid", "Mitsubishi Outlander PHEV", "Volvo XC90 Hybrid", "Kia Sportage Hybrid", "Hyundai Tucson Hybrid", "BMW X5 xDrive45e", "Mercedes GLE Hybrid"]
    }
}

# ========== ФУНКЦИИ БОТА ==========
user_data = {}

questions = [
    ("Выберите тип кузова:", ["Седан", "Внедорожник"]),
    ("Выберите тип двигателя:", ["Бензиновый", "Дизельный", "Электро", "Гибрид"])
]

@dp.message(lambda message: message.text == "/start")
async def start_cmd(message: types.Message):
    user_data[message.from_user.id] = {"answers": []}
    await ask_question(message, 0)

async def ask_question(message: types.Message, index: int):
    if index < len(questions):
        question, options = questions[index]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for option in options:
            keyboard.add(KeyboardButton(option))
        await message.answer(question, reply_markup=keyboard)
    else:
        await recommend_car(message)

@dp.message(lambda message: message.text in sum([q[1] for q in questions], []))
async def process_answer(message: types.Message):
    user_data[message.from_user.id]["answers"].append(message.text)
    await ask_question(message, len(user_data[message.from_user.id]["answers"]))

async def recommend_car(message: types.Message):
    body_type, engine_type = user_data[message.from_user.id]["answers"]
    recommended_cars = random.sample(cars_db[body_type][engine_type], 3)

    cursor.execute("INSERT INTO orders (user_id, order_details, recommended_cars) VALUES (?, ?, ?)",
                   (message.from_user.id, ", ".join(user_data[message.from_user.id]["answers"]), ", ".join(recommended_cars)))
    conn.commit()
    upload_db()

    await message.answer(f"Мы подобрали автомобили: {', '.join(recommended_cars)}")

# ========== ЗАПУСК ==========
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())