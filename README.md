# Master Telegram Bot Management System

A powerful FastAPI-based control panel to host and manage multiple Telegram bots from a single dashboard.

## Features

- **Multi-Bot Management**: Host and control multiple Telegram bots simultaneously
- **Password-Protected Admin Access**: Secure authentication system
- **Real-time Dashboard**: Monitor all bots status at a glance
- **Bot Lifecycle Control**: Start, stop, and restart bots individually
- **Activity Logging**: Track all admin actions
- **REST API**: Programmatic access to manage bots
- **Web Interface**: Beautiful dark-themed dashboard

## Requirements

- Python 3.10+
- Telegram Bot Token (from @BotFather)

## Quick Start

### 1. Clone and Install

```bash
cd master_bot

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 2. Configure

Edit `.env` file with your settings:

```env
# Change these for security!
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Your Telegram bot token will be added when creating bots
```

### 3. Initialize and Run

```bash
# Create required directories
mkdir -p data/bots data/logs

# Start the server
python main.py
```

### 4. Access Dashboard

Open your browser and navigate to:
```
http://localhost:8000/admin/login
```

Default credentials:
- Username: `admin`
- Password: `admin123` (change this!)

## Usage

### Adding a Bot

1. Go to "Add New Bot" in the sidebar
2. Enter your bot name (e.g., "My Test Bot")
3. Paste your Telegram bot token from @BotFather
4. Add an optional description
5. Click "Add Bot"

### Managing Bots

From the dashboard you can:
- **Start**: Launch a bot
- **Stop**: Shutdown a running bot
- **Restart**: Quick restart for a bot
- **Edit**: Update bot details
- **Delete**: Remove a bot completely

### Using the API

```bash
# Get all bots
curl http://localhost:8000/api/bots

# Start a bot
curl -X POST http://localhost:8000/api/bots/1/start

# Stop a bot
curl -X POST http://localhost:8000/api/bots/1/stop
```

## Project Structure

```
master_bot/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py    # Configuration management
│   │   ├── security.py  # Authentication & security
│   │   └── logging.py   # Logging setup
│   ├── db/
│   │   ├── models.py    # Database models
│   │   └── init_db.py   # Database initialization
│   ├── routers/
│   │   ├── auth.py      # Authentication routes
│   │   ├── dashboard.py # Dashboard routes
│   │   ├── bots.py      # Bot management routes
│   │   └── api.py       # REST API routes
│   ├── services/
│   │   └── bot_manager.py  # Bot lifecycle management
│   ├── static/
│   │   └── css/
│   │       └── styles.css  # Dashboard styling
│   └── templates/
│       ├── base.html        # Base template
│       ├── login.html       # Login page
│       ├── dashboard.html   # Main dashboard
│       ├── bots.html        # Bot list
│       ├── bot_form.html    # Add/Edit bot
│       ├── settings.html    # Settings page
│       └── logs.html        # Activity logs
└── data/
    ├── master_bot.db    # SQLite database (auto-created)
    ├── bots/            # Bot configurations
    └── logs/            # Application logs
```

## Security Recommendations

1. **Change Default Credentials**: Update admin username and password immediately
2. **Use Strong Secret Key**: Generate a strong SECRET_KEY for JWT tokens
3. **Environment Variables**: Never commit `.env` to version control
4. **HTTPS in Production**: Use HTTPS when deploying to production
5. **Rate Limiting**: Implement rate limiting for API endpoints

## Default Commands for Bots

Each managed bot comes with built-in commands:
- `/start` - Welcome message
- `/help` - Help information
- `/status` - Bot status check

## Troubleshooting

### Bot won't start
- Check if the bot token is valid
- Ensure no other instance is running on the same token
- Check logs in `data/logs/`

### Can't access dashboard
- Verify you're using the correct credentials
- Check if the server is running
- Clear browser cache and cookies

### Database issues
- Delete `data/master_bot.db` and restart to reset
- Ensure the `data/` directory is writable

## License

MIT License - Feel free to use and modify!

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

Built with ❤️ using FastAPI, aiogram, and modern web technologies.
