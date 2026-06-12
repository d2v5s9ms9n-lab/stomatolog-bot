from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from config import WORKING_HOURS, APPOINTMENT_DURATION
import calendar

def get_calendar_keyboard(year: int, month: int, selected_date: datetime = None):
    """Generate calendar keyboard for month selection."""
    keyboard = []
    
    # Month and year header
    month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    header_text = f"{month_names[month-1]} {year}"
    keyboard.append([InlineKeyboardButton(header_text, callback_data='ignore')])
    
    # Weekday headers
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    weekday_row = [InlineKeyboardButton(day, callback_data='ignore') for day in weekdays]
    keyboard.append(weekday_row)
    
    # Get calendar matrix
    cal = calendar.monthcalendar(year, month)
    
    # Generate day buttons
    today = datetime.now().date()
    max_date = today + timedelta(days=30)  # Only 30 days ahead
    
    for week in cal:
        week_row = []
        for day in week:
            if day == 0:
                # Empty day
                week_row.append(InlineKeyboardButton(' ', callback_data='ignore'))
            else:
                date = datetime(year, month, day).date()
                
                # Check if date is valid (not past, not too far, not weekend)
                if date < today:
                    # Past date - disabled
                    week_row.append(InlineKeyboardButton(f'{day}', callback_data='ignore'))
                elif date > max_date:
                    # Too far ahead - disabled
                    week_row.append(InlineKeyboardButton(f'{day}', callback_data='ignore'))
                elif date.weekday() >= 5:  # Weekend (5=Saturday, 6=Sunday)
                    # Weekend - disabled
                    week_row.append(InlineKeyboardButton(f'{day}', callback_data='ignore'))
                else:
                    # Valid date - clickable
                    callback_data = f'date_{year}_{month}_{day}'
                    week_row.append(InlineKeyboardButton(f'{day}', callback_data=callback_data))
        keyboard.append(week_row)
    
    # Navigation buttons
    nav_row = []
    # Previous month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    nav_row.append(InlineKeyboardButton('◀️ Пред. месяц', callback_data=f'calendar_{prev_year}_{prev_month}'))
    
    # Next month
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    nav_row.append(InlineKeyboardButton('След. месяц ▶️', callback_data=f'calendar_{next_year}_{next_month}'))
    keyboard.append(nav_row)
    
    # Back button
    keyboard.append([InlineKeyboardButton('🔙 Назад к услугам', callback_data='back_to_services')])
    
    return InlineKeyboardMarkup(keyboard)

def get_time_slots_keyboard(date: datetime):
    """Generate time slots for selected date."""
    keyboard = []
    
    # Generate time slots from WORKING_HOURS
    start_hour = WORKING_HOURS['start']
    end_hour = WORKING_HOURS['end']
    lunch_start = WORKING_HOURS['lunch_start']
    lunch_end = WORKING_HOURS['lunch_end']
    
    current_hour = start_hour
    row = []
    
    while current_hour < end_hour:
        # Skip lunch time
        if lunch_start <= current_hour < lunch_end:
            current_hour += 1
            continue
        
        # Create time button
        time_str = f'{current_hour:02d}:00'
        callback_data = f'time_{date.strftime("%Y_%m_%d")}_{current_hour}_00'
        
        row.append(InlineKeyboardButton(time_str, callback_data=callback_data))
        
        # Add to keyboard (2 buttons per row)
        if len(row) == 2:
            keyboard.append(row)
            row = []
        
        current_hour += 1
    
    # Add remaining buttons
    if row:
        keyboard.append(row)
    
    # Back button
    keyboard.append([InlineKeyboardButton('🔙 Назад к календарю', callback_data='back_to_calendar')])
    
    return InlineKeyboardMarkup(keyboard)

def get_current_month_year():
    """Get current month and year."""
    now = datetime.now()
    return now.year, now.month
