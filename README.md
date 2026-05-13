# Notletters-Email-bot

Бот для NotLetters — держишь список почт, читаешь письма, меняешь пароли.

## Запуск

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Рядом положи `.env` с токенами:

```
TELEGRAM_BOT_TOKEN=...
NOTLETTERS_API_KEY=...
NOTLETTERS_API_BASE_URL=https://api.notletters.com
LOG_LEVEL=INFO
NEW_PASSWORD=пароль
```

```bash
python -m src.main
```
