from flask import Flask
import threading
import os
import time
from profii_test_bot import bot

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
            print("🔄 Запуск бота...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"❌ Ошибка бота: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)

# Запускаем бота в отдельном потоке при старте приложения
print("🚀 Запуск приложения...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
print("✅ Поток бота запущен")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
