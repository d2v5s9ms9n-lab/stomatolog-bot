# 🦷 Dental Bot

Telegram bot for dental appointments booking.

## Features
- Book appointments with doctors
- Select service, doctor, date and time
- View your appointments
- Simple and user-friendly interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```env
BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@localhost:5432/dental_bot
ADMIN_IDS=123456789
```

3. Run the bot:
```bash
python bot.py
```

## Commands
- `/start` - Start the bot
- `/book` - Book an appointment