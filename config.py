import os
import json
from dotenv import load_dotenv
from ast import literal_eval

# Load environment variables from .env file
load_dotenv()

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str]
BANNED_IDS = []  # ID забаненных пользователей

# ID топиков для уведомлений
QUESTION_NOTIFICATION_TOPIC_ID = int(os.getenv("QUESTION_NOTIFICATION_TOPIC_ID", 162))
QUESTION_ANSWER_TOPIC_ID = int(os.getenv("QUESTION_ANSWER_TOPIC_ID", 166))
CHAT_NOTIFICATION_TOPIC_ID = int(os.getenv("CHAT_NOTIFICATION_TOPIC_ID", 162))

# ID и информация о топиках администраторов
ADMIN_TOPICS = {
    "Дамир": {"id": 208, "user_id": 609461858, "status": "open"},
    "Дамир2": {"id": 214, "user_id": 6121047119, "status": "open"},
    "Қасымова Елназ": {"id": 1135, "user_id": 872455313, "status": "open"},
    "Қабаева Қарлығаш": {"id": 1137, "user_id": 1515802071, "status": "open"},
    "Оспанова Айнаш": {"id": 1139, "user_id": 354690987, "status": "open"},
    "Сагатбекова Ажар": {"id": 1141, "user_id": 1007868370, "status": "open"},
    "Кенжебаева Жансая": {"id": 1143, "user_id": 1588957616, "status": "open"},
    "Тулеубекова Асель": {"id": 1155, "user_id": 822719166, "status": "open"}
} 