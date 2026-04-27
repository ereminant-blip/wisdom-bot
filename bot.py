import logging
from datetime import time
import random
import pytz
import sys
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8725776252:AAE1QI_Sl_UgsFvBZtnYa71PE6n5h8qyoh0"

CHAT_IDS = [
    586687616,
    -1003632635325,
]

SEND_TIMES = [
    (7, 30),
    (13, 2),
]

TIMEZONE = "Europe/Moscow"

sys.path.insert(0, os.path.dirname(__file__))
from quotes import QUOTES


async def send_daily_quote(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    quote = QUOTES[job_data["index"] % len(QUOTES)]
    job_data["index"] += 1
    message = f"{quote['title']}\n\n_{quote['text']}_\n\n{quote['reflection']}"
    for chat_id in CHAT_IDS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Мудрость древних - ежедневный бот\n\n"
        "Отрывки отправляются в 7:30 и 13:05 по Москве.\n\n"
        f"В коллекции {len(QUOTES)} отрывков.\n\n"
        "Используйте /quote чтобы получить отрывок прямо сейчас."
    )


async def quote_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    message = f"{quote['title']}\n\n_{quote['text']}_\n\n{quote['reflection']}"
    await update.message.reply_text(message, parse_mode="Markdown")


def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quote", quote_now))

    tz = pytz.timezone(TIMEZONE)
    job_data = {"index": 0}

    for hour, minute in SEND_TIMES:
        send_time = time(hour=hour, minute=minute, tzinfo=tz)
        app.job_queue.run_daily(
            send_daily_quote,
            time=send_time,
            data=job_data,
            name=f"daily_wisdom_{hour}_{minute}"
        )
        print(f"Scheduled at {hour}:{minute:02d} Moscow time")

    print(f"Bot started. Quotes: {len(QUOTES)}. Sending to {len(CHAT_IDS)} chats.")
    app.run_polling()


if __name__ == "__main__":
    main()
