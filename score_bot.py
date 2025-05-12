import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import json

# Инициализация
load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Константы
SCORES_FILE = "scores.json"
TRIGGER_PHRASE = "Выебать овнера говнопроекта"

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_scores():
    """Загружает баллы из файла"""
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки баллов: {e}")
    return {}

def save_scores(scores):
    """Сохраняет баллы в файл"""
    try:
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения баллов: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name
    
    scores = load_scores()
    user_id = str(user.id)
    if user_id not in scores:
        scores[user_id] = {"username": username, "score": 0}
        save_scores(scores)
    
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        f"Пиши «{TRIGGER_PHRASE}» для баллов.\n"
        "🔝 Топ: /top\n"
        "➕ Добавить баллы (админ): /add @username количество"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит топ игроков"""
    scores = load_scores()
    
    if not scores:
        await update.message.reply_text("📭 Топ пуст. Будь первым!")
        return
    
    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:10]
    
    msg = "🏆 Топ игроков:\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, (user_id, data) in enumerate(sorted_scores):
        username = data.get("username", f"ID {user_id}")
        msg += f"{medals[i]} {username}: {data['score']} баллов\n"
    
    await update.message.reply_text(msg)

async def add_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет баллы (только для админа)"""
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("🚫 Только для админа!")
        return
    
    try:
        target = context.args[0]
        amount = int(context.args[1])
    except:
        await update.message.reply_text(
            "ℹ️ Используйте: /add @username количество\n"
            "Пример: /add @tolik_scripter 10"
        )
        return
    
    scores = load_scores()
    target_found = False
    
    # Поиск по юзернейму или ID
    for user_id, data in scores.items():
        if target == data.get("username") or target == user_id:
            data["score"] += amount
            target_found = True
            break
    
    if not target_found:
        await update.message.reply_text("❌ Пользователь не найден. Сначала он должен написать боту.")
        return
    
    save_scores(scores)
    await update.message.reply_text(
        f"✅ Добавлено {amount} баллов пользователю {target}\n"
        f"Новый счет: {scores[user_id]['score']}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает триггерную фразу"""
    if TRIGGER_PHRASE.lower() in update.message.text.lower():
        user = update.effective_user
        user_id = str(user.id)
        username = f"@{user.username}" if user.username else user.first_name
        
        scores = load_scores()
        if user_id not in scores:
            scores[user_id] = {"username": username, "score": 0}
        
        scores[user_id]["score"] += 1
        save_scores(scores)
        
        await update.message.reply_text(
            f"🎉 +1 балл! Твой счет: {scores[user_id]['score']}\n"
            "Посмотреть топ: /top"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("add", add_score))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
