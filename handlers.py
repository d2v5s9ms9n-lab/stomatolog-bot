from telegram import Update
from telegram.ext import ContextTypes
from config import SERVICES, CLINIC_NAME, CLINIC_ADDRESS, CLINIC_PHONE, ADMIN_ID
from database import Session, Appointment
from keyboards import service_menu, confirmation_menu, ton_payment_menu
from calendar import get_calendar_keyboard, get_time_slots_keyboard, get_current_month_year
from ton_wallet import wallet_manager, initialize_wallet_manager
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Initialize wallet manager
initialize_wallet_manager()

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
        text += f"Статус: {apt.status}\n"
        if apt.payment_status != 'unpaid':
            text += f"💳 Оплата: {apt.payment_status}\n"
        text += "\n"
    
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
    
    # Check if wallet is initialized
    if not wallet_manager:
        text = "💳 Оплата TON\n\n"
        text += "⚠️ TON кошелёк не настроен.\n\n"
        text += "Для оплаты через TON необходимо настроить кошелёк.\n"
        text += "Обратитесь к администратору."
        await query.edit_message_text(text, reply_markup=main_menu())
        return
    
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
        appointment_id = appointment.id
    
    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 Новая запись!\n\n"
             f"👤 Пациент: {user.first_name} {user.last_name or ''}\n"
             f"📞 Тел: +7 999 123-45-67\n"
             f"📅 Дата: {selected_datetime.strftime('%d.%m.%Y %H:%M')}\n"
             f"📝 Услуга: {service['name']}\n"
             f"💰 Стоимость: {service['price']} ₽\n"
             f"🆔 ID записи: #{appointment_id}"
    )
    
    # Offer TON payment
    payment_text = (
        "✅ Запись подтверждена!\n\n"
        f"Вы записаны на {service['name']}\n"
        f"📅 {selected_datetime.strftime('%d.%m.%Y')} в {selected_datetime.strftime('%H:%M')}\n"
        f"💰 Стоимость: {service['price']} ₽\n\n"
    )
    
    # Add payment button if wallet is available
    if wallet_manager:
        payment_text += "💳 Хотите оплатить через TON сейчас?\n"
        payment_text += "(Оплата не обязательна для записи)"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("💸 Оплатить TON сейчас", callback_data=f'pay_now_{appointment_id}')],
            [InlineKeyboardButton("⏭️ Оплатить позже", callback_data='skip_payment')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        payment_text += "\nВ ближайшее время с вами свяжется администратор для подтверждения."
        reply_markup = main_menu()
    
    await query.edit_message_text(payment_text, reply_markup=reply_markup)
    
    # Clear user data
    context.user_data.clear()

async def handle_payment_now(update: Update, context: ContextTypes.DEFAULT_TYPE, appointment_id: int):
    """Handle immediate TON payment."""
    query = update.callback_query
    
    if not wallet_manager:
        await query.answer("TON кошелёк не настроен")
        return
    
    # Get appointment details
    with Session() as session:
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        if not appointment:
            await query.answer("Запись не найдена")
            return
    
    # Calculate TON amount (example: 1 TON = 100 ₽)
    ton_rate = 100  # Placeholder rate
    ton_amount = appointment.price / ton_rate
    
    # Create invoice
    invoice = await wallet_manager.create_invoice(
        amount=ton_amount,
        description=f"Оплата: {appointment.service} ({appointment.date.strftime('%d.%m.%Y')})"
    )
    
    if "error" in invoice:
        await query.edit_message_text(
            f"❌ Ошибка при создании invoice: {invoice['error']}\n\n"
            "Попробуйте позже или свяжитесь с администратором.",
            reply_markup=main_menu()
        )
        return
    
    # Show payment instructions
    payment_text = (
        f"💸 Оплата TON\n\n"
        f"📝 Услуга: {appointment.service}\n"
        f"💰 Сумма: {appointment.price} ₽\n"
        f"🪙 TON: {ton_amount:.4f}\n\n"
        f"🔗 Ссылка для оплаты:\n"
        f"`{invoice['payment_link']}`\n\n"
        "Отсканируйте QR-код или перейдите по ссылке для оплаты.\n\n"
        "После оплаты нажмите 'Проверить платёж'"
    )
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("✅ Проверить платёж", callback_data=f'check_payment_{appointment_id}')],
        [InlineKeyboardButton("❌ Отмена", callback_data='cancel_payment')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(payment_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, appointment_id: int):
    """Check payment status."""
    query = update.callback_query
    
    if not wallet_manager:
        await query.answer("TON кошелёк не настроен")
        return
    
    # Check payment status
    status = await wallet_manager.check_payment(f"inv_{appointment_id}")
    
    if status.get('status') == 'paid':
        # Update appointment payment status
        with Session() as session:
            appointment = session.query(Appointment).filter_by(id=appointment_id).first()
            if appointment:
                appointment.payment_status = 'paid'
                appointment.payment_tx_hash = status.get('tx_hash')
                session.commit()
        
        await query.edit_message_text(
            "✅ Платёж подтверждён!\n\n"
            "Ваша запись полностью оплачена.\n"
            "Ждём вас в клинике!",
            reply_markup=main_menu()
        )
    else:
        await query.edit_message_text(
            "⏳ Платёж ещё не поступив.\n\n"
            "Попробуйте проверить позже или свяжитесь с администратором.",
            reply_markup=main_menu()
        )

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
    """Handle TON payment from main menu."""
    query = update.callback_query
    
    if not wallet_manager:
        await query.edit_message_text(
            "⚠️ TON кошелёк не настроен.\n\n"
            "Для оплаты через TON необходимо настроить кошелёк.\n"
            "Обратитесь к администратору.",
            reply_markup=main_menu()
        )
        return
    
    # Show user's unpaid appointments
    user_id = query.from_user.id
    with Session() as session:
        unpaid_appointments = session.query(Appointment).filter_by(
            patient_id=user_id, 
            payment_status='unpaid'
        ).all()
    
    if not unpaid_appointments:
        await query.edit_message_text(
            "💳 Оплата TON\n\n"
            "У вас нет неоплаченных записей.\n\n"
            "Запишитесь на приём и оплатите его через TON!",
            reply_markup=main_menu()
        )
        return
    
    # Show unpaid appointments
    text = "💳 Оплата TON\n\n"
    text += "Выберите запись для оплаты:\n\n"
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    
    for apt in unpaid_appointments:
        text += f"📝 {apt.service} — {apt.price} ₽\n"
        text += f"📅 {apt.date.strftime('%d.%m.%Y %H:%M')}\n\n"
        keyboard.append([InlineKeyboardButton(
            f"Оплатить {apt.service} ({apt.price} ₽)",
            callback_data=f'pay_now_{apt.id}'
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
