import aiohttp
import asyncio
import logging


AMPLITUDE_API_KEY = '984982210466cb0c2b40057f256919a4'
AMPLITUDE_URL = 'https://api.amplitude.com/2/httpapi'


# Функция отправки события в Amplitude
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
                logging.info("Событие успешно отправлено в Amplitude")
            else:
                logging.error("Ошибка при отправке события в Amplitude")
                logging.error(await response.text())