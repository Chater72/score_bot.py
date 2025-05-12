import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json
from dotenv import load_dotenv

# 1. НАСТРОЙКА ОКРУЖЕНИЯ ======================================
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')  # Проверьте название переменной!
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Ваш ID в Telegram

if not TOKEN:
    raise ValueError("Токен бота не найден! Проверьте .env или настройки Render")

# 2. СИСТЕМА БАЛЛОВ ==========================================
SCORES_FILE = "scores.json"

def load_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки баллов: {e}")
        return {}

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=4)

# 3. КОМАНДА /add (ПЕРЕРАБОТАННАЯ) ==========================
async def add_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет баллы пользователю"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Только для админа!")
        return

    try:
        target = context.args[0]  # Может быть @username или ID
        amount = int(context.args[1])
    except:
        await update.message.reply_text("ℹ️ Формат: /add [@юзернейм или ID] [количество]")
        return

    scores = load_scores()
    updated = False

    # Поиск по юзернейму (формат @username)
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

# 4. ОСТАЛЬНЫЕ КОМАНДЫ =======================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else user.first_name

    scores = load_scores()
    if user_id not in scores:
        scores[user_id] = {'username': username, 'score': 0}
        save_scores(scores)

    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        f"Пиши «Выебать овнера говнопроекта» для баллов\n"
        "🔝 Топ: /top\n"
        "➕ Добавить баллы: /add @юзернейм количество"
    )

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("📭 Топ пуст")
        return

    top_users = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)[:10]
    response = "🏆 Топ игроков:\n\n" + "\n".join(
        f"{i+1}. {data['username']}: {data['score']} баллов"
        for i, (_, data) in enumerate(top_users)
    )
    await update.message.reply_text(response)

# 5. ЗАПУСК БОТА =============================================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("add", add_score))
    
    logger = logging.getLogger(__name__)
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
