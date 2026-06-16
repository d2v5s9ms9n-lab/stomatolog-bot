from telegram import Update
from telegram.ext import ContextTypes
from keyboards.inline import main_menu_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я помогу тебе записаться на приём к стоматологу.\n\n"
        "Используй команду /book для записи или выбери действие ниже:",
        reply_markup=main_menu_keyboard()
    )