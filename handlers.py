from telegram import Update
from telegram.ext import ContextTypes
from config import SERVICES, CLINIC_NAME, CLINIC_ADDRESS, CLINIC_PHONE
from database import Session, Appointment
from keyboards import service_menu, date_selection_menu, confirmation_menu, ton_payment_menu
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text('Выберите услугу:\n\n🦷 Консультация — 1000 ₽ (30 мин)\n🦷 Лечение кариеса — 3000 ₽ (60 мин)\n🦷 Проф. чистка — 2500 ₽ (45 мин)\n🦷 Отбеливание — 5000 ₽ (90 мин)', reply_markup=service_menu())

async def show_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    with Session() as session:
        appointments = session.query(Appointment).filter_by(patient_id=user_id).all()
    if not appointments:
        await query.edit_message_text('У вас пока нет записей.\n\nЗапишитесь на приём через главное меню.', reply_markup=main_menu())
        return
    text = '📋 Ваши записи:\n\n'
    for apt in appointments:
        text += f'📅 {apt.date.strftime("%d.%m.%Y %H:%M")}\n'
        text += f'📝 {apt.service}\n'
        text += f'Статус: {apt.status}\n\n'
    await query.edit_message_text(text, reply_markup=main_menu())

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = f'🏥 {CLINIC_NAME}\n\n📍 {CLINIC_ADDRESS}\n📞 {CLINIC_PHONE}\n\n🕒 Режим работы:\nПн-Пт: 9:00 - 18:00\nСб-Вс: выходной'
    await query.edit_message_text(text, reply_markup=main_menu())

async def show_ton_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = '💳 Оплата TON\n\nВы можете оплатить услуги криптовалютой TON.\n\nПреимущества:\n• Быстрые транзакции\n• Низкие комиссии\n• Безопасные платежи\n\nВыберите действие:'
    await query.edit_message_text(text, reply_markup=ton_payment_menu())

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service_key: str):
    query = update.callback_query
    service = SERVICES.get(service_key)
    if not service:
        await query.answer('Услуга не найдена')
        return
    context.user_data['selected_service'] = service_key
    await query.edit_message_text(f'Вы выбрали: {service["name"]}\nСтоимость: {service["price"]} ₽\nДлительность: {service["duration"]} мин\n\nТеперь выберите дату:', reply_markup=date_selection_menu())

async def confirm_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    service_key = context.user_data.get('selected_service')
    service = SERVICES.get(service_key)
    if not service:
        await query.answer('Ошибка: услуга не выбрана')
        return
    with Session() as session:
        appointment = Appointment(
            patient_id=user.id,
            patient_name=f'{user.first_name} {user.last_name or ""}',
            patient_phone='+7 999 123-45-67',
            date=datetime.now() + timedelta(days=1),
            service=service['name'],
            price=service['price'],
            status='pending'
        )
        session.add(appointment)
        session.commit()
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f'🆕 Новая запись!\n\n👤 Пациент: {user.first_name} {user.last_name or ""}\n📞 Тел: +7 999 123-45-67\n📅 Дата: {datetime.now() + timedelta(days=1)}\n📝 Услуга: {service["name"]}\n💰 Стоимость: {service["price"]} ₽'
    )
    await query.edit_message_text(f'✅ Запись подтверждена!\n\nВы записаны на {service["name"]}\nСтоимость: {service["price"]} ₽\n\nВ ближайшее время с вами свяжется администратор для подтверждения.', reply_markup=main_menu())

async def cancel_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text('Запись отменена.\n\nЕсли хотите записаться снова, выберите услугу в главном меню.', reply_markup=main_menu())

async def pay_with_ton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer('Функция оплаты TON в разработке')
    await query.edit_message_text('💸 Оплата TON\n\nФункция оплаты криптовалютой TON находится в разработке.\n\nСкоро вы сможете оплачивать услуги напрямую через бота!', reply_markup=main_menu())
