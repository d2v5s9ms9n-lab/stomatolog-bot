from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer)
    patient_name = Column(String)
    patient_phone = Column(String)
    date = Column(DateTime)
    service = Column(String)
    price = Column(Float)
    status = Column(String, default='pending')
    payment_status = Column(String, default='unpaid')
    payment_tx_hash = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    duration = Column(Integer)
    is_active = Column(Boolean, default=True)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def init_services():
    with Session() as session:
        if not session.query(Service).first():
            services = [
                Service(name='Консультация', description='Первичный осмотр и консультация', price=1000, duration=30),
                Service(name='Лечение кариеса', description='Лечение кариеса любой сложности', price=3000, duration=60),
                Service(name='Профессиональная чистка', description='Удаление зубного камня и налета', price=2500, duration=45),
                Service(name='Отбеливание', description='Профессиональное отбеливание зубов', price=5000, duration=90),
            ]
            session.add_all(services)
            session.commit()

init_services()
