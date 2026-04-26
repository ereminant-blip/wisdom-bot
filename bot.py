import logging
from datetime import time
import random
import pytz
import sys
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = “8725776252:AAE1QI_Sl_UgsFvBZtnYa71PE6n5h8qyoh0”
CHAT_ID = 586687616
SEND_HOUR = 7
SEND_MINUTE = 0
TIMEZONE = “Europe/Moscow”

sys.path.insert(0, os.path.dirname(**file**))
from quotes import QUOTES

async def send_daily_quote(context: ContextTypes.DEFAULT_TYPE):
job_data = context.job.data
quote = QUOTES[job_data[“index”] % len(QUOTES)]
job_data[“index”] += 1
message = f”{quote[‘title’]}\n\n_{quote[‘text’]}_\n\n{quote[‘reflection’]}”
await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=“Markdown”)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“Мудрость древних - ежедневный бот\n\n”
“Каждое утро в 7:00 по Москве - отрывок из великих текстов человечества.\n\n”
f”В коллекции {len(QUOTES)} отрывков из:\n”
“- Эпоса о Гильгамеше и Египта\n”
“- Библии (Ветхий и Новый завет)\n”
“- Платона, Аристотеля, Сократа\n”
“- Марка Аврелия, Сенеки, Эпиктета\n”
“- Лао-цзы, Конфуция, Чжуан-цзы\n”
“- Бхагавад-гиты, Дхаммапады\n”
“- Руми, Хафиза, Омара Хайяма\n”
“- Августина, Фомы Аквинского, Данте\n”
“- Монтеня, Паскаля, Канта, Спинозы\n”
“- Ницше, Достоевского, Толстого и других\n\n”
“Используйте /quote чтобы получить отрывок прямо сейчас.”
)

async def quote_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
quote = random.choice(QUOTES)
message = f”{quote[‘title’]}\n\n_{quote[‘text’]}_\n\n{quote[‘reflection’]}”
await update.message.reply_text(message, parse_mode=“Markdown”)

def main():
logging.basicConfig(level=logging.INFO)
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler(“start”, start))
app.add_handler(CommandHandler(“quote”, quote_now))

```
tz = pytz.timezone(TIMEZONE)
send_time = time(hour=SEND_HOUR, minute=SEND_MINUTE, tzinfo=tz)
job_data = {"index": 0}
app.job_queue.run_daily(send_daily_quote, time=send_time, data=job_data, name="daily_wisdom")

print(f"Bot started. Quotes: {len(QUOTES)}. Sending at {SEND_HOUR}:{SEND_MINUTE:02d} Moscow time.")
app.run_polling()
```

if **name** == “**main**”:
main()