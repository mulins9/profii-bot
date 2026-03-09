import telebot
import json
import random
import os
import time
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

# ======== НАСТРОЙКИ ========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"

# GigaChat настройки (ваш ключ)
GIGACHAT_CREDENTIALS = "MDE5Y2QzZGYtNzFkMC03MjRlLTljNjMtZDQyYjFlNmI4ZjYyOmIwNGViNDk5LTY5MjktNDJhNi04ODc4LTQ5Y2M5OGMxZGMwNw=="
# ===========================

bot = telebot.TeleBot(TELEGRAM_TOKEN)

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

# Хранилища состояний пользователей
user_answers = {}  # для ответов на тест
user_mode = {}     # для режима: 'menu', 'test', 'gigachat'

# ======== ФУНКЦИЯ ЗАПРОСА К GIGACHAT ========
def ask_gigachat(user_message):
    """Отправляет запрос к GigaChat и возвращает ответ"""
    try:
        print("🔄 Подключение к GigaChat...")
        
        # Создаём клиента с отключённой проверкой SSL
        with GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
            verify_ssl_certs=False,
            timeout=60,
            model="GigaChat"
        ) as client:
            
            # Системный промпт
            system_prompt = """Ты — дружелюбный помощник по профориентации для подростков 12-15 лет по имени ПрофИИ.
Твоя задача — в непринужденной беседе выяснить интересы ребенка и предложить подходящие современные профессии.
Общайся на понятном языке, используй эмодзи, будь позитивным.
Задавай уточняющие вопросы, если нужно.
В конце предложи 2-3 профессии из списка: разработчик нейросетей, промпт-инженер, геймдизайнер, UX-дизайнер, робототехник, оператор дронов, биоинженер, специалист по кибербезопасности, врач, учитель, инженер, психолог."""
            
            # Формируем сообщения
            messages = [
                Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                Messages(role=MessagesRole.USER, content=user_message)
            ]
            
            # Отправляем запрос
            response = client.chat(messages)
            
            if response and response.choices:
                answer = response.choices[0].message.content
                print(f"✅ Получен ответ от GigaChat")
                return answer
            else:
                print("❌ Пустой ответ от GigaChat")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка GigaChat: {e}")
        return None
# ============================================

# ======== ФУНКЦИЯ ГЛАВНОГО МЕНЮ ========
def show_main_menu(chat_id):
    """Показывает главное меню с двумя кнопками"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
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
    user_answers[user_id] = []
    user_mode[user_id] = 'menu'
    show_main_menu(message.chat.id)

# ======== КОМАНДА /TEST ========
@bot.message_handler(commands=['test'])
def test_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'test'
    bot.send_message(message.chat.id, "📋 *Начинаем тест!*", parse_mode="Markdown")
    ask_question(message.chat.id, user_id, 0)

# ======== КОМАНДА /MENU ========
@bot.message_handler(commands=['menu'])
def menu_command(message):
    user_id = message.from_user.id
    user_answers[user_id] = []
    user_mode[user_id] = 'menu'
    show_main_menu(message.chat.id)

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
    
    if user_text == "💬 ОБЩЕНИЕ С GigaChat":
        user_answers[user_id] = []
        user_mode[user_id] = 'gigachat'
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
    
    # Режим теста
    if user_mode.get(user_id) == 'test' and user_id in user_answers:
        answered_count = sum(1 for item in user_answers[user_id] if isinstance(item, dict) and 'keywords' in item)
        
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
                bot.send_message(message.chat.id, "Пожалуйста, выбери один из предложенных вариантов, нажав на кнопку 👇")
            return
    
    # Режим GigaChat или меню
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
                    "🤔 Не нашёл подходящих профессий. Расскажи подробнее о своих увлечениях!\n\n"
                    "Чтобы вернуться в меню, нажми /menu или кнопку '🏠 В меню'")

# ======== ФУНКЦИЯ ПОКАЗА РЕЗУЛЬТАТОВ ТЕСТА ========
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
    
    bot.send_message(chat_id, 
        "✅ *Тест пройден!*\n\n"
        "Ты можешь:\n"
        "• Пройти тест ещё раз — /test\n"
        "• Пообщаться с GigaChat — просто напиши сообщение\n"
        "• Вернуться в меню — /menu",
        parse_mode="Markdown")
    
    user_mode[user_id] = 'menu'

# ======== ЗАПУСК БОТА ========
if __name__ == "__main__":
    print("🚀 Бот ПрофИИ запускается...")
    print(f"✅ Загружено профессий: {len(professions)}")
    print("✅ GigaChat настроен")
    print("❓ Если GigaChat не работает, бот будет использовать локальную базу")
    bot.infinity_polling()
