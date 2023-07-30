import aiohttp
import asyncio
import logging
import psycopg2
import json
import datetime

from aiogram.types.web_app_info import WebAppInfo
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from open_ai import get_ai_answer, get_response_to_request


AMPLITUDE_API_KEY = '984982210466cb0c2b40057f256919a4'
AMPLITUDE_URL = 'https://api.amplitude.com/2/httpapi'

# Database connection parameters
DB_NAME = 'i5cpu'
DB_USER = 'i5cpu'
DB_PASSWORD = 'Johon667'
DB_HOST = 'localhost'
DB_PORT = '5432'

bot = Bot(token='6626572732:AAGMXYcjNNRLArWOsF40nf9c_F7Xlp2SJI8')
dp = Dispatcher(bot)

# Logging setup
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    time TEXT,
                    character TEXT DEFAULT 'guest'
                )''')
conn.commit()

# Function to send an event to Amplitude
async def send_amplitude_event(event_type, user_id):
    async with aiohttp.ClientSession() as session:
        data = {
            'api_key': AMPLITUDE_API_KEY,
            'events': [
                {
                    'user_id': user_id,
                    'event_type': event_type,
                }
            ]
        }
        async with session.post(AMPLITUDE_URL, json=data) as response:
            if response.status == 200:
                logging.info("Event successfully sent to Amplitude")
            else:
                logging.error("Error sending event to Amplitude")
                logging.error(await response.text())


def is_user_id_in_db(user_id):
    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()
    for i in user_ids:
        return i[0] == user_id


@dp.message_handler(commands=['start'])
async def main(message: types.Message):
    user_id = message.from_user.id

    # Sending Amplitude event
    event = 'registration_completed'
    await send_amplitude_event(event, user_id)

    # Save the user to the database
    if not is_user_id_in_db(user_id):
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        current_time = datetime.datetime.now()

        cursor.execute(
            'INSERT INTO users VALUES (%s, %s, %s, %s, %s, NULL)',
            (user_id, username, first_name, last_name, current_time)
        )
        conn.commit()

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton("Characters ", web_app=WebAppInfo(url='https://i3cpu.github.io/characterAi-bot-web-interface/index.html'))
    markup.row(btn1)

    await message.answer('Hello, choose a character you want to chat with!', reply_markup=markup)


@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    user_id = message.from_user.id
    data = json.loads(message.web_app_data.data)
    character = data['character']

    # Sending Amplitude event
    event = f'{character} character selected'
    await send_amplitude_event(event, user_id)

    cursor.execute("UPDATE users SET character = %s WHERE user_id = %s", (character, user_id))
    conn.commit()

    msg_from_user = f"Hi,{character}"
    response = get_response_to_request(character=character, msg_from_user=msg_from_user)

    await message.answer(f'{response}')


@dp.message_handler(content_types=['text'])
async def answer(message: types.Message):

    user_id = message.from_user.id
    cursor.execute("SELECT character FROM users WHERE user_id = %s", (user_id,))
    character = cursor.fetchone()[0]

    # Sending Amplitude event
    event = f'request from user sent: "{message.text}"'
    await send_amplitude_event(event, user_id)

    response = get_response_to_request(character=character, msg_from_user=message.text)

    # Sending Amplitude event
    event = f'received response from ai: "{response}"'
    await send_amplitude_event(event, user_id)

    await message.answer(f'{response}')


# def show_db():
#     cursor.execute("SELECT * FROM users")
#     rows = cursor.fetchall()
#     if rows:
#         print(rows)
#     else:
#         print('-- None --')


executor.start_polling(dp)
