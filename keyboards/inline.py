from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📅 Записаться на приём", callback_data='book_appointment')],
        [InlineKeyboardButton("📋 Мои записи", callback_data='my_appointments')],
        [InlineKeyboardButton("ℹ️ О нас", callback_data='about')]
    ]
    return InlineKeyboardMarkup(keyboard)

def services_keyboard():
    services = [
        ("🦷 Консультация", "service_consultation", "Первичный осмотр и диагностика"),
        ("🦷 Лечение кариеса", "service_caries", "Лечение кариеса любой сложности"),
        ("🦷 Удаление зуба", "service_extraction", "Удаление зубов мудрости и других"),
        ("🦷 Чистка зубов", "service_cleaning", "Профессиональная чистка и отбеливание"),
        ("🦷 Протезирование", "service_prosthesis", "Установка коронок, мостов, протезов"),
        ("🦷 Имплантация", "service_implantation", "Установка имплантов"),
        ("🦷 Лечение дёсен", "service_gums", "Лечение пародонтита и гингивита"),
        ("🦷 Детская стоматология", "service_children", "Лечение зубов у детей")
    ]
    
    keyboard = []
    for name, callback, description in services:
        keyboard.append([InlineKeyboardButton(f"{name} - {description}", callback_data=callback)])
    
    return InlineKeyboardMarkup(keyboard)

def doctors_keyboard():
    doctors = [
        ("👨‍⚕️ Иванов И.И. - Терапевт", "doctor_ivanov"),
        ("👩‍⚕️ Петрова А.А. - Хирург", "doctor_petrova"),
        ("👨‍⚕️ Сидоров В.В. - Ортопед", "doctor_sidorov"),
        ("👩‍⚕️ Козлова Е.М. - Детский стоматолог", "doctor_kozlova")
    ]
    keyboard = [[InlineKeyboardButton(name, callback_data=callback)] for name, callback in doctors]
    return InlineKeyboardMarkup(keyboard)

def dates_keyboard():
    keyboard = []
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y (%A)")
        callback = f"date_{date.strftime('%Y-%m-%d')}"
        keyboard.append([InlineKeyboardButton(date_str, callback_data=callback)])
    return InlineKeyboardMarkup(keyboard)

def time_keyboard():
    times = [
        ("09:00", "Утро"),
        ("10:00", "Утро"),
        ("11:00", "Утро"),
        ("12:00", "Обед"),
        ("14:00", "День"),
        ("15:00", "День"),
        ("16:00", "День"),
        ("17:00", "Вечер")
    ]
    keyboard = [[InlineKeyboardButton(f"{time} ({period})", callback_data=f"time_{time}")] for time, period in times]
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard(appointment_data):
    callback = f"confirm_{appointment_data['doctor']}_{appointment_data['service']}_{appointment_data['date']}_{appointment_data['time']}"
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=callback)],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking")]
    ]
    return InlineKeyboardMarkup(keyboard)