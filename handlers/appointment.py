from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards.inline import services_keyboard, doctors_keyboard, dates_keyboard, time_keyboard, confirm_keyboard
from database import get_or_create_user, create_appointment

# Состояния ConversationHandler
SERVICE, DOCTOR, DATE, TIME, CONFIRM = range(5)

async def book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выберите услугу:",
        reply_markup=services_keyboard()
    )
    return SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service = query.data.replace("service_", "")
    context.user_data['service'] = service
    await query.edit_message_text(
        f"Выбрана услуга: {service}\n\nВыберите врача:",
        reply_markup=doctors_keyboard()
    )
    return DOCTOR

async def select_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    doctor = query.data.replace("doctor_", "")
    context.user_data['doctor'] = doctor
    await query.edit_message_text(
        f"Выбран врач: {doctor}\n\nВыберите дату:",
        reply_markup=dates_keyboard()
    )
    return DATE

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    date = query.data.replace("date_", "")
    context.user_data['date'] = date
    await query.edit_message_text(
        f"Выбрана дата: {date}\n\nВыберите время:",
        reply_markup=time_keyboard()
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
        'date': context.user_data['date'],
        'time': context.user_data['time']
    }
    await query.edit_message_text(
        f"📋 Подтверждение записи:\n\n"
        f"👨‍⚕️ Врач: {appointment_data['doctor']}\n"
        f"🦷 Услуга: {appointment_data['service']}\n"
        f"📅 Дата: {appointment_data['date']}\n"
        f"⏰ Время: {appointment_data['time']}\n\n"
        "Подтвердите запись:",
        reply_markup=confirm_keyboard(appointment_data)
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
        service_type=appointment_data['service'],
        appointment_date=appointment_data['date'],
        appointment_time=appointment_data['time']
    )
    await query.edit_message_text(
        f"✅ Запись подтверждена!\n\n"
        f"👨‍⚕️ Врач: {appointment_data['doctor']}\n"
        f"🦷 Услуга: {appointment_data['service']}\n"
        f"📅 Дата: {appointment_data['date']}\n"
        f"⏰ Время: {appointment_data['time']}\n\n"
        "Ждём вас на приём!"
    )
    context.user_data.clear()
    return ConversationHandler.END