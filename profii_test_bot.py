import telebot
import json
import random
import requests
import uuid
from datetime import datetime, timedelta

# ======== НАСТРОЙКИ ========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ======== GIGACHAT НАСТРОЙКИ ========
GIGACHAT_AUTH_KEY = "MDE5Y2QzZGYtNzFkMC03MjRlLTljNjMtZDQyYjFlNmI4ZjYyOmIwNGViNDk5LTY5MjktNDJhNi04ODc4LTQ5Y2M5OGMxZGMwNw=="
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"
# ====================================

# Кэш для токена
gigachat_token = {
    'token': None,
    'expires_at': None
}

def get_gigachat_token():
    """Получение токена строго по документации"""
    global gigachat_token
    
    # Проверяем, жив ли ещё токен
    if gigachat_token['token'] and gigachat_token['expires_at'] and datetime.now() < gigachat_token['expires_at']:
        return gigachat_token['token']
    
    # URL из документации
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    # Генерируем уникальный RqUID (обязательно!)
    rq_uid = str(uuid.uuid4())
    
    # Заголовки как в curl
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': rq_uid,
        'Authorization': f'Basic {GIGACHAT_AUTH_KEY}'
    }
    
    # Данные как в curl
    data = {'scope': GIGACHAT_SCOPE}
    
    try:
        print(f"🔄 Получение токена (RqUID: {rq_uid})...")
        
        # Отключаем проверку SSL (как в curl с -k)
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        response = requests.post(url, headers=headers, data=data, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            token = result['access_token']
            expires_at = result['expires_at']  # в миллисекундах
            
            # Конвертируем в datetime (из миллисекунд)
            gigachat_token['token'] = token
            gigachat_token['expires_at'] = datetime.fromtimestamp(expires_at / 1000)
            
            print(f"✅ Токен получен, истекает: {gigachat_token['expires_at']}")
            return token
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            print(f"Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def ask_gigachat(user_message):
    """Отправка запроса к GigaChat"""
    
    token = get_gigachat_token()
    if not token:
        return None
    
    # URL для запросов из документации
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Системный промпт для профориентации
    system_prompt = """Ты — дружелюбный помощник по профориентации для подростков 12-15 лет по имени ПрофИИ.
Твоя задача — помочь выбрать профессию. Общайся просто, используй эмодзи, будь позитивным.
Узнай интересы ребёнка и предложи 2-3 подходящие профессии."""
    
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
            print("✅ Ответ получен!")
            return answer
        else:
            print(f"❌ Ошибка GigaChat: {response.status_code}")
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

# Хранилища
user_answers = {}
user_mode = {}

# ======== ГЛАВНОЕ МЕНЮ ========
def show_main_menu(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📋 ПРОЙТИ ТЕСТ")
    btn2 = telebot.types.KeyboardButton("💬 ОБЩЕНИЕ С GigaChat")
    markup.add(btn1, btn2)
    
    welcome = """
🚀 *ПрофИИ — твой навигатор в мире профессий!*

📋 *ПРОЙТИ ТЕСТ* — 10 вопросов подберут профессию
💬 *GigaChat* — пообщайся с искусственным интеллектом

*Выбирай!* 👇
    """
    bot.send_message(chat_id, welcome, parse_mode="Markdown", reply_markup=markup)

# ======== ТЕСТ (10 вопросов) ========
questions = [
    {
        "id": 1,
        "text": "Какая сфера тебе ближе?",
        "options": [
            {"text": "🧑‍⚕️ Помощь людям", "keywords": ["врач", "психолог"]},
            {"text": "📚 Образование", "keywords": ["учитель"]},
            {"text": "💻 Программирование", "keywords": ["программист"]},
            {"text": "🏗️ Строительство", "keywords": ["инженер"]},
            {"text": "🎨 Творчество", "keywords": ["дизайнер"]}
        ]
    },
    {
        "id": 2,
        "text": "Как любишь работать?",
        "options": [
            {"text": "🎯 С людьми", "keywords": ["врач", "учитель"]},
            {"text": "🧠 Анализировать", "keywords": ["аналитик"]},
            {"text": "✋ Руками", "keywords": ["строитель"]},
            {"text": "🎨 Творить", "keywords": ["дизайнер"]}
        ]
    }
] + [{"id": i, "text": f"Вопрос {i}", "options": []} for i in range(3, 11)]

# ======== ПОИСК ========
def find_professions(user_text):
    text = user_text.lower()
    found = []
    for prof in professions:
        for kw in prof['keywords']:
            if kw.lower() in text:
                if prof not in found:
                    found.append(prof)
                break
    return found

# ======== КАРТОЧКА ========
def format_prof(prof):
    return f"""
🔹 *{prof['name']}*

{prof['description']}

📚 *Предметы:* {', '.join(prof['school_subjects'])}
🔧 *Навыки:* {', '.join(prof['skills'])}
💰 *Зарплата:* {prof['salary']}

✨ {prof['trend']}
    """

# ======== КОМАНДЫ ========
@bot.message_handler(commands=['start', 'menu'])
def start_menu(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'menu'
    show_main_menu(message.chat.id)

# ======== ВОПРОСЫ ТЕСТА ========
def ask_question(chat_id, user_id, q_index):
    if q_index < len(questions):
        q = questions[q_index]
        text = f"*Вопрос {q_index+1} из {len(questions)}*\n\n{q['text']}"
        
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for opt in q['options']:
            markup.add(telebot.types.KeyboardButton(opt['text']))
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    else:
        show_result(chat_id, user_id)

# ======== РЕЗУЛЬТАТ ТЕСТА ========
def show_result(chat_id, user_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🏠 В меню"))
    
    bot.send_message(chat_id, "🔍 *Анализирую...*", parse_mode="Markdown", reply_markup=markup)
    
    # Собираем ключевые слова
    answers = user_answers.get(user_id, [])
    keywords = []
    for a in answers:
        if isinstance(a, dict) and 'keywords' in a:
            keywords.extend(a['keywords'])
    
    # Считаем баллы
    scores = []
    for prof in professions:
        score = sum(1 for kw in keywords if kw.lower() in [k.lower() for k in prof['keywords']])
        scores.append((prof, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    top = [p for p, s in scores[:3] if s > 0]
    
    if not top:
        top = random.sample(professions, min(3, len(professions)))
    
    for prof in top:
        bot.send_message(chat_id, format_prof(prof), parse_mode="Markdown")
    
    bot.send_message(chat_id, "✅ *Готово!* /menu", parse_mode="Markdown")
    user_mode[user_id] = 'menu'

# ======== ОБРАБОТКА СООБЩЕНИЙ ========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    
    if user_id not in user_mode:
        user_mode[user_id] = 'menu'
    
    # Кнопка меню
    if text == "🏠 В меню":
        user_answers[user_id] = []
        user_mode[user_id] = 'menu'
        show_main_menu(message.chat.id)
        return
    
    # Кнопки меню
    if text == "📋 ПРОЙТИ ТЕСТ":
        user_answers[user_id] = []
        user_mode[user_id] = 'test'
        ask_question(message.chat.id, user_id, 0)
        return
    
    if text == "💬 ОБЩЕНИЕ С GigaChat":
        user_answers[user_id] = []
        user_mode[user_id] = 'gigachat'
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        bot.send_message(message.chat.id, 
            "💬 *Режим GigaChat*\n\n"
            "Напиши о своих увлечениях, я подключу ИИ!\n\n"
            "Например:\n"
            "• Люблю рисовать\n"
            "• Интересуюсь программированием\n"
            "• Хочу помогать людям",
            parse_mode="Markdown", reply_markup=markup)
        return
    
    # Режим теста
    if user_mode.get(user_id) == 'test':
        answered = sum(1 for a in user_answers[user_id] if isinstance(a, dict) and 'keywords' in a)
        if answered < len(questions):
            q = questions[answered]
            selected = None
            for opt in q['options']:
                if opt['text'].lower() in text.lower():
                    selected = opt
                    break
            
            if selected:
                user_answers[user_id].append({"keywords": selected['keywords']})
                ask_question(message.chat.id, user_id, answered + 1)
            else:
                bot.send_message(message.chat.id, "Пожалуйста, выбери вариант из кнопок 👇")
        return
    
    # Режим GigaChat
    if user_mode.get(user_id) == 'gigachat':
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Пробуем GigaChat
        giga_response = ask_gigachat(text)
        
        if giga_response:
            bot.send_message(message.chat.id, giga_response)
        else:
            # Если GigaChat не сработал, ищем в локальной базе
            bot.send_message(message.chat.id, "⚠️ GigaChat временно недоступен, ищу в своей базе...")
            found = find_professions(text)
            if found:
                response = "🔍 *Нашёл в базе:*\n\n"
                for prof in found[:3]:
                    response += format_prof(prof) + "\n—\n"
                bot.send_message(message.chat.id, response, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "🤔 Не нашёл. Попробуй иначе или /menu")
        return
    
    # Обычный режим (если вдруг)
    found = find_professions(text)
    if found:
        response = "🔍 *Нашёл в базе:*\n\n"
        for prof in found[:3]:
            response += format_prof(prof) + "\n—\n"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🤔 Не нашёл. Попробуй /menu")

# ======== ЗАПУСК ========
if __name__ == "__main__":
    print("🚀 Бот ПрофИИ с GigaChat запускается...")
    print(f"✅ Профессий: {len(professions)}")
    print("🔄 Пробую получить токен GigaChat...")
    
    # Пробуем получить токен при старте
    token = get_gigachat_token()
    if token:
        print("✅ GigaChat готов к работе!")
    else:
        print("⚠️ GigaChat пока недоступен, будет работать локальная база")
    
    bot.infinity_polling()
