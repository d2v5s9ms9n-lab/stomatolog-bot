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
        ("🦷 Консультация", "service_consultation"),
        ("🦷 Лечение кариеса", "service_caries"),
        ("🦷 Удаление зуба", "service_extraction"),
        ("🦷 Чистка зубов", "service_cleaning"),
        ("🦷 Протезирование", "service_prosthesis")
    ]
    keyboard = [[InlineKeyboardButton(name, callback_data=callback)] for name, callback in services]
    return InlineKeyboardMarkup(keyboard)

def doctors_keyboard():
    doctors = [
        ("👨‍⚕️ Иванов И.И.", "doctor_ivanov"),
        ("👩‍⚕️ Петрова А.А.", "doctor_petrova"),
        ("👨‍⚕️ Сидоров В.В.", "doctor_sidorov")
    ]
    keyboard = [[InlineKeyboardButton(name, callback_data=callback)] for name, callback in doctors]
    return InlineKeyboardMarkup(keyboard)

def dates_keyboard():
    keyboard = []
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y")
        callback = f"date_{date.strftime('%Y-%m-%d')}"
        keyboard.append([InlineKeyboardButton(date_str, callback_data=callback)])
    return InlineKeyboardMarkup(keyboard)

def time_keyboard():
    times = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    keyboard = [[InlineKeyboardButton(time, callback_data=f"time_{time}")] for time in times]
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard(appointment_data):
    callback = f"confirm_{appointment_data['doctor']}_{appointment_data['service']}_{appointment_data['date']}_{appointment_data['time']}"
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=callback)],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_booking")]
    ]
    return InlineKeyboardMarkup(keyboard)