import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Настройки
TOKEN = os.getenv('TELEGRAM_TOKEN')  # Получаем токен из переменных окружения
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))  # ID админа (опционально)

# Проверка токена
if not TOKEN:
    raise ValueError("❌ Токен бота не найден! Проверьте настройки Render")

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name
    
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        "Я работающий бот без системы баллов\n"
        "Доступные команды:\n"
        "/help - Показать это сообщение\n"
        "/info - Информация о боте"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "ℹ️ Справка по боту:\n\n"
        "/start - Начать работу\n"
        "/info - Информация\n"
        "/help - Эта справка"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /info"""
    await update.message.reply_text(
        "🤖 Бот создан @tolik_scripter\n"
        "Версия: 1.0 (без системы баллов)\n"
        "Работает на Render.com"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик обычных сообщений"""
    text = update.message.text
    if "привет" in text.lower():
        await update.message.reply_text("И тебе привет! 😊")

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("info", info))
    
    # Обработчик обычных сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
