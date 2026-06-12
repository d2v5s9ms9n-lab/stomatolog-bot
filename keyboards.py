from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import SERVICES

def main_menu():
    keyboard = [
        [InlineKeyboardButton('📅 Записаться на приём', callback_data='book')],
        [InlineKeyboardButton('📋 Мои записи', callback_data='my_appointments')],
        [InlineKeyboardButton('ℹ️ О клинике', callback_data='info')],
        [InlineKeyboardButton('💳 Оплата TON', callback_data='ton_payment')],
    ]
    return InlineKeyboardMarkup(keyboard)

def service_menu():
    keyboard = []
    for key, service in SERVICES.items():
        keyboard.append([InlineKeyboardButton(
            f"{service['name']} — {service['price']} ₽",
            callback_data=f'service_{key}'
        )])
    keyboard.append([InlineKeyboardButton('🔙 Назад', callback_data='back_to_main')])
    return InlineKeyboardMarkup(keyboard)

def date_selection_menu():
    keyboard = [
        [InlineKeyboardButton('◀️ Предыдущая неделя', callback_data='prev_week')],
        [InlineKeyboardButton('Следующая неделя ▶️', callback_data='next_week')],
        [InlineKeyboardButton('🔙 Назад', callback_data='back_to_services')],
    ]
    return InlineKeyboardMarkup(keyboard)

def confirmation_menu():
    keyboard = [
        [InlineKeyboardButton('✅ Подтвердить запись', callback_data='confirm_appointment')],
        [InlineKeyboardButton('❌ Отмена', callback_data='cancel_appointment')],
    ]
    return InlineKeyboardMarkup(keyboard)

def ton_payment_menu():
    keyboard = [
        [InlineKeyboardButton('💸 Оплатить TON', callback_data='pay_with_ton')],
        [InlineKeyboardButton('📋 История платежей', callback_data='payment_history')],
        [InlineKeyboardButton('🔙 Назад', callback_data='back_to_main')],
    ]
    return InlineKeyboardMarkup(keyboard)
