import telebot
import json
import random
import requests
import os
import time
import uuid
from datetime import datetime, timedelta

# ======== НАСТРОЙКИ ========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"

# GigaChat настройки (ваш ключ)
GIGACHAT_AUTH_KEY = "MDE5Y2QzZGYtNzFkMC03MjRlLTljNjMtZDQyYjFlNmI4ZjYyOmIwNGViNDk5LTY5MjktNDJhNi04ODc4LTQ5Y2M5OGMxZGMwNw=="
# ===========================

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Кэш для токенов GigaChat
gigachat_token_cache = {
    'token': None,
    'expires_at': None
}

def get_gigachat_token():
    """Получает access token для GigaChat API"""
    global gigachat_token_cache
    
    # Проверяем кэш
    if gigachat_token_cache['token'] and gigachat_token_cache['expires_at'] > datetime.now():
        return gigachat_token_cache['token']
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {GIGACHAT_AUTH_KEY}'
    }
    
    data = {'scope': 'GIGACHAT_API_PERS'}
    
    try:
        print("🔄 Получение токена GigaChat...")
        
        # Отключаем проверку SSL (как в curl с флагом -k)
        response = requests.post(url, headers=headers, data=data, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            token = result['access_token']
            expires_in = result['expires_in']
            
            gigachat_token_cache['token'] = token
            gigachat_token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print("✅ Токен получен")
            return token
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            print(f"Ответ: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def ask_gigachat(user_message):
    """Отправляет запрос к GigaChat"""
    
    token = get_gigachat_token()
    if not token:
        return None
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    system_prompt = """Ты — дружелюбный помощник по профориентации для подростков 12-15 лет по имени ПрофИИ.
Твоя задача — в непринужденной беседе выяснить интересы ребенка и предложить подходящие современные профессии.
Общайся на понятном языке, используй эмодзи, будь позитивным.
В конце предложи 2-3 профессии."""
    
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        print("🔄 Отправка запроса к GigaChat...")
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print("✅ Ответ получен")
            return answer
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

# ======== ЗАГРУЗКА ПРОФЕССИЙ ========
def load_professions():
    try:
        with open('professions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"✅ Загружено профессий: {len(data['professions'])}")
            return data['professions']
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return []

professions = load_professions()

# Хранилища состояний
user_answers = {}
user_mode = {}

# ======== ФУНКЦИЯ ГЛАВНОГО МЕНЮ ========
def show_main_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📋 ПРОЙТИ ТЕСТ")
    btn2 = telebot.types.KeyboardButton("💬 ОБЩЕНИЕ С GigaChat")
    markup.add(btn1, btn2)
    
    welcome_text = """
🚀 *Добро пожаловать в ПрофИИ!*

Выбери, что хочешь сделать:

📋 *ПРОЙТИ ТЕСТ* — ответь на 10 вопросов
💬 *ОБЩЕНИЕ С GigaChat* — просто поговори со мной

*Попробуй прямо сейчас!* 👇
    """
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ======== ТЕСТ (10 ВОПРОСОВ) ========
questions = [
    {
        "id": 1,
        "text": "Какая сфера деятельности тебе ближе?",
        "options": [
            {"text": "🧑‍⚕️ Помощь людям, забота о здоровье", "keywords": ["врач", "ветеринар", "психолог"]},
            {"text": "📚 Образование, передача знаний", "keywords": ["учитель", "педагогика"]},
            {"text": "💻 Информационные технологии, программирование", "keywords": ["программист", "разработчик"]},
            {"text": "🏗️ Строительство, создание объектов", "keywords": ["инженер", "строитель"]}
        ]
    },
    {
        "id": 2,
        "text": "Какой стиль работы тебе подходит больше?",
        "options": [
            {"text": "🎯 Работа с людьми, общение", "keywords": ["врач", "учитель", "психолог"]},
            {"text": "🧠 Интеллектуальная работа, анализ", "keywords": ["аналитик", "нейросети"]},
            {"text": "✋ Практическая работа руками", "keywords": ["повар", "электрик", "строитель"]},
            {"text": "🎨 Творчество, дизайн", "keywords": ["дизайнер", "архитектор"]}
        ]
    },
    {
        "id": 3,
        "text": "Какие школьные предметы тебе нравятся больше всего?",
        "options": [
            {"text": "🔬 Биология, химия", "keywords": ["врач", "ветеринар", "биоинженер"]},
            {"text": "🧮 Математика, физика", "keywords": ["инженер", "программист"]},
            {"text": "💻 Информатика", "keywords": ["программист", "разработчик"]},
            {"text": "📖 Литература, история", "keywords": ["учитель", "психолог"]},
            {"text": "🎨 Рисование, технология", "keywords": ["дизайнер", "архитектор"]}
        ]
    },
    {
        "id": 4,
        "text": "Какая у тебя суперсила?",
        "options": [
            {"text": "💪 Ответственность и надёжность", "keywords": ["врач", "учитель", "инженер"]},
            {"text": "🤝 Коммуникабельность", "keywords": ["психолог", "учитель", "продавец"]},
            {"text": "🔍 Внимательность к деталям", "keywords": ["аналитик", "разработчик"]},
            {"text": "💡 Креативность", "keywords": ["дизайнер", "архитектор"]}
        ]
    },
    {
        "id": 5,
        "text": "Какую рабочую обстановку ты предпочитаешь?",
        "options": [
            {"text": "🏥 В офисе, с людьми", "keywords": ["врач", "учитель", "психолог"]},
            {"text": "🏗️ На улице, на объектах", "keywords": ["строитель", "инженер"]},
            {"text": "💻 За компьютером", "keywords": ["программист", "дизайнер"]},
            {"text": "🍳 В мастерской, студии", "keywords": ["повар", "художник"]}
        ]
    }
]

# ======== ПОИСК ПРОФЕССИЙ ========
def find_professions_by_keywords(user_text):
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

# ======== КОМАНДЫ ========
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'menu'
    show_main_menu(message.chat.id)

@bot.message_handler(commands=['test'])
def test_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'test'
    bot.send_message(message.chat.id, "📋 *Начинаем тест!*", parse_mode="Markdown")
    ask_question(message.chat.id, user_id, 0)

@bot.message_handler(commands=['menu'])
def menu_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'menu'
    show_main_menu(message.chat.id)

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

# ======== ОБРАБОТКА СООБЩЕНИЙ ========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    
    if user_id not in user_mode:
        user_mode[user_id] = 'menu'
    
    if user_text == "🏠 В меню":
        user_answers[user_id] = []
        user_mode[user_id] = 'menu'
        show_main_menu(message.chat.id)
        return
    
    if user_text == "📋 ПРОЙТИ ТЕСТ":
        test_command(message)
        return
    
    if user_text == "💬 ОБЩЕНИЕ С GigaChat":
        user_answers[user_id] = []
        user_mode[user_id] = 'gigachat'
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        bot.send_message(message.chat.id, 
            "💬 *Режим общения с GigaChat*\n\n"
            "Просто напиши мне о своих увлечениях!\n\n"
            "Например:\n"
            "• \"Я люблю рисовать\"\n"
            "• \"Мне нравится программировать\"\n"
            "• \"Хочу помогать животным\"\n\n"
            "Чтобы вернуться в меню, нажми кнопку ниже 👇",
            parse_mode="Markdown", reply_markup=markup)
        return
    
    # Режим теста
    if user_mode.get(user_id) == 'test' and user_id in user_answers:
        answered = sum(1 for a in user_answers[user_id] if isinstance(a, dict) and 'keywords' in a)
        
        if answered < len(questions):
            q = questions[answered]
            selected = None
            for opt in q['options']:
                if opt['text'].lower() in user_text.lower():
                    selected = opt
                    break
            
            if selected:
                user_answers[user_id].append({"keywords": selected['keywords']})
                ask_question(message.chat.id, user_id, answered + 1)
            else:
                bot.send_message(message.chat.id, "Пожалуйста, выбери вариант из кнопок 👇")
            return
    
    # Режим GigaChat
    if user_mode.get(user_id) in ['gigachat', 'menu']:
        bot.send_chat_action(message.chat.id, 'typing')
        gpt_response = ask_gigachat(user_text)
        
        if gpt_response:
            bot.send_message(message.chat.id, gpt_response)
        else:
            found = find_professions_by_keywords(user_text)
            if found:
                response = "🔍 *Нашёл в локальной базе:*\n\n"
                for prof in found[:3]:
                    response += format_profession(prof) + "\n" + "—" * 30 + "\n"
                bot.send_message(message.chat.id, response, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, 
                    "🤔 Не нашёл подходящих профессий. Расскажи подробнее!\n\n"
                    "Или нажми /menu")

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
    
    bot.send_message(chat_id, "✅ *Готово!* Нажми /menu чтобы вернуться", parse_mode="Markdown")
    user_mode[user_id] = 'menu'

# ======== ЗАПУСК ========
if __name__ == "__main__":
    print("🚀 Бот ПрофИИ запускается...")
    print(f"✅ Загружено профессий: {len(professions)}")
    print("🔄 GigaChat подключен")
    bot.infinity_polling()
