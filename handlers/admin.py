from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_connection
from config import ADMIN_IDS

# Состояния для админ-панели
ADMIN_MENU, VIEW_APPOINTMENTS, FILTER_APPOINTMENTS = range(3)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("📋 Просмотр записей", callback_data='admin_view')],
        [InlineKeyboardButton("🔍 Фильтрация", callback_data='admin_filter')],
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("❌ Закрыть", callback_data='admin_close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ Админ-панель\n\nВыберите действие:",
        reply_markup=reply_markup
    )
    return ADMIN_MENU

async def admin_view_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.id, u.full_name, a.doctor_name, a.service_type, 
               a.appointment_date, a.appointment_time, a.status
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        LIMIT 10
    """)
    
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not appointments:
        await query.edit_message_text("📭 Записей пока нет.")
        return ADMIN_MENU
    
    message = "📋 Последние 10 записей:\n\n"
    for app in appointments:
        message += f"ID: {app[0]}\n"
        message += f"👤 Пациент: {app[1]}\n"
        message += f"👨‍⚕️ Врач: {app[2]}\n"
        message += f"🦷 Услуга: {app[3]}\n"
        message += f"📅 Дата: {app[4]}\n"
        message += f"⏰ Время: {app[5]}\n"
        message += f"📊 Статус: {app[6]}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)
    return ADMIN_MENU

async def admin_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 По дате", callback_data='filter_date')],
        [InlineKeyboardButton("👨‍⚕️ По врачу", callback_data='filter_doctor')],
        [InlineKeyboardButton("📊 По статусу", callback_data='filter_status')],
        [InlineKeyboardButton("⬅️ Назад", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔍 Фильтрация записей:\n\nВыберите критерий:",
        reply_markup=reply_markup
    )
    return FILTER_APPOINTMENTS

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'")
    confirmed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    message = f"📊 Статистика:\n\n"
    message += f"👥 Всего пользователей: {users}\n"
    message += f"📅 Всего записей: {total}\n"
    message += f"⏳ Ожидают подтверждения: {pending}\n"
    message += f"✅ Подтверждено: {confirmed}\n"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)
    return ADMIN_MENU

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📋 Просмотр записей", callback_data='admin_view')],
        [InlineKeyboardButton("🔍 Фильтрация", callback_data='admin_filter')],
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("❌ Закрыть", callback_data='admin_close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ Админ-панель\n\nВыберите действие:",
        reply_markup=reply_markup
    )
    return ADMIN_MENU

async def admin_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Админ-панель закрыта.")
    return ConversationHandler.END