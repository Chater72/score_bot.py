import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# Конфигурация

ADMIN_ID = 8185820733
SCORES_FILE = "scores.json"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_scores():
    """Загружает баллы из файла."""
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}}

def save_scores(data):
    """Сохраняет баллы в файл."""
    with open(SCORES_FILE, 'w') as f:
        json.dump(data, f, indent=4)

async def update_user_data(user_id: str, username: str = None, score_change: int = 0) -> int:
    """Обновляет данные пользователя."""
    data = load_scores()
    normalized_username = username.lower() if username else None
    
    # Обновляем запись по ID
    if user_id not in data["users"]:
        data["users"][user_id] = {"score": 0}
    if normalized_username:
        data["users"][user_id]["username"] = normalized_username
    
    # Обновляем запись по юзернейму
    if normalized_username:
        if normalized_username not in data["users"]:
            data["users"][normalized_username] = {"id": user_id, "score": 0}
        data["users"][normalized_username]["score"] = data["users"][user_id]["score"] + score_change
    
    # Изменяем баллы
    data["users"][user_id]["score"] += score_change
    save_scores(data)
    return data["users"][user_id]["score"]

async def top_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /top."""
    data = load_scores()
    if not data["users"]:
        await update.message.reply_text("📭 Топ пуст.")
        return

    # Собираем уникальных пользователей
    unique_users = {}
    for key, user_data in data["users"].items():
        if isinstance(user_data, dict) and "score" in user_data:
            user_id = user_data.get("id", key)
            if user_id not in unique_users:
                unique_users[user_id] = user_data

    # Сортируем по баллам
    sorted_users = sorted(unique_users.values(), key=lambda x: x["score"], reverse=True)
    
    # Формируем сообщение
    medals = ["🥇", "🥈", "🥉", "🔹", "🔹", "🔹", "🔹", "🔹", "🔹", "🔹"]
    msg = "🏆 <b>Топ 10:</b>\n\n"
    
    for i, user in enumerate(sorted_users[:10]):
        display_name = f"@{user['username']}" if user.get("username") else f"ID {user.get('id', '?')}"
        msg += f"{medals[i]} {display_name}: <b>{user['score']}</b> баллов\n"
    
    await update.message.reply_text(msg, parse_mode="HTML")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений."""
    if not update.message:
        return

    user = update.message.from_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else None

    if "Выебать овнера говнопроекта" in update.message.text:
        new_score = await update_user_data(user_id, username, score_change=1)
        await update.message.reply_text(f"🎉 +1 балл! Твой счёт: <b>{new_score}</b>", parse_mode="HTML")

async def add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add."""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Ты не админ!")
        return

    try:
        target = context.args[0]
        amount = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Используй: /add @username или ID количество_баллов")
        return

    data = load_scores()
    target_data = data["users"].get(target, {})

    # Определяем ID и юзернейм
    user_id = target_data.get("id", target) if target.startswith("@") else target
    username = target if target.startswith("@") else target_data.get("username")

    new_score = await update_user_data(user_id, username, score_change=amount)
    display_name = username or f"ID {user_id}"
    await update.message.reply_text(
        f"✅ +{amount} баллов для <b>{display_name}</b>. Новый счёт: <b>{new_score}</b>",
        parse_mode="HTML"
    )

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.message.from_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else None
    await update_user_data(user_id, username)

    await update.message.reply_text(
        f"👋 Привет, {username or 'друг'}!\n\n"
        "Пиши «Выебать овнера говнопроекта» для баллов.\n"
        "🔝 Топ: /top\n"
        "➕ Добавить баллы (админ): /add @username или ID количество",
        parse_mode="HTML"
    )

def main():
    """Запуск бота."""
    app = Application.builder().token(TELEGRAM_API_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("top", top_handler))
    app.add_handler(CommandHandler("add", add_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
