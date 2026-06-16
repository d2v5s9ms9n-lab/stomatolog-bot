import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
from config import TOKEN
from database import init_db
from handlers.start import start_command
from handlers.appointment import (
    book_appointment, select_service, select_doctor,
    select_date, select_time, confirm_booking,
    SERVICE, DOCTOR, DATE, TIME, CONFIRM
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def main():
    init_db()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("book", book_appointment)],
        states={
            SERVICE: [CallbackQueryHandler(select_service, pattern='^service_')],
            DOCTOR: [CallbackQueryHandler(select_doctor, pattern='^doctor_')],
            DATE: [CallbackQueryHandler(select_date, pattern='^date_')],
            TIME: [CallbackQueryHandler(select_time, pattern='^time_')],
            CONFIRM: [CallbackQueryHandler(confirm_booking, pattern='^confirm_')]
        },
        fallbacks=[CallbackQueryHandler(confirm_booking, pattern='^cancel_')]
    )
    application.add_handler(conv_handler)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())