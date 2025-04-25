import json
import os
from typing import Dict, Any


def get_user_data_path(user_id: int) -> str:
    """Получение пути к файлу пользовательских данных."""
    return f"data/{user_id}.json"


def is_user_registered(user_id: int) -> bool:
    """Проверка на зарегистрирован ли уже пользователь."""
    return os.path.exists(get_user_data_path(user_id))


def load_user_data(user_id: int) -> Dict[str, Any]:
    """Загрузка пользовательских данных из файла JSON."""
    file_path = get_user_data_path(user_id)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


def save_user_data(user_id: int, data: Dict[str, Any]) -> None:
    """Сохранение пользовательских данных в файл JSON."""
    os.makedirs("data", exist_ok=True)
    with open(get_user_data_path(user_id), 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_user_language(user_id: int) -> str:
    """Получение языка пользователя. По умолчанию - русский."""
    user_data = load_user_data(user_id)
    return user_data.get("language", "ru")


def set_user_language(user_id: int, language: str) -> None:
    """Сохранение выбранного языка пользователя."""
    user_data = load_user_data(user_id)
    user_data["language"] = language
    save_user_data(user_id, user_data)


def load_faq(language: str = "ru") -> Dict[str, Any]:
    """Загрузка часто задаваемых вопросов из файла JSON с учетом языка."""
    faq_path = f"faq/faq_{language}.json"
    
    # Проверяем, существует ли файл для указанного языка
    if os.path.exists(faq_path):
        try:
            with open(faq_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # Если файл поврежден или имеет неверный формат, логируем ошибку
            print(f"Ошибка при чтении FAQ файла {faq_path}")
    
    # Только если файла нет или была ошибка чтения, используем русский как запасной вариант
    if language != "ru":
        ru_faq_path = "faq/faq_ru.json"
        if os.path.exists(ru_faq_path):
            try:
                with open(ru_faq_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Ошибка при чтении FAQ файла {ru_faq_path}")
    
    # Если ни одного файла нет или все поврежденны, возвращаем пустой словарь
    return {}


def is_user_banned(user_id: int) -> bool:
    """Проверка, забанен ли пользователь."""
    try:
        if os.path.exists("banned.json"):
            with open("banned.json", 'r', encoding='utf-8') as file:
                banned_ids = json.load(file)
                return user_id in banned_ids
        return False
    except Exception as e:
        print(f"Ошибка при проверке бана пользователя: {e}")
        return False


def ban_user(user_id: int) -> bool:
    """Забанить пользователя, добавив его ID в banned.json."""
    try:
        banned_ids = []
        if os.path.exists("banned.json"):
            with open("banned.json", 'r', encoding='utf-8') as file:
                banned_ids = json.load(file)
        
        if user_id not in banned_ids:
            banned_ids.append(user_id)
            with open("banned.json", 'w', encoding='utf-8') as file:
                json.dump(banned_ids, file, ensure_ascii=False, indent=4)
            return True
        return False  # Пользователь уже забанен
    except Exception as e:
        print(f"Ошибка при бане пользователя: {e}")
        return False


def unban_user(user_id: int) -> bool:
    """Разбанить пользователя, удалив его ID из banned.json."""
    try:
        if not os.path.exists("banned.json"):
            return False  # Файл бана не существует
        
        with open("banned.json", 'r', encoding='utf-8') as file:
            banned_ids = json.load(file)
        
        if user_id in banned_ids:
            banned_ids.remove(user_id)
            with open("banned.json", 'w', encoding='utf-8') as file:
                json.dump(banned_ids, file, ensure_ascii=False, indent=4)
            return True
        return False  # Пользователь не был забанен
    except Exception as e:
        print(f"Ошибка при разбане пользователя: {e}")
        return False


async def setup_sample_faq():
    """Создание файлов faq_*.json, если их нет"""
    os.makedirs("faq", exist_ok=True)
    
    # Образцы для каждого языка
    sample_faqs = {
        "ru": {
            "1": {
                "question": "ВОПРОС1",
                "answer": "ОТВЕТ1"
            },
            "2": {
                "question": "ВОПРОС2",
                "answer": "ОТВЕТ2"
            },
            "3": {
                "question": "ВОПРОС3",
                "answer": "ОТВЕТ3"
            }
        },
        "kz": {
            "1": {
                "question": "СҰРАҚ1",
                "answer": "ЖАУАП1"
            },
            "2": {
                "question": "СҰРАҚ2",
                "answer": "ЖАУАП2"
            },
            "3": {
                "question": "СҰРАҚ3",
                "answer": "ЖАУАП3"
            }
        },
        "en": {
            "1": {
                "question": "QUESTION1",
                "answer": "ANSWER1"
            },
            "2": {
                "question": "QUESTION2",
                "answer": "ANSWER2"
            },
            "3": {
                "question": "QUESTION3",
                "answer": "ANSWER3"
            }
        }
    }
    
    # Создаем файлы для каждого языка, если они не существуют
    for lang, faq_data in sample_faqs.items():
        faq_path = f"faq/faq_{lang}.json"
        if not os.path.exists(faq_path):
            with open(faq_path, 'w', encoding='utf-8') as file:
                json.dump(faq_data, file, ensure_ascii=False, indent=4) 