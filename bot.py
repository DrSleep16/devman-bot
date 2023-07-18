import os
import time
import requests
from telegram import Bot


def get_user_reviews_long_polling(api_token, chat_id, tg_token):
    bot = Bot(tg_token)
    headers = {"Authorization": f"Token {api_token}"}
    url = "https://dvmn.org/api/long_polling/"
    params = None
    while True:
        try:
            response = requests.get(url, headers=headers,
                                    params=params)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as e:
            print(f"Нет соединения: {e}")
            time.sleep(5)
            continue
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            continue
        review_result = response.json()
        if review_result["status"] == "found":
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
            bot.send_message(chat_id,text=message)

if __name__ == '__main__':
    tg_token = os.getenv('TG_TOKEN')
    api_token= os.getenv('API_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    get_user_reviews_long_polling(api_token, tg_chat_id, tg_token)


