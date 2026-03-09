import telebot
import json
import random
import requests
import time
import os
import uuid
from datetime import datetime, timedelta

# ======== НАСТРОЙКИ ========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"  # Вставьте свой токен

# GigaChat настройки (ваш ключ)
GIGACHAT_AUTH_KEY = "MDE5Y2QzZGYtNzFkMC03MjRlLTljNjMtZDQyYjFlNmI4ZjYyOmIwNGViNDk5LTY5MjktNDJhNi04ODc4LTQ5Y2M5OGMxZGMwNw=="
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"  # Обычно так
# ===========================

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Кэш для токенов GigaChat (токен живёт 30 минут)
gigachat_token_cache = {
    'token': None,
    'expires_at': None
}

def get_gigachat_token():
    """Получает access token для GigaChat API"""
    global gigachat_token_cache
    
    # Проверяем, есть ли ещё живой токен в кэше
    if gigachat_token_cache['token'] and gigachat_token_cache['expires_at'] > datetime.now():
        return gigachat_token_cache['token']
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        'Authorization': f'Basic {GIGACHAT_AUTH_KEY}',
        'RqUID': str(uuid.uuid4()),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {'scope': GIGACHAT_SCOPE}
    
    try:
        # Отключаем проверку SSL (нужно для GigaChat)
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        print("🔄 Получение токена GigaChat...")
        response = requests.post(url, headers=headers, data=data, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            token = result['access_token']
            expires_in = result['expires_in']  # обычно 1800 секунд (30 минут)
            
            # Сохраняем в кэш
            gigachat_token_cache['token'] = token
            gigachat_token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in - 60)  # запас 1 минута
            
            print("✅ Получен новый токен GigaChat")
            return token
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            print(f"Текст ошибки: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при получении токена: {e}")
        return None

def ask_gigachat(user_message):
    """Отправляет запрос к GigaChat и возвращает ответ"""
    
    # Получаем токен
    token = get_gigachat_token()
    if not token:
        return None
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Системный промпт для GigaChat
    system_prompt = """Ты — дружелюбный помощник по профориентации для подростков 12-15 лет по имени ПрофИИ.
Твоя задача — в непринужденной беседе выяснить интересы ребенка и предложить подходящие современные профессии.
Общайся на понятном языке, используй эмодзи, будь позитивным.
Задавай уточняющие вопросы, если нужно.
В конце предложи 2-3 профессии из списка: разработчик нейросетей, промпт-инженер, геймдизайнер, UX-дизайнер, робототехник, оператор дронов, биоинженер, специалист по кибербезопасности, врач, учитель, инженер, психолог."""
    
    payload = {
        "model": "GigaChat",  # Можно также "GigaChat-Pro" или "GigaChat-Lite"
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "repetition_penalty": 1.1
    }
    
    try:
        print(f"🔄 Отправка запроса к GigaChat...")
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            message_text = result['choices'][0]['message']['content']
            print(f"✅ Ответ получен от GigaChat")
            return message_text
        else:
            print(f"❌ Ошибка GigaChat API: {response.status_code}")
            print(f"Текст ошибки: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при запросе к GigaChat: {e}")
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
# ====================================

# ======== ХРАНИЛИЩА СОСТОЯНИЙ ========
# Хранилище ответов пользователей для теста
user_answers = {}
# Хранилище текущего режима пользователя
user_mode = {}
# ======================================

# ======== ФУНКЦИЯ ГЛАВНОГО МЕНЮ ========
def show_main_menu(chat_id):
    """Показывает главное меню с двумя кнопками"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # Создаём две большие кнопки
    btn1 = telebot.types.KeyboardButton("📋 ПРОЙТИ ТЕСТ")
    btn2 = telebot.types.KeyboardButton("💬 ОБЩЕНИЕ С GigaChat")
    
    markup.add(btn1, btn2)
    
    welcome_text = """
🚀 *Добро пожаловать в ПрофИИ!*

Я помогу тебе найти профессию мечты. Выбери, что хочешь сделать:

📋 *ПРОЙТИ ТЕСТ* — ответь на 10 вопросов, и я подберу профессии на основе твоих ответов

💬 *ОБЩЕНИЕ С GigaChat* — просто расскажи о своих увлечениях, и искусственный интеллект поможет с выбором

*Попробуй прямо сейчас!* 👇
    """
    
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)
# ========================================

# ======== РАСШИРЕННЫЙ ТЕСТ (10 ВОПРОСОВ) ========
questions = [
    {
        "id": 1,
        "text": "Какая сфера деятельности тебе ближе? (Выбери наиболее интересное)",
        "options": [
            {"text": "🧑‍⚕️ Помощь людям, забота о здоровье", "keywords": ["врач", "ветеринар", "психолог", "медицина", "забота"]},
            {"text": "📚 Образование, передача знаний", "keywords": ["учитель", "педагогика", "образование", "обучение"]},
            {"text": "💻 Информационные технологии, программирование", "keywords": ["программирование", "нейросети", "разработчик", "it", "код"]},
            {"text": "🏗️ Строительство, создание объектов", "keywords": ["инженер", "строитель", "архитектура", "конструировать"]}
        ]
    },
    {
        "id": 2,
        "text": "Какой стиль работы тебе подходит больше?",
        "options": [
            {"text": "🎯 Работа с людьми, общение, помощь", "keywords": ["врач", "учитель", "психолог", "продавец", "общение"]},
            {"text": "🧠 Интеллектуальная работа, анализ, исследования", "keywords": ["нейросети", "аналитика", "исследования", "данные", "наука"]},
            {"text": "✋ Практическая работа руками, создание чего-то", "keywords": ["повар", "электрик", "парикмахер", "инженер", "строитель"]},
            {"text": "🎨 Творчество, создание нового, дизайн", "keywords": ["дизайн", "креатив", "искусство", "творчество"]}
        ]
    },
    {
        "id": 3,
        "text": "Какие школьные предметы тебе нравятся больше всего? (Выбери самый любимый)",
        "options": [
            {"text": "🔬 Биология, химия", "keywords": ["врач", "ветеринар", "биоинженерия", "медицина"]},
            {"text": "🧮 Математика, физика", "keywords": ["инженер", "программирование", "нейросети", "строитель", "электрик"]},
            {"text": "💻 Информатика", "keywords": ["программирование", "нейросети", "разработчик", "it"]},
            {"text": "📖 Литература, русский язык, история", "keywords": ["учитель", "юрист", "писатель", "психолог"]},
            {"text": "🎨 Рисование, технология", "keywords": ["дизайн", "архитектура", "парикмахер", "повар"]}
        ]
    },
    {
        "id": 4,
        "text": "Какая у тебя суперсила? (Твоя главная черта характера)",
        "options": [
            {"text": "💪 Ответственность и надёжность", "keywords": ["врач", "учитель", "инженер", "электрик", "водитель"]},
            {"text": "🤝 Коммуникабельность, легко нахожу общий язык", "keywords": ["продавец", "психолог", "учитель", "юрист"]},
            {"text": "🔍 Внимательность к деталям", "keywords": ["аналитик", "разработчик", "юрист", "электрик"]},
            {"text": "💡 Креативность, придумываю новое", "keywords": ["дизайн", "повар", "архитектор", "креативный продюсер"]},
            {"text": "🧠 Логическое мышление", "keywords": ["программист", "инженер", "нейросети", "аналитика"]}
        ]
    },
    {
        "id": 5,
        "text": "Какую рабочую обстановку ты предпочитаешь?",
        "options": [
            {"text": "🏥 В офисе, больнице, школе (работа с людьми)", "keywords": ["врач", "учитель", "психолог", "юрист"]},
            {"text": "🏗️ На улице, на объектах, в разъездах", "keywords": ["строитель", "водитель", "инженер", "электрик"]},
            {"text": "💻 За компьютером, удалённо", "keywords": ["программист", "дизайн", "нейросети", "аналитика"]},
            {"text": "🍳 В мастерской, на кухне, в студии", "keywords": ["повар", "парикмахер", "художник"]}
        ]
    },
    {
        "id": 6,
        "text": "Что для тебя важно в будущей профессии?",
        "options": [
            {"text": "💰 Высокий доход", "keywords": ["программист", "нейросети", "юрист", "разработчик"]},
            {"text": "❤️ Помощь людям, польза обществу", "keywords": ["врач", "учитель", "ветеринар", "психолог"]},
            {"text": "🎨 Творческая самореализация", "keywords": ["дизайн", "повар", "парикмахер", "креативный продюсер"]},
            {"text": "🛡️ Стабильность и надёжность", "keywords": ["учитель", "врач", "инженер", "электрик"]}
        ]
    },
    {
        "id": 7,
        "text": "Как ты любишь решать проблемы?",
        "options": [
            {"text": "📚 Ищу информацию, анализирую", "keywords": ["аналитик", "юрист", "исследователь", "нейросети"]},
            {"text": "🤔 Думаю логически, ищу алгоритм", "keywords": ["программист", "инженер", "электрик"]},
            {"text": "💬 Обсуждаю с другими, советуюсь", "keywords": ["психолог", "учитель", "менеджер"]},
            {"text": "🛠️ Пробую на практике, экспериментирую", "keywords": ["повар", "инженер", "строитель", "электрик"]}
        ]
    },
    {
        "id": 8,
        "text": "Какие у тебя хобби? (Что делаешь в свободное время)",
        "options": [
            {"text": "🎮 Играю в компьютерные игры", "keywords": ["геймдизайнер", "разработчик", "киберспорт", "тестировщик"]},
            {"text": "📚 Читаю книги, изучаю новое", "keywords": ["учитель", "юрист", "психолог", "исследователь"]},
            {"text": "🎨 Рисую, фотографирую, монтирую", "keywords": ["дизайн", "креативный продюсер", "архитектор"]},
            {"text": "🔧 Мастерю, собираю, чиню", "keywords": ["инженер", "электрик", "робототехник"]},
            {"text": "🏃 Занимаюсь спортом", "keywords": ["учитель физкультуры", "тренер"]}
        ]
    },
    {
        "id": 9,
        "text": "Какие профессии будущего тебе кажутся интересными?",
        "options": [
            {"text": "🤖 Работа с ИИ и нейросетями", "keywords": ["нейросети", "промпт-инженер", "разработчик", "ai"]},
            {"text": "🚁 Дроны и роботы", "keywords": ["робототехник", "дроны", "оператор бпла"]},
            {"text": "🧬 Биотехнологии и медицина", "keywords": ["биоинженер", "врач", "ветеринар"]},
            {"text": "🌱 Экология и устойчивое развитие", "keywords": ["эколог", "биолог"]}
        ]
    },
    {
        "id": 10,
        "text": "Кем ты видишь себя через 15 лет?",
        "options": [
            {"text": "👨‍🏫 Уважаемый профессионал, эксперт в своём деле", "keywords": ["врач", "учитель", "инженер", "юрист"]},
            {"text": "🚀 Создаю инновации, работаю в новой сфере", "keywords": ["нейросети", "разработчик", "робототехник", "биоинженерия"]},
            {"text": "👩‍🎨 Занимаюсь творчеством, создаю красоту", "keywords": ["дизайн", "архитектор", "повар", "парикмахер"]},
            {"text": "🤝 Руковожу командой, управляю проектами", "keywords": ["менеджер", "продюсер", "директор"]}
        ]
    }
]
# =================================================

# ======== ФУНКЦИЯ ПОИСКА ПРОФЕССИЙ ========
def find_professions_by_keywords(user_text):
    """Ищет профессии по ключевым словам в тексте"""
    user_text_lower = user_text.lower()
    found = []
    
    for prof in professions:
        for keyword in prof['keywords']:
            if keyword.lower() in user_text_lower:
                if prof not in found:
                    found.append(prof)
                break
    
    return found
# ==========================================

# ======== ФУНКЦИЯ ФОРМАТИРОВАНИЯ ПРОФЕССИИ ========
def format_profession(prof):
    return f"""
🔹 *{prof['name']}*

{prof['description']}

📚 *Предметы:* {', '.join(prof['school_subjects'])}
🔧 *Навыки:* {', '.join(prof['skills'])}
💰 *Зарплата:* {prof['salary']}

✨ {prof['trend']}

🎓 *Курс:* {prof['courses'][0]}
    """
# ==================================================

# ======== КОМАНДА /START ========
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []  # Очищаем состояние теста
    user_mode[user_id] = 'menu'  # Устанавливаем режим меню
    
    # Показываем главное меню
    show_main_menu(message.chat.id)

# ======== КОМАНДА /TEST ========
@bot.message_handler(commands=['test'])
def test_command(message):
    user_id = message.from_user.id
    # Полностью очищаем предыдущие ответы
    user_answers[user_id] = []
    user_mode[user_id] = 'test'  # Устанавливаем режим теста
    
    bot.send_message(message.chat.id, "📋 *Начинаем тест!*", parse_mode="Markdown")
    ask_question(message.chat.id, user_id, 0)

# ======== КОМАНДА /MENU ========
@bot.message_handler(commands=['menu'])
def menu_command(message):
    """Возвращает в главное меню"""
    user_id = message.from_user.id
    user_answers[user_id] = []  # Очищаем состояние теста
    user_mode[user_id] = 'menu'  # Устанавливаем режим меню
    show_main_menu(message.chat.id)

# ======== ФУНКЦИЯ ЗАДАНИЯ ВОПРОСА ========
def ask_question(chat_id, user_id, question_index):
    if question_index < len(questions):
        q = questions[question_index]
        text = f"*Вопрос {question_index + 1} из {len(questions)}*\n\n{q['text']}"
        
        # СОЗДАЁМ КЛАВИАТУРУ С КНОПКАМИ
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for opt in q['options']:
            markup.add(telebot.types.KeyboardButton(opt['text']))
        
        # Добавляем кнопку возврата в меню
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        
        # Отправляем сообщение с клавиатурой
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    else:
        # Вопросы закончились - показываем результат
        show_result(chat_id, user_id)

# ======== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    
    # Инициализируем режим пользователя, если его нет
    if user_id not in user_mode:
        user_mode[user_id] = 'menu'
    
    # Обработка кнопки "В меню"
    if user_text == "🏠 В меню":
        user_answers[user_id] = []  # Очищаем состояние теста
        user_mode[user_id] = 'menu'  # Устанавливаем режим меню
        show_main_menu(message.chat.id)
        return
    
    # Обработка кнопок главного меню
    if user_text == "📋 ПРОЙТИ ТЕСТ":
        test_command(message)
        return
    
    if user_text == "💬 ОБЩЕНИЕ С GigaChat":
        # Переходим в режим общения с GigaChat
        user_answers[user_id] = []  # Очищаем состояние теста
        user_mode[user_id] = 'gigachat'  # Устанавливаем режим GigaChat
        
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("🏠 В меню"))
        
        bot.send_message(message.chat.id, 
            "💬 *Режим общения с GigaChat*\n\n"
            "Просто напиши мне о своих увлечениях, и я помогу подобрать профессию!\n\n"
            "Например:\n"
            "• \"Я люблю рисовать и монтировать видео\"\n"
            "• \"Мне нравится программировать\"\n"
            "• \"Хочу помогать животным\"\n"
            "• \"Интересуюсь дронами\"\n\n"
            "Чтобы вернуться в меню, нажми кнопку ниже 👇",
            parse_mode="Markdown", reply_markup=markup)
        return
    
    # Проверяем, находится ли пользователь в режиме теста
    if user_mode.get(user_id) == 'test' and user_id in user_answers:
        # Считаем, сколько ответов уже дано
        answered_count = 0
        for item in user_answers[user_id]:
            if isinstance(item, dict) and 'keywords' in item:
                answered_count += 1
        
        # Если тест ещё не завершён
        if answered_count < len(questions):
            # Получаем текущий вопрос
            current_q_index = answered_count
            if current_q_index < len(questions):
                q = questions[current_q_index]
                
                # Проверяем, есть ли текст ответа среди вариантов
                selected = None
                for opt in q['options']:
                    if opt['text'].lower() in user_text.lower() or user_text.lower() in opt['text'].lower():
                        selected = opt
                        break
                
                if selected:
                    # Сохраняем ответ с ключевыми словами
                    user_answers[user_id].append({"keywords": selected['keywords']})
                    # Задаём следующий вопрос
                    ask_question(message.chat.id, user_id, answered_count + 1)
                else:
                    bot.send_message(message.chat.id, 
                        "Пожалуйста, выбери один из предложенных вариантов, нажав на кнопку 👇")
                return
    
    # Если пользователь в режиме GigaChat или меню (не в тесте) — используем GigaChat
    if user_mode.get(user_id) in ['gigachat', 'menu']:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Пробуем получить ответ от GigaChat
        gpt_response = ask_gigachat(user_text)
        
        if gpt_response:
            bot.send_message(message.chat.id, gpt_response)
        else:
            # Если GigaChat не работает, ищем в локальной базе
            found = find_professions_by_keywords(user_text)
            if found:
                response = "🔍 *Нашёл в локальной базе:*\n\n"
                for prof in found[:3]:
                    response += format_profession(prof)
                    response += "\n" + "—" * 30 + "\n"
                bot.send_message(message.chat.id, response, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, 
                    "🤔 Не нашёл подходящих профессий. Расскажи подробнее о своих увлечениях!\n\n"
                    "Чтобы вернуться в меню, нажми /menu или кнопку '🏠 В меню'")

# ======== ФУНКЦИЯ ПОКАЗА РЕЗУЛЬТАТОВ ТЕСТА ========
def show_result(chat_id, user_id):
    # Убираем клавиатуру
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("🏠 В меню"))
    
    bot.send_message(chat_id, "🔍 *Анализирую твои ответы...*", parse_mode="Markdown", reply_markup=markup)
    
    # Собираем ключевые слова из ответов
    answers = user_answers.get(user_id, [])
    all_keywords = []
    for a in answers:
        if isinstance(a, dict) and 'keywords' in a:
            all_keywords.extend(a['keywords'])
    
    # Считаем баллы для профессий
    scores = []
    for prof in professions:
        score = 0
        for kw in all_keywords:
            if kw.lower() in [k.lower() for k in prof['keywords']]:
                score += 1
        scores.append((prof, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    top = [prof for prof, score in scores[:3] if score > 0]
    
    if not top:
        top = random.sample(professions, 3)
    
    for prof in top:
        bot.send_message(chat_id, format_profession(prof), parse_mode="Markdown")
    
    bot.send_message(chat_id, 
        "✅ *Тест пройден!*\n\n"
        "Ты можешь:\n"
        "• Пройти тест ещё раз — /test\n"
        "• Пообщаться с GigaChat — просто напиши сообщение\n"
        "• Вернуться в меню — /menu",
        parse_mode="Markdown")
    
    # После завершения теста возвращаем в меню
    user_mode[user_id] = 'menu'

# ======== ЗАПУСК БОТА ========
if __name__ == "__main__":
    print("🚀 Бот ПрофИИ запускается...")
    print(f"✅ Загружено профессий: {len(professions)}")
    print("✅ GigaChat настроен")
    bot.infinity_polling()
