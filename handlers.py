from telegram import Update
from telegram.ext import ContextTypes
from config import SERVICES, CLINIC_NAME, CLINIC_ADDRESS, CLINIC_PHONE
from database import Session, Appointment
from keyboards import service_menu, confirmation_menu, ton_payment_menu
from calendar import get_calendar_keyboard, get_time_slots_keyboard, get_current_month_year
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available services."""
    query = update.callback_query
    await query.edit_message_text(
        "Выберите услугу:\n\n"
        "🦷 Консультация — 1000 ₽ (30 мин)\n"
        "🦷 Лечение кариеса — 3000 ₽ (60 мин)\n"
        "🦷 Проф. чистка — 2500 ₽ (45 мин)\n"
        "🦷 Отбеливание — 5000 ₽ (90 мин)",
        reply_markup=service_menu()
    )

async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's appointments."""
    query = update.callback_query
    user_id = query.from_user.id
    
    with Session() as session:
        appointments = session.query(Appointment).filter_by(patient_id=user_id).all()
    
    if not appointments:
        await query.edit_message_text(
            "У вас пока нет записей.\n\n"
            "Запишитесь на приём через главное меню.",
            reply_markup=main_menu()
        )
        return
    
    text = "📋 Ваши записи:\n\n"
    for apt in appointments:
        text += f"📅 {apt.date.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"📝 {apt.service}\n"
        text += f"Статус: {apt.status}\n\n"
    
    await query.edit_message_text(text, reply_markup=main_menu())

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show clinic information."""
    query = update.callback_query
    text = f"🏥 {CLINIC_NAME}\n\n"
    text += f"📍 {CLINIC_ADDRESS}\n"
    text += f"📞 {CLINIC_PHONE}\n\n"
    text += "🕒 Режим работы:\n"
    text += "Пн-Пт: 9:00 - 18:00\n"
    text += "Сб-Вс: выходной"
    
    await query.edit_message_text(text, reply_markup=main_menu())

async def show_ton_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show TON payment options."""
    query = update.callback_query
    text = "💳 Оплата TON\n\n"
    text += "Вы можете оплатить услуги криптовалютой TON.\n\n"
    text += "Преимущества:\n"
    text += "• Быстрые транзакции\n"
    text += "• Низкие комиссии\n"
    text += "• Безопасные платежи\n\n"
    text += "Выберите действие:"
    
    await query.edit_message_text(text, reply_markup=ton_payment_menu())

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service_key: str):
    """Handle service selection."""
    query = update.callback_query
    service = SERVICES.get(service_key)
    
    if not service:
        await query.answer("Услуга не найдена")
        return
    
    # Store selected service in context
    context.user_data['selected_service'] = service_key
    
    # Show calendar
    year, month = get_current_month_year()
    await query.edit_message_text(
        f"Вы выбрали: {service['name']}\n"
        f"Стоимость: {service['price']} ₽\n"
        f"Длительность: {service['duration']} мин\n\n"
        "Теперь выберите дату:",
        reply_markup=get_calendar_keyboard(year, month)
    )

async def handle_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, year: int, month: int):
    """Handle calendar navigation."""
    query = update.callback_query
    await query.edit_message_text(
        "Выберите дату:",
        reply_markup=get_calendar_keyboard(year, month)
    )

async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, year: int, month: int, day: int):
    """Handle date selection."""
    query = update.callback_query
    
    # Store selected date in context
    selected_date = datetime(year, month, day)
    context.user_data['selected_date'] = selected_date
    
    await query.edit_message_text(
        f"📅 Выбрана дата: {selected_date.strftime('%d.%m.%Y')}\n\n"
        "Теперь выберите время:",
        reply_markup=get_time_slots_keyboard(selected_date)
    )

async def handle_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, year: int, month: int, day: int, hour: int, minute: int):
    """Handle time selection."""
    query = update.callback_query
    
    # Store selected time in context
    selected_datetime = datetime(year, month, day, hour, minute)
    context.user_data['selected_datetime'] = selected_datetime
    
    # Get service info
    service_key = context.user_data.get('selected_service')
    service = SERVICES.get(service_key)
    
    if not service:
        await query.answer("Ошибка: услуга не выбрана")
        return
    
    await query.edit_message_text(
        f"✅ Вы выбрали:\n\n"
        f"📝 Услуга: {service['name']}\n"
        f"📅 Дата: {selected_datetime.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {selected_datetime.strftime('%H:%M')}\n"
        f"💰 Стоимость: {service['price']} ₽\n"
        f"⏱️ Длительность: {service['duration']} мин\n\n"
        "Подтвердите запись:",
        reply_markup=confirmation_menu()
    )

async def confirm_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm appointment."""
    query = update.callback_query
    user = query.from_user
    
    # Get appointment data from context
    service_key = context.user_data.get('selected_service')
    service = SERVICES.get(service_key)
    selected_datetime = context.user_data.get('selected_datetime')
    
    if not service or not selected_datetime:
        await query.answer("Ошибка: данные не найдены")
        return
    
    # Create appointment
    with Session() as session:
        appointment = Appointment(
            patient_id=user.id,
            patient_name=f"{user.first_name} {user.last_name or ''}",
            patient_phone="+7 999 123-45-67",  # TODO: Get from user input
            date=selected_datetime,
            service=service['name'],
            price=service['price'],
            status='pending'
        )
        session.add(appointment)
        session.commit()
    
    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Новая запись!\n\n"
             f"👤 Пациент: {user.first_name} {user.last_name or ''}\n"
             f"📞 Тел: +7 999 123-45-67\n"
             f"📅 Дата: {selected_datetime.strftime('%d.%m.%Y %H:%M')}\n"
             f"📝 Услуга: {service['name']}\n"
             f"💰 Стоимость: {service['price']} ₽"
    )
    
    await query.edit_message_text(
        "✅ Запись подтверждена!\n\n"
        f"Вы записаны на {service['name']}\n"
        f"📅 {selected_datetime.strftime('%d.%m.%Y')} в {selected_datetime.strftime('%H:%M')}\n"
        f"💰 Стоимость: {service['price']} ₽\n\n"
        "В ближайшее время с вами свяжется администратор для подтверждения.",
        reply_markup=main_menu()
    )
    
    # Clear user data
    context.user_data.clear()

async def cancel_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel appointment."""
    query = update.callback_query
    context.user_data.clear()
    await query.edit_message_text(
        "Запись отменена.\n\n"
        "Если хотите записаться снова, выберите услугу в главном меню.",
        reply_markup=main_menu()
    )

async def pay_with_ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle TON payment."""
    query = update.callback_query
    await query.answer("Функция оплаты TON в разработке")
    await query.edit_message_text(
        "💸 Оплата TON\n\n"
        "Функция оплаты криптовалютой TON находится в разработке.\n\n"
        "Скоро вы сможете оплачивать услуги напрямую через бота!",
        reply_markup=main_menu()
    )
