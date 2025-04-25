from aiogram.types import Message


async def save_media_file(message: Message, question_id: str) -> dict:
    """Сохраняет медиафайл и возвращает информацию о нем."""
    media_info = {
        "type": message.content_type,
        "file_id": None,
        "caption": None
    }

    if message.content_type == "text":
        return None

    if message.content_type in ["photo", "video", "audio", "voice", "video_note", "document"]:
        if message.content_type == "photo":
            # Для фото берем самое большое разрешение
            media_info["file_id"] = message.photo[-1].file_id
        elif message.content_type == "video":
            media_info["file_id"] = message.video.file_id
        elif message.content_type == "audio":
            media_info["file_id"] = message.audio.file_id
        elif message.content_type == "voice":
            media_info["file_id"] = message.voice.file_id
        elif message.content_type == "video_note":
            media_info["file_id"] = message.video_note.file_id
        elif message.content_type == "document":
            media_info["file_id"] = message.document.file_id

        if message.caption:
            media_info["caption"] = message.caption

    return media_info 