## EJIE Azure Function

This project is a timer-triggered Azure Function that monitors EJIE public job postings.

On each run, it:
- Opens the EJIE listings page
- Detects open offers
- Reads each offer detail page and extracts the main information
- Sends a formatted notification to a Telegram chat

If something fails, it logs the error and sends an alert message to Telegram.

Required environment variables: `TIMER_SCHEDULE`, `BASE_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
