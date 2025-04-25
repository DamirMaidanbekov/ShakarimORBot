# Telegram Bot for OR

A Telegram bot for handling user questions and chat requests. The bot supports multiple administrators and routing messages to specific admin topics.

## Features

- User registration
- FAQs management
- Question handling with admin notifications
- Live chat with administrators
- Multi-language support
- Environment variable configuration

## Project Structure

- `main.py` - Bot entry point
- `config.py` - Configuration settings loaded from .env file
- `handlers/` - Telegram command and message handlers
- `utils/` - Utility functions
- `states/` - Bot states for conversation handling
- `faq/` - FAQ data storage
- `data/` - Data storage
- `logs/` - Log files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/OR_bot.git
cd OR_bot
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate 
# On Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with:
```
BOT_TOKEN=your_telegram_bot_token
ADMIN_GROUP_ID=your_admin_group_id
ADMIN_IDS=id1,id2,id3
QUESTION_NOTIFICATION_TOPIC_ID=topic_id
QUESTION_ANSWER_TOPIC_ID=topic_id
CHAT_NOTIFICATION_TOPIC_ID=topic_id
```

4. Run the bot:
```bash
python main.py
```

## Configuration

Configure the bot by editing the `.env` file:

- `BOT_TOKEN`: Telegram Bot API token from BotFather
- `ADMIN_GROUP_ID`: ID of the admin group
- `ADMIN_IDS`: Comma-separated list of admin user IDs
- `QUESTION_NOTIFICATION_TOPIC_ID`: Topic ID for question notifications
- `QUESTION_ANSWER_TOPIC_ID`: Topic ID for question answers
- `CHAT_NOTIFICATION_TOPIC_ID`: Topic ID for chat notifications

## Usage

- `/start` - Start the bot and registration
- `/help` - Show help message
- `/faq` - Access FAQ section
- `/question` - Ask a question to admins
- `/chat` - Start a live chat with admins

## License

[MIT License](LICENSE) 