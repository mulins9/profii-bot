from flask import Flask
import threading
import os
import time
from profii_test_bot import bot  # импортируем вашего бота

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 ПрофИИ бот работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Запускает бота в отдельном потоке"""
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка бота: {e}, перезапуск через 5 секунд...")
            time.sleep(5)

@app.before_first_request
def start_bot_thread():
    """Запускает бота при первом запросе к серверу"""
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
