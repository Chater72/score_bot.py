import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Проверка токена
if not TOKEN:
    raise ValueError("❌ Токен бота не найден! Проверьте Environment Variables в Render.com")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}!\n\n"
        "Я бот, созданный @tolik_scripter\n"
        "Отправь мне фразу для получения баллов"
    )

async def add_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление баллов (только для админа)"""
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещен!")
        return
    
    try:
        amount = int(context.args[0])
        # Логика добавления баллов
        await update.message.reply_text(f"✅ Добавлено {amount} баллов")
    except:
        await update.message.reply_text("Используйте: /add [количество]")

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_score))
    
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
