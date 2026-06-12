import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, ADMIN_ID
from database import Session, Appointment, Patient
from keyboards import main_menu
import handlers
from calendar import get_current_month_year

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    user = update.effective_user
    with Session() as session:
        patient = session.query(Patient).filter_by(telegram_id=user.id).first()
        if not patient:
            patient = Patient(telegram_id=user.id, first_name=user.first_name, last_name=user.last_name)
            session.add(patient)
            session.commit()
    await update.message.reply_text(f'👋 Привет, {user.first_name}!\n\nЯ бот клиники стоматолога Али.\n\nЧем могу помочь?', reply_markup=main_menu())

async def handle_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Calendar navigation
    if data.startswith('calendar_'):
        parts = data.split('_')
        year = int(parts[1])
        month = int(parts[2])
        await handlers.handle_calendar(update, context, year, month)
    
    # Date selection
    elif data.startswith('date_'):
        parts = data.split('_')
        year = int(parts[1])
        month = int(parts[2])
        day = int(parts[3])
        await handlers.handle_date_selection(update, context, year, month, day)
    
    # Time selection
    elif data.startswith('time_'):
        parts = data.split('_')
        year = int(parts[1])
        month = int(parts[2])
        day = int(parts[3])
        hour = int(parts[4])
        minute = int(parts[5])
        await handlers.handle_time_selection(update, context, year, month, day, hour, minute)
    
    # Service selection
    elif data.startswith('service_'):
        service_key = data.split('_')[1]
        await handlers.select_service(update, context, service_key)
    
    # Navigation buttons
    elif data == 'book':
        await handlers.show_services(update, context)
    elif data == 'my_appointments':
        await handlers.show_appointments(update, context)
    elif data == 'info':
        await handlers.show_info(update, context)
    elif data == 'ton_payment':
        await handlers.show_ton_payment(update, context)
    elif data == 'back_to_main':
        await query.edit_message_text('Чем могу помочь?', reply_markup=main_menu())
    elif data == 'back_to_services':
        await handlers.show_services(update, context)
    elif data == 'back_to_calendar':
        year, month = get_current_month_year()
        await handlers.handle_calendar(update, context, year, month)
    elif data == 'confirm_appointment':
        await handlers.confirm_appointment(update, context)
    elif data == 'cancel_appointment':
        await handlers.cancel_appointment(update, context)
    elif data == 'pay_with_ton':
        await handlers.pay_with_ton(update, context)
    elif data == 'ignore':
        pass  # Do nothing for disabled buttons

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    logger.info('Bot started')
    app.run_polling()

if __name__ == '__main__':
    main()
