import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import json

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Проверка токена
if not TOKEN:
    raise ValueError("❌ Токен бота не найден! Проверьте Environment Variables")

# Настройки
SCORES_FILE = "scores.json"
TRIGGER_PHRASE = "Выебать овнера говнопроекта"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_scores():
    """Загрузка баллов из файла"""
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scores(scores):
    """Сохранение баллов в файл"""
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name
    
    # Регистрируем пользователя
    scores = load_scores()
    user_id = str(user.id)
    if user_id not in scores:
        scores[user_id] = {"score": 0, "username": username}
        save_scores(scores)
    
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        f"Пиши «{TRIGGER_PHRASE}» для баллов.\n"
        "🔝 Топ: /top\n"
        "➕ Добавить баллы (админ): /add @username или ID количество"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /top"""
    scores = load_scores()
    
    if not scores:
        await update.message.reply_text("📭 Топ пуст. Будь первым!")
        return
    
    # Сортировка по баллам
    sorted_users = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:10]  # Топ-10
    
    # Формируем сообщение
    message = "🏆 Топ игроков:\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, (user_id, data) in enumerate(sorted_users):
        username = data.get("username", f"ID {user_id}")
        message += f"{medals[i]} {username}: {data['score']} баллов\n"
    
    await update.message.reply_text(message)

async def add_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add"""
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("🚫 Только для админа!")
        return
    
    try:
        target = context.args[0]
        amount = int(context.args[1])
    except:
        await update.message.reply_text(
            "⚠️ Используйте: /add @username или ID количество\n"
            "Пример: /add @tolik_scripter 10"
        )
        return
    
    scores = load_scores()
    
    # Поиск пользователя
    user_id = None
    for uid, data in scores.items():
        if target == uid or data.get("username") == target:
            user_id = uid
            break
    
    if not user_id:
        await update.message.reply_text("❌ Пользователь не найден")
        return
    
    # Добавление баллов
    scores[user_id]["score"] += amount
    save_scores(scores)
    
    await update.message.reply_text(
        f"✅ Добавлено {amount} баллов пользователю {scores[user_id].get('username', user_id)}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик триггерной фразы"""
    if TRIGGER_PHRASE.lower() in update.message.text.lower():
        user = update.effective_user
        user_id = str(user.id)
        username = f"@{user.username}" if user.username else user.first_name
        
        scores = load_scores()
        if user_id not in scores:
            scores[user_id] = {"score": 0, "username": username}
        
        scores[user_id]["score"] += 1
        save_scores(scores)
        
        await update.message.reply_text(
            f"🎉 +1 балл! Твой счет: {scores[user_id]['score']}\n"
            "Посмотреть топ: /top"
        )

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("add", add_score))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
