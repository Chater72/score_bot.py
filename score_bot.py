import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json

# Настройки для Render
TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))

if not TOKEN:
    raise ValueError("❌ Токен бота не найден! Проверьте Environment Variables в Render")

# Константы
SCORES_FILE = "scores.json"
TRIGGER_PHRASE = "Выебать овнера говнопроекта"
MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки баллов: {e}")
        return {}

def save_scores(scores):
    try:
        with open(SCORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else user.first_name
    
    scores = load_scores()
    if user_id not in scores:
        scores[user_id] = {"username": username, "score": 0}
        save_scores(scores)
    
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        f"Пиши «{TRIGGER_PHRASE}» для баллов.\n"
        "🔝 Топ: /top\n"
        "➕ Добавить баллы: /add @юзернейм количество"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("📭 Топ пуст")
        return
    
    top_users = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )[:10]
    
    response = "🏆 Топ игроков:\n\n"
    for i, (user_id, data) in enumerate(top_users):
        response += f"{MEDALS[i]} {data['username']}: {data['score']} баллов\n"
    
    await update.message.reply_text(response)

async def add_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Только для админа!")
        return
    
    try:
        target = context.args[0]
        amount = int(context.args[1])
    except:
        await update.message.reply_text(
            "ℹ️ Формат: /add [@юзернейм или ID] [количество]\n"
            "Пример: /add @tolik_scripter 10"
        )
        return
    
    scores = load_scores()
    updated = False
    
    # Поиск по юзернейму
    if target.startswith('@'):
        for user_id, data in scores.items():
            if data.get('username') == target:
                scores[user_id]['score'] += amount
                updated = True
                break
    # Поиск по ID
    elif target in scores:
        scores[target]['score'] += amount
        updated = True
    
    if not updated:
        await update.message.reply_text(f"⚠️ Пользователь {target} не найден")
        return
    
    save_scores(scores)
    await update.message.reply_text(f"✅ Начислено {amount} баллов для {target}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    logger.info("✅ Бот запущен и готов к работе")
    app.run_polling()

if __name__ == "__main__":
    main()
