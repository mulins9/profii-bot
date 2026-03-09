import telebot
import json
import random
import requests
import os
import uuid
from datetime import datetime
from flask import Flask
import threading
import time

# ========== FLASK ДЛЯ RENDER ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот ПрофИИ работает!"

@app.route('/health')
def health():
    return "OK", 200
# ========================================

# ========== ТЕЛЕГРАМ ==========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"
bot = telebot.TeleBot(TELEGRAM_TOKEN)
# ===============================

# ========== GIGACHAT ==========
GIGACHAT_AUTH_KEY = "MDE5Y2QzZGYtNzFkMC03MjRlLTljNjMtZDQyYjFlNmI4ZjYyOmIwNGViNDk5LTY5MjktNDJhNi04ODc4LTQ5Y2M5OGMxZGMwNw=="
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

gigachat_token = {
    'token': None,
    'expires_at': None
}

def get_gigachat_token():
    global gigachat_token
    if gigachat_token['token'] and gigachat_token['expires_at'] and datetime.now() < gigachat_token['expires_at']:
        return gigachat_token['token']

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {GIGACHAT_AUTH_KEY}'
    }
    data = {'scope': GIGACHAT_SCOPE}

    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            result = response.json()
            gigachat_token['token'] = result['access_token']
            gigachat_token['expires_at'] = datetime.fromtimestamp(result['expires_at'] / 1000)
            return gigachat_token['token']
        else:
            print(f"❌ Ошибка токена: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def ask_gigachat(user_message):
    token = get_gigachat_token()
    if not token:
        return None

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": "Ты — помощник по профориентации для подростков. Отвечай коротко, с эмодзи, предлагай 2-3 профессии."},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"❌ Ошибка GigaChat: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None
# ===============================

# ========== ЗАГРУЗКА ПРОФЕССИЙ ========
def load_professions():
    try:
        with open('professions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Загружено профессий: {len(data['professions'])}")
            return data['professions']
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return []

professions = load_professions()
# ====================================

# Хранилища
user_answers = {}
user_mode = {}

# ======== ТЕСТ ИЗ 10 ВОПРОСОВ ========
questions = [
    {
        "id": 1,
        "text": "Какая сфера деятельности тебе ближе?",
        "options": [
            {"text": "🧑‍⚕️ Помощь людям, забота о здоровье", "keywords": ["врач", "ветеринар", "психолог", "медицина"]},
            {"text": "📚 Образование, передача знаний", "keywords": ["учитель", "педагогика", "образование"]},
            {"text": "💻 Информационные технологии, программирование", "keywords": ["программист", "разработчик", "it", "код"]},
            {"text": "🏗️ Строительство, создание объектов", "keywords": ["инженер", "строитель", "архитектура"]},
            {"text": "🎨 Творчество, дизайн", "keywords": ["дизайнер", "архитектор", "художник"]}
        ]
    },
    {
        "id": 2,
        "text": "Какой стиль работы тебе подходит больше?",
        "options": [
            {"text": "🎯 Работа с людьми, общение", "keywords": ["врач", "учитель", "психолог", "менеджер"]},
            {"text": "🧠 Интеллектуальная работа, анализ", "keywords": ["аналитик", "исследователь", "программист"]},
            {"text": "✋ Практическая работа руками", "keywords": ["повар", "электрик", "строитель", "столяр"]},
            {"text": "🎨 Творчество, создание нового", "keywords": ["дизайнер", "архитектор", "художник"]}
        ]
    },
    {
        "id": 3,
        "text": "Какие школьные предметы тебе нравятся больше всего?",
        "options": [
            {"text": "🔬 Биология, химия", "keywords": ["врач", "ветеринар", "биолог", "химик"]},
            {"text": "🧮 Математика, физика", "keywords": ["инженер", "программист", "физик", "экономист"]},
            {"text": "💻 Информатика", "keywords": ["программист", "разработчик", "сисадмин"]},
            {"text": "📖 Литература, история", "keywords": ["учитель", "журналист", "писатель", "историк"]},
            {"text": "🎨 Рисование, технология", "keywords": ["дизайнер", "архитектор", "художник"]}
        ]
    },
    {
        "id": 4,
        "text": "Какая у тебя главная черта характера?",
        "options": [
            {"text": "💪 Ответственность и надёжность", "keywords": ["врач", "учитель", "инженер", "пилот"]},
            {"text": "🤝 Коммуникабельность", "keywords": ["менеджер", "продавец", "психолог", "журналист"]},
            {"text": "🔍 Внимательность к деталям", "keywords": ["аналитик", "программист", "редактор", "бухгалтер"]},
            {"text": "💡 Креативность, фантазия", "keywords": ["дизайнер", "художник", "писатель", "архитектор"]},
            {"text": "🧠 Логическое мышление", "keywords": ["программист", "инженер", "учёный", "шахматист"]}
        ]
    },
    {
        "id": 5,
        "text": "Какую обстановку для работы ты предпочитаешь?",
        "options": [
            {"text": "🏥 В офисе, больнице, школе", "keywords": ["врач", "учитель", "менеджер", "адвокат"]},
            {"text": "🏗️ На улице, на объектах, в разъездах", "keywords": ["строитель", "геолог", "водитель", "курьер"]},
            {"text": "💻 За компьютером, удалённо", "keywords": ["программист", "дизайнер", "копирайтер", "аналитик"]},
            {"text": "🍳 В мастерской, студии, на кухне", "keywords": ["повар", "художник", "столяр", "керамист"]}
        ]
    },
    {
        "id": 6,
        "text": "Что для тебя важнее всего в профессии?",
        "options": [
            {"text": "💰 Высокий доход", "keywords": ["программист", "менеджер", "пилот", "врач"]},
            {"text": "❤️ Помощь людям, польза обществу", "keywords": ["врач", "учитель", "психолог", "соцработник"]},
            {"text": "🎨 Творческая самореализация", "keywords": ["дизайнер", "художник", "музыкант", "писатель"]},
            {"text": "🛡️ Стабильность и надёжность", "keywords": ["учитель", "врач", "инженер", "военный"]},
            {"text": "🚀 Инновации и развитие", "keywords": ["программист", "учёный", "инженер", "исследователь"]}
        ]
    },
    {
        "id": 7,
        "text": "Как ты обычно решаешь проблемы?",
        "options": [
            {"text": "📚 Ищу информацию, анализирую", "keywords": ["аналитик", "учёный", "журналист", "детектив"]},
            {"text": "🤔 Думаю логически, ищу алгоритм", "keywords": ["программист", "инженер", "шахматист", "математик"]},
            {"text": "💬 Обсуждаю с другими, советуюсь", "keywords": ["психолог", "менеджер", "учитель", "адвокат"]},
            {"text": "🛠️ Пробую на практике, экспериментирую", "keywords": ["инженер", "химик", "повар", "строитель"]},
            {"text": "🎨 Ищу нестандартный, творческий подход", "keywords": ["дизайнер", "художник", "изобретатель", "писатель"]}
        ]
    },
    {
        "id": 8,
        "text": "Какое у тебя хобби?",
        "options": [
            {"text": "🎮 Компьютерные игры", "keywords": ["программист", "тестировщик", "киберспортсмен", "геймдизайнер"]},
            {"text": "📚 Чтение книг", "keywords": ["учитель", "журналист", "писатель", "библиотекарь"]},
            {"text": "🎨 Рисование, фото, монтаж", "keywords": ["дизайнер", "художник", "фотограф", "видеомейкер"]},
            {"text": "🔧 Мастерю, чиню, собираю", "keywords": ["инженер", "электрик", "механик", "робототехник"]},
            {"text": "🏃 Спорт", "keywords": ["тренер", "спортсмен", "учитель физкультуры", "массажист"]}
        ]
    },
    {
        "id": 9,
        "text": "Какие профессии будущего тебе интересны?",
        "options": [
            {"text": "🤖 Работа с ИИ и нейросетями", "keywords": ["разработчик ИИ", "промпт-инженер", "аналитик данных"]},
            {"text": "🚁 Дроны и роботы", "keywords": ["робототехник", "оператор дронов", "инженер"]},
            {"text": "🧬 Биотехнологии, медицина", "keywords": ["биоинженер", "врач", "генетик", "фармацевт"]},
            {"text": "🌱 Экология, устойчивое развитие", "keywords": ["эколог", "биолог", "агроном"]}
        ]
    },
    {
        "id": 10,
        "text": "Кем ты видишь себя через 10–15 лет?",
        "options": [
            {"text": "👨‍🏫 Эксперт, профессионал в своём деле", "keywords": ["врач", "учитель", "инженер", "адвокат"]},
            {"text": "🚀 Создаю инновации, новое", "keywords": ["программист", "учёный", "изобретатель", "дизайнер"]},
            {"text": "👩‍🎨 Занимаюсь творчеством, создаю красоту", "keywords": ["дизайнер", "художник", "архитектор", "музыкант"]},
            {"text": "🤝 Руковожу командой, управляю", "keywords": ["менеджер", "директор", "продюсер", "руководитель"]}
        ]
    }
]
# ======================================

# ======== ФУНКЦИЯ ГЛАВНОГО МЕНЮ ========
def show_main_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📋 ПРОЙТИ ТЕСТ")
    btn2 = telebot.types.KeyboardButton("💬 GigaChat")
    markup.add(btn1, btn2)
    
    welcome_text = """
🚀 *ПрофИИ — твой навигатор в мире профессий!*

📋 *ПРОЙТИ ТЕСТ* — 10 вопросов подберут профессию
💬 *GigaChat* — пообщайся с искусственным интеллектом

*Выбирай!* 👇
    """
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ======== ПОИСК ПРОФЕССИЙ ========
def find_professions(user_text):
    user_text_lower = user_text.lower()
    found = []
    for prof in professions:
        for keyword in prof['keywords']:
            if keyword.lower() in user_text_lower:
                if prof not in found:
                    found.append(prof)
                break
    return found

# ======== ФОРМАТ ПРОФЕССИИ ========
def format_profession(prof):
    return f"""
🔹 *{prof['name']}*

{prof['description']}

📚 *Предметы:* {', '.join(prof['school_subjects'])}
🔧 *Навыки:* {', '.join(prof['skills'])}
💰 *Зарплата:* {prof['salary']}

✨ {prof['trend']}
    """

# ======== КОМАНДА /START ========
@bot.message_handler(commands=['start', 'menu'])
def start_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'menu'
    show_main_menu(message.chat.id)

# ======== КОМАНДА /TEST ========
@bot.message_handler(commands=['test'])
def test_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'test'
    bot.send_message(message.chat.id, "📋 *Начинаем тест из 10 вопросов!*", parse_mode="Markdown")
    ask_question(message.chat.id, user_id, 0)

# ======== ФУНКЦИЯ ЗАДАНИЯ ВОПРОСА ========
def ask_question(chat_id, user_id, question_index):
    if question_index < len(questions):
        q = questions[question_index]
        text = f"*Вопрос {question_index + 1} из {len(questions)}*\n\n{q['text']}"
        
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for opt in q['options']:
            markup.add(telebot.types.KeyboardButton(opt['text']))
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    else:
        show_result(chat_id, user_id)

# ======== ПОКАЗ РЕЗУЛЬТАТОВ ТЕСТА ========
def show_result(chat_id, user_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🏠 В меню"))
    
    bot.send_message(chat_id, "🔍 *Анализирую твои ответы...*", parse_mode="Markdown", reply_markup=markup)
    
    answers = user_answers.get(user_id, [])
    all_keywords = []
    for a in answers:
        if isinstance(a, dict) and 'keywords' in a:
            all_keywords.extend(a['keywords'])
    
    scores = []
    for prof in professions:
        score = sum(1 for kw in all_keywords if kw.lower() in [k.lower() for k in prof['keywords']])
        scores.append((prof, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    top = [prof for prof, score in scores[:3] if score > 0]
    
    if not top:
        top = random.sample(professions, min(3, len(professions)))
    
    for prof in top:
        bot.send_message(chat_id, format_profession(prof), parse_mode="Markdown")
        time.sleep(0.5)
    
    bot.send_message(chat_id, "✅ *Тест пройден!* /menu", parse_mode="Markdown")
    user_mode[user_id] = 'menu'

# ======== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    
    if user_id not in user_mode:
        user_mode[user_id] = 'menu'
    
    # Кнопка "В меню"
    if user_text == "🏠 В меню":
        user_answers[user_id] = []
        user_mode[user_id] = 'menu'
        show_main_menu(message.chat.id)
        return
    
    # Кнопки главного меню
    if user_text == "📋 ПРОЙТИ ТЕСТ":
        test_command(message)
        return
    
    if user_text == "💬 GigaChat":
        user_answers[user_id] = []
        user_mode[user_id] = 'gigachat'
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        bot.send_message(message.chat.id, 
            "💬 *Режим GigaChat*\n\nНапиши о своих увлечениях, я помогу подобрать профессию!",
            parse_mode="Markdown", reply_markup=markup)
        return
    
    # Режим теста
    if user_mode.get(user_id) == 'test':
        answered_count = 0
        for item in user_answers[user_id]:
            if isinstance(item, dict) and 'keywords' in item:
                answered_count += 1
        
        if answered_count < len(questions):
            q = questions[answered_count]
            selected = None
            for opt in q['options']:
                if opt['text'].lower() in user_text.lower() or user_text.lower() in opt['text'].lower():
                    selected = opt
                    break
            
            if selected:
                user_answers[user_id].append({"keywords": selected['keywords']})
                ask_question(message.chat.id, user_id, answered_count + 1)
            else:
                bot.send_message(message.chat.id, "Пожалуйста, выбери вариант из кнопок 👇")
        return
    
    # Режим GigaChat
    if user_mode.get(user_id) == 'gigachat':
        bot.send_chat_action(message.chat.id, 'typing')
        gpt_response = ask_gigachat(user_text)
        
        if gpt_response:
            bot.send_message(message.chat.id, gpt_response)
        else:
            bot.send_message(message.chat.id, "⚠️ GigaChat временно недоступен, ищу в локальной базе...")
            found = find_professions(user_text)
            if found:
                response = "🔍 *Нашёл в базе:*\n\n"
                for prof in found[:3]:
                    response += format_profession(prof) + "\n" + "—" * 30 + "\n"
                bot.send_message(message.chat.id, response, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, 
                    "🤔 Не нашёл подходящих профессий. Попробуй иначе или /menu")
        return
    
    # Обычный режим
    found = find_professions(user_text)
    if found:
        response = "🔍 *Нашёл в базе:*\n\n"
        for prof in found[:3]:
            response += format_profession(prof) + "\n" + "—" * 30 + "\n"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🤔 Не нашёл. Попробуй /menu")

# ======== ЗАПУСК БОТА ========
def run_bot():
    while True:
        try:
            print("🚀 Бот ПрофИИ запускается...")
            print(f"✅ Загружено профессий: {len(professions)}")
            print("🔄 Пробую получить токен GigaChat...")
            token = get_gigachat_token()
            if token:
                print("✅ GigaChat готов к работе!")
            else:
                print("⚠️ GigaChat пока недоступен, будет работать локальная база")
            bot.infinity_polling()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
