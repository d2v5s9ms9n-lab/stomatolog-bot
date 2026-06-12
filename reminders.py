"""Reminders system for stomatolog bot."""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from sqlalchemy import and_
from database import Session, Appointment
from config import ADMIN_ID
import asyncio

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

class ReminderSystem:
    """System for managing appointment reminders."""
    
    def __init__(self, bot):
        """Initialize reminder system.
        
        Args:
            bot: Telegram bot instance
        """
        self.bot = bot
        self.scheduler = scheduler
        self.scheduler.start()
        logger.info("Reminder system initialized")
    
    async def send_reminder(self, appointment_id: int, hours_before: int):
        """Send reminder to patient.
        
        Args:
            appointment_id: Appointment ID
            hours_before: Hours before appointment
        """
        try:
            with Session() as session:
                appointment = session.query(Appointment).filter_by(id=appointment_id).first()
                
                if not appointment:
                    logger.warning(f"Appointment {appointment_id} not found")
                    return
                
                if appointment.status == 'cancelled':
                    logger.info(f"Appointment {appointment_id} is cancelled, skipping reminder")
                    return
                
                # Calculate time until appointment
                time_until = appointment.date - datetime.now()
                hours_until = time_until.total_seconds() / 3600
                
                # Skip if appointment is in the past or too far
                if hours_until < 0:
                    logger.info(f"Appointment {appointment_id} is in the past, skipping")
                    return
                
                if hours_until > 48:
                    logger.info(f"Appointment {appointment_id} is too far, skipping")
                    return
                
                # Prepare reminder message
                if hours_before == 24:
                    reminder_text = (
                        f"🔔 Напоминание\n\n"
                        f"У вас запись к стоматологу завтра!\n\n"
                        f"📅 Дата: {appointment.date.strftime('%d.%m.%Y')}\n"
                        f"⏰ Время: {appointment.date.strftime('%H:%M')}\n"
                        f"📝 Услуга: {appointment.service}\n\n"
                        f"Не забудьте взять с собой паспорт и полис.\n"
                        f"Ждём вас! 🦷"
                    )
                elif hours_before == 1:
                    reminder_text = (
                        f"🔔 Срочное напоминание\n\n"
                        f"У вас запись к стоматологу через час!\n\n"
                        f"📅 Дата: {appointment.date.strftime('%d.%m.%Y')}\n"
                        f"⏰ Время: {appointment.date.strftime('%H:%M')}\n"
                        f"📝 Услуга: {appointment.service}\n\n"
                        f"Пожалуйста, будьте пунктуальны! 🦷"
                    )
                else:
                    reminder_text = (
                        f"🔔 Напоминание о записи\n\n"
                        f"У вас запись к стоматологу через {hours_before} час(ов)!\n\n"
                        f"📅 Дата: {appointment.date.strftime('%d.%m.%Y')}\n"
                        f"⏰ Время: {appointment.date.strftime('%H:%M')}\n"
                        f"📝 Услуга: {appointment.service}\n\n"
                        f"Ждём вас! 🦷"
                    )
                
                # Send reminder
                await self.bot.send_message(
                    chat_id=appointment.patient_id,
                    text=reminder_text
                )
                
                logger.info(f"Reminder sent for appointment {appointment_id} ({hours_before}h before)")
                
        except Exception as e:
            logger.error(f"Failed to send reminder for appointment {appointment_id}: {e}")
    
    def schedule_reminder(self, appointment_id: int, appointment_date: datetime, hours_before: int):
        """Schedule reminder for appointment.
        
        Args:
            appointment_id: Appointment ID
            appointment_date: Appointment date
            hours_before: Hours before appointment to send reminder
        """
        # Calculate when to send reminder
        reminder_time = appointment_date - timedelta(hours=hours_before)
        
        # Don't schedule if reminder time is in the past
        if reminder_time < datetime.now():
            logger.warning(f"Reminder time for appointment {appointment_id} is in the past")
            return
        
        # Schedule the reminder
        self.scheduler.add_job(
            self.send_reminder,
            trigger=DateTrigger(run_date=reminder_time),
            args=[appointment_id, hours_before],
            id=f"reminder_{appointment_id}_{hours_before}",
            replace_existing=True
        )
        
        logger.info(
            f"Scheduled reminder for appointment {appointment_id} "
            f"at {reminder_time.strftime('%d.%m.%Y %H:%M')} ({hours_before}h before)"
        )
    
    def schedule_all_reminders(self, appointment_id: int, appointment_date: datetime):
        """Schedule all reminders for appointment.
        
        Args:
            appointment_id: Appointment ID
            appointment_date: Appointment date
        """
        # Schedule 24-hour reminder
        self.schedule_reminder(appointment_id, appointment_date, 24)
        
        # Schedule 1-hour reminder
        self.schedule_reminder(appointment_id, appointment_date, 1)
        
        logger.info(f"All reminders scheduled for appointment {appointment_id}")
    
    def cancel_reminders(self, appointment_id: int):
        """Cancel all reminders for appointment.
        
        Args:
            appointment_id: Appointment ID
        """
        # Cancel 24-hour reminder
        try:
            self.scheduler.remove_job(f"reminder_{appointment_id}_24")
        except Exception:
            pass
        
        # Cancel 1-hour reminder
        try:
            self.scheduler.remove_job(f"reminder_{appointment_id}_1")
        except Exception:
            pass
        
        logger.info(f"Cancelled reminders for appointment {appointment_id}")
    
    def reschedule_reminders(self, appointment_id: int, new_date: datetime):
        """Reschedule reminders for appointment.
        
        Args:
            appointment_id: Appointment ID
            new_date: New appointment date
        """
        # Cancel existing reminders
        self.cancel_reminders(appointment_id)
        
        # Schedule new reminders
        self.schedule_all_reminders(appointment_id, new_date)
        
        logger.info(f"Rescheduled reminders for appointment {appointment_id} to {new_date}")

# Global reminder system instance
reminder_system: ReminderSystem = None

def initialize_reminder_system(bot):
    """Initialize global reminder system.
    
    Args:
        bot: Telegram bot instance
    """
    global reminder_system
    reminder_system = ReminderSystem(bot)
    return reminder_system

async def send_admin_notification(appointment_id: int, notification_type: str = "new"):
    """Send notification to admin about appointment.
    
    Args:
        appointment_id: Appointment ID
        notification_type: Type of notification (new, cancelled, completed)
    """
    try:
        with Session() as session:
            appointment = session.query(Appointment).filter_by(id=appointment_id).first()
            
            if not appointment:
                logger.warning(f"Appointment {appointment_id} not found")
                return
            
            if notification_type == "new":
                text = (
                    f"🆕 Новая запись!\n\n"
                    f"👤 Пациент: {appointment.patient_name}\n"
                    f"📞 Тел: {appointment.patient_phone}\n"
                    f"📅 Дата: {appointment.date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📝 Услуга: {appointment.service}\n"
                    f"💰 Стоимость: {appointment.price} ₽\n"
                    f"🆔 ID: #{appointment.id}"
                )
            elif notification_type == "cancelled":
                text = (
                    f"❌ Запись отменена\n\n"
                    f"👤 Пациент: {appointment.patient_name}\n"
                    f"📅 Дата: {appointment.date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📝 Услуга: {appointment.service}\n"
                    f"🆔 ID: #{appointment.id}"
                )
            elif notification_type == "completed":
                text = (
                    f"✅ Запись выполнена\n\n"
                    f"👤 Пациент: {appointment.patient_name}\n"
                    f"📅 Дата: {appointment.date.strftime('%d.%m.%Y %H:%M')}\n"
                    f"📝 Услуга: {appointment.service}\n"
                    f"🆔 ID: #{appointment.id}"
                )
            
            # Send notification to admin
            # Note: This would need bot instance, handled in handlers
            logger.info(f"Admin notification prepared: {notification_type} appointment {appointment_id}")
            
    except Exception as e:
        logger.error(f"Failed to prepare admin notification: {e}")
