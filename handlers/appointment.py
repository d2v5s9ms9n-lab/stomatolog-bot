from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards.inline import services_keyboard, doctors_keyboard, dates_keyboard, time_keyboard, confirm_keyboard
from database import get_or_create_user, create_appointment

# Состояния ConversationHandler
SERVICE, DOCTOR, DATE, TIME, CONFIRM = range(5)

# Описание услуг
SERVICE_DESCRIPTIONS = {
    "consultation": "Консультация",
    "caries": "Лечение кариеса",
    "extraction": "Удаление зуба",
    "cleaning": "Чистка зубов",
    "prosthesis": "Протезирование",
    "implantation": "Имплантация",
    "gums": "Лечение дёсен",
    "children": "Детская стоматология"
}

async def book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦷 **Выберите услугу**\n\n"
        "Я помогу записаться на приём к стоматологу.\n\n"
        "Сначала выберите нужную услугу:",
        reply_markup=services_keyboard(),
        parse_mode="Markdown"
    )
    return SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    service = query.data.replace("service_", "")
    service_name = SERVICE_DESCRIPTIONS.get(service, service)
    context.user_data['service'] = service
    context.user_data['service_name'] = service_name
    
    await query.edit_message_text(
        f"✅ Выбрана услуга: *{service_name}*\n\n"
        "Теперь выберите врача:",
        reply_markup=doctors_keyboard(),
        parse_mode="Markdown"
    )
    return DOCTOR

async def select_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    doctor = query.data.replace("doctor_", "")
    context.user_data['doctor'] = doctor
    
    await query.edit_message_text(
        f"✅ Выбран врач: *{doctor}*\n\n"
        "Теперь выберите дату:",
        reply_markup=dates_keyboard(),
        parse_mode="Markdown"
    )
    return DATE

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    date = query.data.replace("date_", "")
    context.user_data['date'] = date
    
    await query.edit_message_text(
        f"✅ Выбрана дата: *{date}*\n\n"
        "Теперь выберите время:",
        reply_markup=time_keyboard(),
        parse_mode="Markdown"
    )
    return TIME

async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    time = query.data.replace("time_", "")
    context.user_data['time'] = time
    
    appointment_data = {
        'doctor': context.user_data['doctor'],
        'service': context.user_data['service'],
        'service_name': context.user_data['service_name'],
        'date': context.user_data['date'],
        'time': context.user_data['time']
    }
    
    await query.edit_message_text(
        f"📋 *Подтверждение записи*\n\n"
        f"👨‍⚕️ Врач: *{appointment_data['doctor']}*\n"
        f"🦷 Услуга: *{appointment_data['service_name']}*\n"
        f"📅 Дата: *{appointment_data['date']}*\n"
        f"⏰ Время: *{appointment_data['time']}*\n\n"
        "Подтвердите запись:",
        reply_markup=confirm_keyboard(appointment_data),
        parse_mode="Markdown"
    )
    return CONFIRM

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_booking":
        await query.edit_message_text("❌ Запись отменена.")
        return ConversationHandler.END
    
    user = query.from_user
    user_id = get_or_create_user(user.id, user.full_name)
    
    appointment_data = context.user_data
    create_appointment(
        user_id=user_id,
        doctor_name=appointment_data['doctor'],
        service_type=appointment_data['service_name'],
        appointment_date=appointment_data['date'],
        appointment_time=appointment_data['time']
    )
    
    await query.edit_message_text(
        f"✅ *Запись подтверждена!*\n\n"
        f"👨‍⚕️ Врач: *{appointment_data['doctor']}*\n"
        f"🦷 Услуга: *{appointment_data['service_name']}*\n"
        f"📅 Дата: *{appointment_data['date']}*\n"
        f"⏰ Время: *{appointment_data['time']}*\n\n"
        "Ждём вас на приём! 🦷",
        parse_mode="Markdown"
    )
    
    context.user_data.clear()
    return ConversationHandler.END