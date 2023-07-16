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
        except requests.exceptions.ConnectionError as e:
            print(f"Нет соединения: {e}")
            time.sleep(5)
            continue
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            continue
        response_data = response.json()
        if response_data["status"] == "found":
            new_attempts = response_data["new_attempts"]
            last_attempt_timestamp = response_data["last_attempt_timestamp"]
            print(new_attempts)
            params = {"timestamp": last_attempt_timestamp}
            if new_attempts[0]['is_negative']:
                bot.sendMessage(
                chat_id=chat_id,
                text=f"У вас проверили работу «{new_attempts[0]['lesson_title']}»"
                     f"\n\n"
                     f"К сожалению, в работе нашлись ошибки."
                     f"\n\n"
                     f"Ссылка на работу: {new_attempts[0]['lesson_url']}"
                            )
            elif new_attempts[0]['is_negative'] is False:
                bot.sendMessage(
                chat_id=chat_id,
                text=f"У вас проверили работу «{new_attempts[0]['lesson_title']}»"
                     f"\n\n"
                     f"преподавателю всё понравилось! Можно приступить к следующему уроку!"
                     f"\n\n"
                     f"Ссылка на работу: {new_attempts[0]['lesson_url']}"
                            )

if __name__ == '__main__':
    tg_token = os.getenv('TG_TOKEN')
    api_token= os.getenv('API_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    get_user_reviews_long_polling(api_token, tg_chat_id, tg_token)


