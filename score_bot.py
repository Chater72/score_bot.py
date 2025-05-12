import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json

# Настройки
TOKEN = os.getenv('TELEGRAM_TOKEN')
SCORES_FILE = "scores.json"
TRIGGER_PHRASE = "выебать овнера говнопроекта"  # в нижнем регистре для сравнения

# Проверка токена
if not TOKEN:
    raise ValueError("❌ Токен не найден!")

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
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки баллов: {e}")
        return {}

def save_scores(scores):
    """Сохраняет баллы в файл"""
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=4, ensure_ascii=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = str(user.id)
    username = user.username if user.username else user.first_name  # Без @
    
    scores = load_scores()
    if user_id not in scores:
        scores[user_id] = {"username": username, "score": 0}
        save_scores(scores)
    
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        f"Пиши «{TRIGGER_PHRASE}» для баллов.\n"
        "🔝 Топ: /top"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /top"""
    scores = load_scores()
    
    if not scores:
        await update.message.reply_text("📭 Топ пуст")
        return
    
    # Сортировка по баллам
    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:10]  # Топ-10
    
    # Формирование сообщения
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    msg = "🏆 Топ игроков:\n\n"
    
    for i, (user_id, data) in enumerate(sorted_scores):
        msg += f"{medals[i]} {data['username']}: {data['score']} баллов\n"
    
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик обычных сообщений"""
    text = update.message.text.lower()  # Приводим к нижнему регистру
    
    if TRIGGER_PHRASE in text:  # Проверяем без учета регистра
        user = update.effective_user
        user_id = str(user.id)
        username = user.username if user.username else user.first_name  # Без @
        
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
