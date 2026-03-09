import telebot
import json
import random
import os

# ВНИЗУ файла, после всего кода, но перед bot.infinity_polling()
# Замените старый запуск (bot.infinity_polling()) на ЭТО:

if __name__ == "__main__":
    # Эта часть не будет выполняться на Render
    # На Render бот запускается через app.py
    print("🤖 Бот запускается локально...")
    bot.infinity_polling()


# ======== НАСТРОЙКИ ========
TELEGRAM_TOKEN = "8776463968:AAEPkERlkvBuN9WsKZ9FlqVpeOa0PET5Euc"  # ВСТАВЬТЕ СВОЙ ТОКЕН
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


# Хранилище ответов пользователей (временное)
user_answers = {}

# ======== ФУНКЦИЯ ПОДСЧЕТА РЕЗУЛЬТАТОВ ========
# ======== УЛУЧШЕННАЯ ФУНКЦИЯ ПОДСЧЕТА РЕЗУЛЬТАТОВ ========
def calculate_result(user_id):
    """Анализирует ответы пользователя и подбирает профессии с весовыми коэффициентами"""
    
    # Получаем все ответы пользователя
    answers = user_answers.get(user_id, [])
    
    if len(answers) < len(questions):
        return random.sample(professions, min(3, len(professions)))
    
    # Собираем все ключевые слова из ответов
    all_keywords = []
    for answer in answers:
        if isinstance(answer, dict) and 'keywords' in answer:
            all_keywords.extend(answer['keywords'])
    
    print(f"📊 Ключевые слова пользователя: {all_keywords}")
    
    # Словарь для подсчета баллов по профессиям
    profession_scores = {}
    
    # Для каждой профессии считаем баллы
    for prof in professions:
        score = 0
        prof_keywords = [kw.lower() for kw in prof['keywords']]
        
        for keyword in all_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in prof_keywords:
                score += 2  # Прямое совпадение даёт 2 балла
            else:
                # Проверяем частичные совпадения (например, "программист" и "программирование")
                for prof_kw in prof_keywords:
                    if keyword_lower in prof_kw or prof_kw in keyword_lower:
                        score += 1
                        break
        
        # Дополнительные баллы за особые комбинации (можно настроить под свои профессии)
        
        profession_scores[prof['name']] = {
            'profession': prof,
            'score': score
        }
    
    # Сортируем по баллам
    sorted_professions = sorted(
        profession_scores.values(), 
        key=lambda x: x['score'], 
        reverse=True
    )
    
    # Отладочный вывод топ-5 профессий
    print("🏆 Топ-5 профессий по баллам:")
    for i, item in enumerate(sorted_professions[:5]):
        print(f"   {i+1}. {item['profession']['name']}: {item['score']} баллов")
    
    # Берём топ-3 профессии
    top_professions = [item['profession'] for item in sorted_professions[:3]]
    
    # Если баллы слишком низкие, добавляем случайные
    if all(item['score'] < 3 for item in sorted_professions[:3]):
        print("⚠️ Баллы низкие, добавляем случайные профессии")
        random_profs = random.sample(professions, 2)
        top_professions = top_professions + random_profs
        top_professions = list({p['name']: p for p in top_professions}.values())[:3]
    
    return top_professions
# ========================================================


# ======== ФУНКЦИЯ ФОРМАТИРОВАНИЯ ПРОФЕССИИ ========
def format_profession(prof):
    return f"""
🔹 *{prof['name']}*

{prof['description']}

📚 *Школьные предметы:* {', '.join(prof['school_subjects'])}
🔧 *Навыки:* {', '.join(prof['skills'])}
💰 *Зарплата:* {prof['salary']}

✨ {prof['trend']}

🎓 *Где учиться:* {prof['courses'][0]}
    """
# ==================================================

# ======== КОМАНДА /START ========
@bot.message_handler(commands=['start'])
def start_test(message):
    user_id = message.from_user.id
    user_answers[user_id] = []  # Очищаем старые ответы
    
    welcome_text = """
🚀 *Привет! Я ПрофИИ — твой персональный навигатор в мире профессий!*

Я проведу для тебя небольшой тест из 5 вопросов и на основе твоих ответов подберу профессии будущего, которые тебе подойдут.

Готов? Поехали! 🎯
    """
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    
    # Задаем первый вопрос
    ask_question(message.chat.id, user_id, 0)

# ======== ФУНКЦИЯ ЗАДАНИЯ ВОПРОСА ========
def ask_question(chat_id, user_id, question_index):
    if question_index < len(questions):
        question = questions[question_index]
        
        # Формируем текст вопроса
        text = f"*Вопрос {question_index + 1} из {len(questions)}*\n\n{question['text']}"
        
        # Создаем клавиатуру с вариантами ответов
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        
        for option in question['options']:
            button = telebot.types.KeyboardButton(option['text'])
            markup.add(button)
        
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
        
        # Сохраняем индекс текущего вопроса для пользователя
        user_answers[user_id].append({"question_index": question_index})
    else:
        # Вопросы закончились - показываем результат
        show_result(chat_id, user_id)

# ======== ОБРАБОТКА ОТВЕТОВ ========
@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    user_id = message.from_user.id
    user_text = message.text
    
    # Проверяем, есть ли пользователь в хранилище
    if user_id not in user_answers:
        bot.send_message(message.chat.id, "Напиши /start чтобы начать тест заново")
        return
    
    # Определяем, на какой вопрос отвечают
    user_data = user_answers[user_id]
    answered_questions = len([a for a in user_data if isinstance(a, dict) and 'keywords' in a])
    current_question_index = answered_questions
    
    if current_question_index >= len(questions):
        show_result(message.chat.id, user_id)
        return
    
    # Ищем выбранный вариант в текущем вопросе
    question = questions[current_question_index]
    selected_option = None
    
    for option in question['options']:
        if option['text'].lower() in user_text.lower() or user_text.lower() in option['text'].lower():
            selected_option = option
            break
    
    if selected_option:
        # Сохраняем ответ с ключевыми словами
        user_answers[user_id].append({
            "question_index": current_question_index,
            "keywords": selected_option['keywords']
        })
        
        # Задаем следующий вопрос
        ask_question(message.chat.id, user_id, answered_questions + 1)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выбери один из вариантов ответа 👇")

# ======== ПОКАЗ РЕЗУЛЬТАТА ========
def show_result(chat_id, user_id):
    # Убираем клавиатуру
    markup = telebot.types.ReplyKeyboardRemove()
    
    bot.send_message(chat_id, "🔍 *Анализирую твои ответы...*", parse_mode="Markdown", reply_markup=markup)
    
    # Получаем подходящие профессии
    top_professions = calculate_result(user_id)
    
    # Отправляем результат
    result_text = "🎉 *Профессии, которые тебе подходят:*\n\n"
    bot.send_message(chat_id, result_text, parse_mode="Markdown")
    
    for prof in top_professions:
        bot.send_message(chat_id, format_profession(prof), parse_mode="Markdown")
    
    # Предлагаем пройти тест заново
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton("/start"))
    bot.send_message(chat_id, "🔄 Хочешь пройти тест еще раз? Нажми /start", reply_markup=markup)

# ======== ЗАПУСК БОТА ========
if __name__ == "__main__":
    print("🤖 Бот-тест ПрофИИ запущен!")
    bot.infinity_polling()