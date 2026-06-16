import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Bot
from config import TOKEN
from database import get_connection

logger = logging.getLogger(__name__)

async def send_notification(bot: Bot, user_id: int, message: str):
    """Отправить уведомление пользователю"""
    try:
        await bot.send_message(chat_id=user_id, text=message)
        logger.info(f"Уведомление отправлено пользователю {user_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
        return False

async def check_appointments_for_notifications():
    """Проверить записи на необходимость уведомлений"""
    bot = Bot(token=TOKEN)
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now()
    
    # Уведомление за 24 часа
    tomorrow = now + timedelta(days=1)
    cursor.execute("""
        SELECT a.id, u.telegram_id, u.full_name, a.doctor_name, 
               a.appointment_date, a.appointment_time
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.appointment_date = %s 
          AND a.status = 'confirmed'
          AND a.notified_24h = FALSE
    """, (tomorrow.date(),))
    
    appointments_24h = cursor.fetchall()
    
    for app in appointments_24h:
        appointment_id, telegram_id, full_name, doctor_name, app_date, app_time = app
        message = (
            f"🔔 Напоминание о записи\n\n"
            f"👤 {full_name}\n"
            f"👨‍⚕️ Врач: {doctor_name}\n"
            f"📅 Дата: {app_date}\n"
            f"⏰ Время: {app_time}\n\n"
            f"Ждём вас завтра!"
        )
        
        success = await send_notification(bot, telegram_id, message)
        if success:
            cursor.execute(
                "UPDATE appointments SET notified_24h = TRUE WHERE id = %s",
                (appointment_id,)
            )
    
    # Уведомление за 1 час
    hour_later = now + timedelta(hours=1)
    cursor.execute("""
        SELECT a.id, u.telegram_id, u.full_name, a.doctor_name, 
               a.appointment_date, a.appointment_time
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        WHERE a.appointment_date = %s 
          AND a.appointment_time BETWEEN %s AND %s
          AND a.status = 'confirmed'
          AND a.notified_1h = FALSE
    """, (now.date(), now.time(), hour_later.time()))
    
    appointments_1h = cursor.fetchall()
    
    for app in appointments_1h:
        appointment_id, telegram_id, full_name, doctor_name, app_date, app_time = app
        message = (
            f"⏰ Скоро ваш приём!\n\n"
            f"👤 {full_name}\n"
            f"👨‍⚕️ Врач: {doctor_name}\n"
            f"📅 Дата: {app_date}\n"
            f"⏰ Время: {app_time}\n\n"
            f"Пожалуйста, будьте вовремя!"
        )
        
        success = await send_notification(bot, telegram_id, message)
        if success:
            cursor.execute(
                "UPDATE appointments SET notified_1h = TRUE WHERE id = %s",
                (appointment_id,)
            )
    
    conn.commit()
    cursor.close()
    conn.close()

async def notification_scheduler():
    """Планировщик уведомлений"""
    while True:
        try:
            await check_appointments_for_notifications()
            await asyncio.sleep(60)  # Проверка каждую минуту
        except Exception as e:
            logger.error(f"Ошибка в планировщике уведомлений: {e}")
            await asyncio.sleep(60)