import telebot
import json
import random
import requests
import time
import os

# ======== НАСТРОЙКИ ========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"  # Вставьте свой токен

# Yandex GPT настройки (нужно заполнить!)
YANDEX_API_KEY = "AQVNx605HheWLBkKgGoc3ROIT_4bCUI8qMnYeWGk"  # Вставьте API-ключ
YANDEX_FOLDER_ID = "b1gggr7mfpg3htc999vb"  # Вставьте ID папки
YANDEX_GPT_MODEL = "yandexgpt-lite"  # Можно использовать "yandexgpt" для более мощной версии
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

# ======== ФУНКЦИЯ ЗАПРОСА К YANDEX GPT ========
def ask_yandex_gpt(user_message):
    """Отправляет запрос к Yandex GPT и возвращает ответ"""
    
    # Проверяем, заполнены ли ключи
    if YANDEX_API_KEY == "ВАШ_API_КЛЮЧ_ОТ_YANDEX_CLOUD" or YANDEX_FOLDER_ID == "ВАШ_FOLDER_ID":
        return "⚠️ Yandex GPT не настроен. Использую локальную базу профессий."
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    # Системный промпт для GPT
    system_prompt = """Ты — дружелюбный помощник по профориентации для подростков 12-15 лет по имени ПрофИИ.
Твоя задача — в непринужденной беседе выяснить интересы ребенка и предложить подходящие современные профессии.
Общайся на понятном языке, используй эмодзи, будь позитивным.
Задавай уточняющие вопросы, если нужно.
В конце предложи 2-3 профессии из списка: разработчик нейросетей, промпт-инженер, геймдизайнер, UX-дизайнер, робототехник, оператор дронов, биоинженер, специалист по кибербезопасности, врач, учитель, инженер, психолог."""
    
    # Подготавливаем данные для запроса
    prompt_data = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_GPT_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {
                "role": "system",
                "text": system_prompt
            },
            {
                "role": "user",
                "text": user_message
            }
        ]
    }
    
    # Отправляем запрос
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }
    
    try:
        print(f"🔄 Отправка запроса к Yandex GPT...")
        response = requests.post(url, headers=headers, json=prompt_data)
        
        if response.status_code == 200:
            result = response.json()
            message_text = result['result']['alternatives'][0]['message']['text']
            print(f"✅ Ответ получен от Yandex GPT")
            return message_text
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"Текст ошибки: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при запросе к Yandex GPT: {e}")
        return None
# ===============================================

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



# Хранилище ответов пользователей
user_answers = {}

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
    
    # Убираем клавиатуру, если она была
    markup = telebot.types.ReplyKeyboardRemove()
    
    welcome = """
🚀 *Привет! Я ПрофИИ — твой навигатор в мире профессий!*

Я использую **Yandex GPT** (искусственный интеллект) и базу из 30+ профессий, чтобы помочь тебе найти своё призвание.

Напиши мне о своих увлечениях, и я предложу подходящие профессии!

Например:
• "Люблю играть в игры"
• "Интересуюсь нейросетями"
• "Хочу помогать людям"
• "Нравится рисовать"

Или нажми /test, чтобы пройти тест.
    """
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=markup)

# ======== КОМАНДА /TEST ========
@bot.message_handler(commands=['test'])
def test_command(message):
    user_id = message.from_user.id
    # Полностью очищаем предыдущие ответы
    user_answers[user_id] = []
    
    bot.send_message(message.chat.id, "📋 *Начинаем тест!*", parse_mode="Markdown")
    ask_question(message.chat.id, user_id, 0)

def ask_question(chat_id, user_id, question_index):
    if question_index < len(questions):
        q = questions[question_index]
        text = f"*Вопрос {question_index + 1} из {len(questions)}*\n\n{q['text']}"
        
        # СОЗДАЁМ КЛАВИАТУРУ С КНОПКАМИ
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for opt in q['options']:
            markup.add(telebot.types.KeyboardButton(opt['text']))
        
        # Отправляем сообщение с клавиатурой
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    else:
        # Вопросы закончились - показываем результат
        show_result(chat_id, user_id)

# ======== ОБРАБОТКА СООБЩЕНИЙ ========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    
    # Проверяем, является ли сообщение командой
    if user_text.startswith('/'):
        # Команды обрабатываются отдельными хэндлерами
        return
    
    # Проверяем, находится ли пользователь в режиме теста
    if user_id in user_answers:
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
    
    # Если пользователь НЕ в режиме теста — используем Yandex GPT
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Пробуем получить ответ от Yandex GPT
    gpt_response = ask_yandex_gpt(user_text)
    
    if gpt_response:
        bot.send_message(message.chat.id, gpt_response)
    else:
        # Если GPT не работает, ищем в локальной базе
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
                "Или попробуй пройти тест: /test")
def show_result(chat_id, user_id):
    markup = telebot.types.ReplyKeyboardRemove()
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
    
    bot.send_message(chat_id, "🔄 Хочешь пройти тест еще раз? Нажми /test")

# ======== ЗАПУСК БОТА ========
if __name__ == "__main__":
    print("🚀 Бот ПрофИИ запускается...")
    print(f"✅ Загружено профессий: {len(professions)}")
    print("✅ Yandex GPT " + ("настроен" if YANDEX_API_KEY != "ВАШ_API_КЛЮЧ_ОТ_YANDEX_CLOUD" else "НЕ настроен"))
    bot.infinity_polling()
