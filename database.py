import psycopg2
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            full_name VARCHAR(255),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            doctor_name VARCHAR(255),
            service_type VARCHAR(255),
            appointment_date DATE,
            appointment_time TIME,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("База данных инициализирована")

def get_or_create_user(telegram_id, full_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        cursor.execute(
            "INSERT INTO users (telegram_id, full_name) VALUES (%s, %s) RETURNING id",
            (telegram_id, full_name)
        )
        user_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return user_id

def create_appointment(user_id, doctor_name, service_type, appointment_date, appointment_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (user_id, doctor_name, service_type, appointment_date, appointment_time)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """, (user_id, doctor_name, service_type, appointment_date, appointment_time))
    appointment_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return appointment_id