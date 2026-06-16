import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

# Если изменяете эти области, удалите файл token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    """Получить учетные данные Google Calendar"""
    creds = None
    token_path = 'token.pickle'
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_calendar_event(appointment_data):
    """Создать событие в Google Calendar"""
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        # Парсинг даты и времени
        appointment_date = appointment_data['date']
        appointment_time = appointment_data['time']
        
        start_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M"
        )
        end_datetime = start_datetime + timedelta(hours=1)
        
        event = {
            'summary': f"Запись к стоматологу: {appointment_data['doctor']}",
            'description': f"Услуга: {appointment_data['service']}",
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Europe/Moscow',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},  # За 24 часа
                    {'method': 'popup', 'minutes': 60},       # За 1 час
                ],
            },
        }
        
        event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        logger.info(f"Событие создано: {event.get('htmlUrl')}")
        return event.get('id')
    
    except HttpError as error:
        logger.error(f"Ошибка создания события: {error}")
        return None

def update_calendar_event(event_id, appointment_data):
    """Обновить событие в Google Calendar"""
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        appointment_date = appointment_data['date']
        appointment_time = appointment_data['time']
        
        start_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M"
        )
        end_datetime = start_datetime + timedelta(hours=1)
        
        event = {
            'summary': f"Запись к стоматологу: {appointment_data['doctor']}",
            'description': f"Услуга: {appointment_data['service']}",
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Europe/Moscow',
            },
        }
        
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        logger.info(f"Событие обновлено: {updated_event.get('htmlUrl')}")
        return True
    
    except HttpError as error:
        logger.error(f"Ошибка обновления события: {error}")
        return False

def delete_calendar_event(event_id):
    """Удалить событие из Google Calendar"""
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        logger.info(f"Событие удалено: {event_id}")
        return True
    
    except HttpError as error:
        logger.error(f"Ошибка удаления события: {error}")
        return False