import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json

# Настройки
TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
SCORES_FILE = "scores.json"
TRIGGER_PHRASE = "Выебать овнера говнопроекта"

# Логирование
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
    try:
        with open(SCORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

async def handle_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает триггерную фразу"""
    if TRIGGER_PHRASE.lower() in update.message.text.lower():
        user = update.effective_user
        user_id = str(user.id)
        username = f"@{user.username}" if user.username else user.first_name
        
        scores = load_scores()
        
        # Добавляем нового пользователя если нужно
        if user_id not in scores:
            scores[user_id] = {"username": username, "score": 0}
            logger.info(f"Зарегистрирован новый пользователь: {username} (ID: {user_id})")
        
        # Добавляем балл
        scores[user_id]["score"] += 1
        save_scores(scores)
        
        logger.info(f"Начислен балл для {username}. Текущий счёт: {scores[user_id]['score']}")
        
        await update.message.reply_text(
            f"🎉 +1 балл! Твой счёт: {scores[user_id]['score']}\n"
            "Посмотреть топ: /top"
        )

async def add_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручное добавление баллов (админ)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Только для админа!")
        return
    
    try:
        target = context.args[0]  # @username или ID
        amount = int(context.args[1])
    except:
        await update.message.reply_text("ℹ️ Формат: /add [@юзернейм или ID] [количество]")
        return
    
    scores = load_scores()
    target_found = False
    
    # Поиск пользователя
    for user_id, data in scores.items():
        if target == data.get("username") or target == user_id:
            data["score"] += amount
            target_found = True
            logger.info(f"Админ добавил {amount} баллов для {target}")
            break
    
    if not target_found:
        await update.message.reply_text(f"⚠️ Пользователь {target} не найден")
        logger.warning(f"Пользователь {target} не найден для команды /add")
        return
    
    save_scores(scores)
    await update.message.reply_text(f"✅ Добавлено {amount} баллов для {target}")

async def show_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает топ игроков"""
    scores = load_scores()
    
    if not scores:
        await update.message.reply_text("📭 Топ пуст")
        return
    
    # Сортируем по баллам
    top_users = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )[:10]  # Только топ-10
    
    # Формируем сообщение
    message = "🏆 Топ игроков:\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, (user_id, data) in enumerate(top_users):
        message += f"{medals[i]} {data['username']}: {data['score']} баллов\n"
    
    await update.message.reply_text(message)

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_trigger))
    app.add_handler(CommandHandler("top", show_top))
    app.add_handler(CommandHandler("add", add_score))
    
    logger.info("Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
