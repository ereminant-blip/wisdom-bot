import logging
from datetime import time
import random
import pytz
import sys
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8725776252:AAE1QI_Sl_UgsFvBZtnYa71PE6n5h8qyoh0"

PERSONAL_ID = 586687616
CHANNEL_ID = "@rassvetpotemki"

TIMEZONE = "Europe/Moscow"

sys.path.insert(0, os.path.dirname(__file__))
from quotes import QUOTES
from paintings import PAINTINGS
from phrases import PHRASES

random.shuffle(QUOTES)
random.shuffle(PAINTINGS)
random.shuffle(PHRASES)

quote_index = 0
painting_index = 0
phrase_index = 0


async def send_broadcast(bot, message):
    """Отправка в канал и лично."""
    for chat_id in [PERSONAL_ID, CHANNEL_ID]:
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")


async def send_personal(bot, message):
    """Отправка только лично."""
    try:
        await bot.send_message(chat_id=PERSONAL_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending to personal: {e}")


# 8:10 — философская цитата → канал + лично
async def send_quote(context: ContextTypes.DEFAULT_TYPE):
    global quote_index
    quote = QUOTES[quote_index % len(QUOTES)]
    quote_index += 1
    message = f"{quote['title']}\n\n_{quote['text']}_"
    await send_broadcast(context.bot, message)


# 9:45 — крылатая фраза → канал + лично
async def send_phrase(context: ContextTypes.DEFAULT_TYPE):
    global phrase_index
    phrase = PHRASES[phrase_index % len(PHRASES)]
    phrase_index += 1
    message = (
        f"🗣 *{phrase['phrase']}*\n\n"
        f"{phrase['meaning']}\n\n"
        f"_{phrase['origin']}_"
    )
    await send_broadcast(context.bot, message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Расписание канала:\n\n"
        "🏛 8:10 — философская мудрость (канал + лично)\n"
        "🗣 9:45 — крылатая фраза (канал + лично)\n\n"
        "Только лично:\n"
        "/quote — цитата\n"
        "/phrase — крылатая фраза\n"
        "/painting — картина для канала"
    )


async def quote_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global quote_index
    quote = QUOTES[quote_index % len(QUOTES)]
    quote_index += 1
    message = f"{quote['title']}\n\n_{quote['text']}_"
    await update.message.reply_text(message, parse_mode="Markdown")


async def phrase_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global phrase_index
    phrase = PHRASES[phrase_index % len(PHRASES)]
    phrase_index += 1
    message = (
        f"🗣 *{phrase['phrase']}*\n\n"
        f"{phrase['meaning']}\n\n"
        f"_{phrase['origin']}_"
    )
    await update.message.reply_text(message, parse_mode="Markdown")


async def painting_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global painting_index
    painting = PAINTINGS[painting_index % len(PAINTINGS)]
    painting_index += 1
    message = f"{painting['title']}\n\n{painting['description']}"
    await update.message.reply_text(message, parse_mode="Markdown")


def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quote", quote_now))
    app.add_handler(CommandHandler("phrase", phrase_now))
    app.add_handler(CommandHandler("painting", painting_now))

    tz = pytz.timezone(TIMEZONE)
    schedule = [
        (8, 10, send_quote, "quote_810"),
        (9, 45, send_phrase, "phrase_945"),
    ]

    for hour, minute, func, name in schedule:
        send_time = time(hour=hour, minute=minute, tzinfo=tz)
        app.job_queue.run_daily(func, time=send_time, name=name)
        print(f"Scheduled '{name}' at {hour}:{minute:02d} Moscow time")

    print(f"Bot started. Quotes: {len(QUOTES)}, Phrases: {len(PHRASES)}, Paintings: {len(PAINTINGS)}")
    app.run_polling()


if __name__ == "__main__":
    main()
