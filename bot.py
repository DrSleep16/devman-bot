import os
import time
import requests
import logging
from telegram import Bot
from dotenv import load_dotenv


root_logger = logging.getLogger()


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def process_review_result(review_result, bot, chat_id):
    new_attempts = review_result["new_attempts"]
    last_attempt_timestamp = review_result["last_attempt_timestamp"]
    params = {"timestamp": last_attempt_timestamp}
    lesson_title = new_attempts[0]['lesson_title']
    lesson_url = new_attempts[0]['lesson_url']
    is_negative = new_attempts[0]['is_negative']
    if is_negative:
        message = f'''
        У вас проверили работу «{lesson_title}»
        К сожалению, в работе нашлись ошибки.
        Ссылка на работу: {lesson_url}
        '''
    else:
        message = f'''
        У вас проверили работу «{lesson_title}»
        Преподавателю всё понравилось! Можно приступить к следующему уроку!
        Ссылка на работу: {lesson_url}
        '''
    bot.send_message(chat_id, text=message)


def main():
    load_dotenv()
    
    tg_token = os.getenv('TG_TOKEN')
    bot = Bot(tg_token)
    
    root_logger.setLevel(logging.ERROR)
    
    api_token = os.getenv('API_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    
    log_handler = TelegramLogHandler(bot, tg_chat_id)
    root_logger.addHandler(log_handler)

    headers = {"Authorization": f"Token {api_token}"}
    url = "https://dvmn.org/api/long_polling/"
    params = None
    
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as e:
            time.sleep(5)
            continue
        except requests.exceptions.RequestException as e:
            continue
        review_result = response.json()
        if review_result["status"] == "found":
            process_review_result(review_result, bot, tg_chat_id)


if __name__ == '__main__':
    main()
