import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
TON_WALLET_ADDRESS = os.getenv('TON_WALLET_ADDRESS')
TON_WALLET_MNEMONIC = os.getenv('TON_WALLET_MNEMONIC')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///appointments.db')
CLINIC_NAME = os.getenv('CLINIC_NAME', 'Стоматолог Али')
CLINIC_ADDRESS = os.getenv('CLINIC_ADDRESS', 'Волгоград, ул. Примерная, 1')
CLINIC_PHONE = os.getenv('CLINIC_PHONE', '+7 999 123-45-67')
SERVICES = {
    'consultation': {'name': 'Консультация', 'price': 1000, 'duration': 30},
    'caries': {'name': 'Лечение кариеса', 'price': 3000, 'duration': 60},
    'cleaning': {'name': 'Профессиональная чистка', 'price': 2500, 'duration': 45},
    'whitening': {'name': 'Отбеливание', 'price': 5000, 'duration': 90},
}
WORKING_HOURS = {'start': 9, 'end': 18, 'lunch_start': 13, 'lunch_end': 14}
APPOINTMENT_DURATION = 30
MAX_DAYS_AHEAD = 30
