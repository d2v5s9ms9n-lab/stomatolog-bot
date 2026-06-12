# Stomatolog Bot

Telegram bot for dental appointment booking with TON payments integration.

## Features

- 📅 Appointment booking system
- 💰 TON cryptocurrency payments
- 🔔 Automated reminders
- 📊 Admin dashboard
- 📱 Telegram integration

## Getting Started

### Prerequisites

- Python 3.9+
- Telegram Bot Token
- TON wallet

### Installation

```bash
# Clone the repository
git clone https://github.com/d2v5s9ms9n-lab/stomatolog-bot.git
cd stomatolog-bot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your tokens

# Run the bot
python bot.py
```

## Configuration

Create a `.env` file with:

```env
BOT_TOKEN=your_telegram_bot_token
TON_WALLET_ADDRESS=your_ton_wallet_address
ADMIN_ID=your_telegram_id
```

## Usage

1. Start the bot: `/start`
2. Choose a service
3. Select date and time
4. Confirm appointment
5. Pay with TON (optional)

## Project Structure

```
├── bot.py              # Main bot file
├── database.py         # Database operations
├── handlers.py         # Message handlers
├── keyboards.py        # Inline keyboards
├── config.py           # Configuration
├── requirements.txt    # Dependencies
└── .env.example        # Environment template
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.