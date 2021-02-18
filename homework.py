import os
import time

import logging
import requests
import telegram
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('__name__')

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

PRACTICUM_URL = 'https://praktikum.yandex.ru/api/user_api/'


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        if homework['status'] == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework['status'] == 'approved':
            verdict = ('Ревьюеру всё понравилось, '
                       'можно приступать к следующему уроку.')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except requests.RequestException as e:
        logger.exception(e)
        return {}


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            '{url}{method}'.format(
                url=PRACTICUM_URL,
                method='homework_statuses/'
            ),
            params=params, headers=headers)
        return homework_statuses.json()
    except requests.RequestException as e:
        logger.exception(e)
        return {}


def send_message(message, bot_client):
    logging.info('Сообщение отправляется.')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            get_homework = new_homework.get('homeworks')
            if get_homework:
                send_message(parse_homework_status(
                    get_homework[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp)
            time.sleep(300)

        except Exception as e:
            logging.error(e, exc_info=True)
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
