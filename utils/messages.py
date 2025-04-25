from typing import Dict, Any


# Словари сообщений для каждого языка
MESSAGES = {
    "ru": {
        # Общие сообщения
        "banned_user": "❌ Вы заблокированы и не можете использовать бота Шәкәрім Университет. Обратитесь в службу поддержки для решения проблемы. ❌",
        "exit_chat_first": "⚠️ Напишите /stop, чтобы выйти из состояния чата Шәкәрім Университет. ⚠️",
        "welcome": "👋 Добро пожаловать в Шәкәрім Университет Support Bot! 🎓\n\n📱 Техническая поддержка: @MDS124578\n⏰ Время работы: 9:00-18:00\n🍽️ Обед: 13:00-14:00\n\n📋 Выберите опцию из меню:",
        "select_option": "📋 Выберите опцию из меню Шәкәрім Университет:",
        
        # Сообщения выбора языка
        "select_language": "🌐 Пожалуйста, выберите язык / Тілді таңдаңыз / Please select a language:",
        "language_selected": "✅ Выбран русский язык. Шәкәрім Университет приветствует вас! 🎓",
        
        # Сообщения регистрации
        "already_registered": "📝 Вы уже зарегистрированы в системе Шәкәрім Университет.",
        "enter_name": "👤 Пожалуйста, введите ваше полное имя для регистрации в Шәкәрім Университет:",
        "enter_email": "📧 Пожалуйста, введите ваш email для связи с Шәкәрім Университет:",
        "registration_successful": "🎉 Регистрация в Шәкәрім Университет успешно завершена! 🎉",
        "registration_cancelled": "🚫 Регистрация в Шәкәрім Университет отменена.",
        
        # FAQ
        "faq_title": "❓ Часто задаваемые вопросы Шәкәрім Университет:",
        "back_to_list": "⬅️ Назад к списку",
        "faq_question_prompt": "🔢 Напишите номер вопроса о Шәкәрім Университет, который подходит для вас:",
        "question_not_found": "❓ Вопрос с таким номером не найден. Пожалуйста, выберите номер из списка вопросов Шәкәрім Университет.",
        
        # Вопросы
        "ask_question": "❓ Пожалуйста, напишите ваш вопрос о Шәкәрім Университет:",
        "question_sent": "📤 Ваш вопрос отправлен администраторам Шәкәрім Университет. Мы ответим вам в ближайшее время. ⏳",
        "question_cancelled": "🚫 Отправка вопроса в Шәкәрім Университет отменена.",
        "question_accepted": "✅ Ваш вопрос #{} принят! Ожидайте ответа от сотрудников Офиса Регистратуры Шәкәрім Университет. ⏳",
        "question_answer_received": "📬 Ответ на ваш вопрос #{}:\n\n❓ Вопрос:\n{}\n\n✅ Ответ от {} (Шәкәрім Университет):\n{}\n\n📱 Чтобы открыть меню напишите /start",
        
        # Чат
        "chat_intro": "💬 Вы запросили чат с администратором Шәкәрім Университет. Пожалуйста, ожидайте подключения... ⏳",
        "chat_connected": "🔗 Администратор Шәкәрім Университет подключился. Вы можете начать общение. 💬",
        "chat_disconnected": "🔌 Администратор Шәкәрім Университет отключился. Чат завершен. 👋",
        "chat_waiting": "⏳ Ожидание подключения администратора Шәкәрім Университет... 💬",
        "chat_stopped": "🛑 Чат с Шәкәрім Университет остановлен.",
        "waiting_for_connection": "⏳ Подождите, пожалуйста! Пытаемся связаться с сотрудником Шәкәрім Университет. Напишите /stop, чтобы отменить. 🔄",
        "connection_terminated_by_user": "🛑 Связь с Шәкәрім Университет прервана вами! Напишите /start, чтобы продолжить использовать бота. 🔄",
        "admin_connected": "👨‍💼 Администратор Шәкәрім Университет: {}\n\n🔗 С вами связались! Можете писать в чат, чтобы общаться. Напишите /stop, чтобы завершить. 💬",
        "connecting": "🔄 Устанавливаем активное соединение с Шәкәрім Университет...",
        "connection_terminated_by_admin": "🔌 Связь с сотрудником Шәкәрім Университет прервана ответчиком! Напишите /start, чтобы продолжить использовать бота. 🔄",
        "connection_terminated_forcibly": "⚠️ Связь с Шәкәрім Университет была прервана принудительно!\n\n📱 Напишите /start чтобы продолжить. 🔄",
    },
    
    "kz": {
        # Общие сообщения
        "banned_user": "❌ Сіз блокталдыңыз және Шәкәрім Университеті ботын қолдана алмайсыз. Мәселені шешу үшін қолдау қызметіне хабарласыңыз. ❌",
        "exit_chat_first": "⚠️ Шәкәрім Университеті сөйлесу режимінен шығу үшін /stop жазыңыз. ⚠️",
        "welcome": "👋 Шәкәрім Университеті Support Bot-қа қош келдіңіз! 🎓\n\n📱 Техникалық қолдау: @MDS124578\n⏰ Жұмыс уақыты: 9:00-18:00\n🍽️ Түскі ас: 13:00-14:00\n\n📋 Мәзірден опцияны таңдаңыз:",
        "select_option": "📋 Шәкәрім Университеті мәзірінен опцияны таңдаңыз:",
        
        # Сообщения выбора языка
        "select_language": "🌐 Пожалуйста, выберите язык / Тілді таңдаңыз / Please select a language:",
        "language_selected": "✅ Қазақ тілі таңдалды. Шәкәрім Университеті сізді құттықтайды! 🎓",
        
        # Сообщения регистрации
        "already_registered": "📝 Сіз Шәкәрім Университеті жүйесінде тіркелгенсіз.",
        "enter_name": "👤 Шәкәрім Университетіне тіркелу үшін толық атыңызды енгізіңіз:",
        "enter_email": "📧 Шәкәрім Университетімен байланысу үшін email енгізіңіз:",
        "registration_successful": "🎉 Шәкәрім Университетіне тіркеу сәтті аяқталды! 🎉",
        "registration_cancelled": "🚫 Шәкәрім Университетіне тіркелу тоқтатылды.",
        
        # FAQ
        "faq_title": "❓ Шәкәрім Университеті жиі қойылатын сұрақтар:",
        "back_to_list": "⬅️ Тізімге оралу",
        "faq_question_prompt": "🔢 Шәкәрім Университеті туралы сізге қолайлы сұрақтың нөмірін жазыңыз:",
        "question_not_found": "❓ Мұндай нөмірмен сұрақ табылмады. Шәкәрім Университеті сұрақтар тізімінен нөмірді таңдаңыз.",
        
        # Вопросы
        "ask_question": "❓ Шәкәрім Университеті туралы сұрағыңызды жазыңыз:",
        "question_sent": "📤 Сұрағыңыз Шәкәрім Университеті әкімшілеріне жіберілді. Жақын арада жауап береміз. ⏳",
        "question_cancelled": "🚫 Шәкәрім Университетіне сұрақты жіберу тоқтатылды.",
        "question_accepted": "✅ Сіздің #{} сұрағыңыз қабылданды! Шәкәрім Университеті Тіркеу кеңсесі қызметкерлерінен жауап күтіңіз. ⏳",
        "question_answer_received": "📬 Сіздің #{} сұрағыңызға жауап:\n\n❓ Сұрақ:\n{}\n\n✅ {} (Шәкәрім Университеті) жауабы:\n{}\n\n📱 Мәзірді ашу үшін /start жазыңыз",
        
        # Чат
        "chat_intro": "💬 Сіз Шәкәрім Университеті әкімшімен сөйлесуді сұрадыңыз. Қосылуды күтіңіз... ⏳",
        "chat_connected": "🔗 Шәкәрім Университеті әкімші қосылды. Сөйлесуді бастай аласыз. 💬",
        "chat_disconnected": "🔌 Шәкәрім Университеті әкімші ажыратылды. Сөйлесу аяқталды. 👋",
        "chat_waiting": "⏳ Шәкәрім Университеті әкімшінің қосылуын күту... 💬",
        "chat_stopped": "🛑 Шәкәрім Университетімен сөйлесу тоқтатылды.",
        "waiting_for_connection": "⏳ Күте тұрыңыз! Шәкәрім Университеті қызметкерімен байланысуға тырысудамыз. Болдырмау үшін /stop жазыңыз. 🔄",
        "connection_terminated_by_user": "🛑 Шәкәрім Университетімен байланыс сізбен үзілді! Ботты пайдалануды жалғастыру үшін /start жазыңыз. 🔄",
        "admin_connected": "👨‍💼 Шәкәрім Университеті әкімшісі: {}\n\n🔗 Сізбен байланыс орнатылды! Сөйлесу үшін чатқа жаза аласыз. Аяқтау үшін /stop жазыңыз. 💬",
        "connecting": "🔄 Шәкәрім Университетімен белсенді байланыс орнатылуда...",
        "connection_terminated_by_admin": "🔌 Шәкәрім Университеті қызметкерімен байланыс жауап берушімен үзілді! Ботты пайдалануды жалғастыру үшін /start жазыңыз. 🔄",
        "connection_terminated_forcibly": "⚠️ Шәкәрім Университетімен байланыс күштеп үзілді!\n\n📱 Жалғастыру үшін /start жазыңыз. 🔄",
    },
    
    "en": {
        # Общие сообщения
        "banned_user": "❌ You are banned and cannot use the Shakarim University bot. Please contact support to resolve this issue. ❌",
        "exit_chat_first": "⚠️ Type /stop to exit the Shakarim University chat mode. ⚠️",
        "welcome": "👋 Welcome to Shakarim University Support Bot! 🎓\n\n📱 Technical support: @MDS124578\n⏰ Working hours: 9:00-18:00\n🍽️ Lunch break: 13:00-14:00\n\n📋 Select an option from the menu:",
        "select_option": "📋 Select an option from the Shakarim University menu:",
        
        # Сообщения выбора языка
        "select_language": "🌐 Пожалуйста, выберите язык / Тілді таңдаңыз / Please select a language:",
        "language_selected": "✅ English language selected. Shakarim University welcomes you! 🎓",
        
        # Сообщения регистрации
        "already_registered": "📝 You are already registered in the Shakarim University system.",
        "enter_name": "👤 Please enter your full name to register with Shakarim University:",
        "enter_email": "📧 Please enter your email to communicate with Shakarim University:",
        "registration_successful": "🎉 Registration with Shakarim University completed successfully! 🎉",
        "registration_cancelled": "🚫 Registration with Shakarim University cancelled.",
        
        # FAQ
        "faq_title": "❓ Shakarim University Frequently Asked Questions:",
        "back_to_list": "⬅️ Back to list",
        "faq_question_prompt": "🔢 Enter the number of the question about Shakarim University that suits you:",
        "question_not_found": "❓ Question with this number not found. Please choose a number from the Shakarim University questions list.",
        
        # Вопросы
        "ask_question": "❓ Please write your question about Shakarim University:",
        "question_sent": "📤 Your question has been sent to Shakarim University administrators. We will answer you as soon as possible. ⏳",
        "question_cancelled": "🚫 Question sending to Shakarim University cancelled.",
        "question_accepted": "✅ Your question #{} is accepted! Wait for a response from the Shakarim University Registration Office staff. ⏳",
        "question_answer_received": "📬 Answer to your question #{}:\n\n❓ Question:\n{}\n\n✅ Answer from {} (Shakarim University):\n{}\n\n📱 To open the menu, type /start",
        
        # Чат
        "chat_intro": "💬 You have requested a chat with a Shakarim University administrator. Please wait for connection... ⏳",
        "chat_connected": "🔗 Shakarim University administrator connected. You can start chatting. 💬",
        "chat_disconnected": "🔌 Shakarim University administrator disconnected. Chat ended. 👋",
        "chat_waiting": "⏳ Waiting for Shakarim University administrator connection... 💬",
        "chat_stopped": "🛑 Chat with Shakarim University stopped.",
        "waiting_for_connection": "⏳ Please wait! We are trying to connect you with a Shakarim University staff member. Type /stop to cancel. 🔄",
        "connection_terminated_by_user": "🛑 Connection with Shakarim University terminated by you! Type /start to continue using the bot. 🔄",
        "admin_connected": "👨‍💼 Shakarim University Administrator: {}\n\n🔗 Connection established! You can now chat. Type /stop to end the conversation. 💬",
        "connecting": "🔄 Establishing active connection with Shakarim University...",
        "connection_terminated_by_admin": "🔌 Connection with Shakarim University staff terminated by the responder! Type /start to continue using the bot. 🔄",
        "connection_terminated_forcibly": "⚠️ Connection with Shakarim University was forcibly terminated!\n\n📱 Type /start to continue. 🔄",
    }
}


def get_message(message_key: str, language: str) -> str:
    """
    Получение сообщения на нужном языке.
    
    :param message_key: Ключ сообщения
    :param language: Код языка (ru, kz, en)
    :return: Сообщение на выбранном языке
    """
    # Если язык не поддерживается или ключ не найден, используем русский язык по умолчанию
    if language not in MESSAGES or message_key not in MESSAGES[language]:
        return MESSAGES["ru"].get(message_key, f"Message key '{message_key}' not found")
    
    return MESSAGES[language][message_key] 