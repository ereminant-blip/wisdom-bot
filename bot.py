import logging
from datetime import time
import random
import pytz
import sys
import os
import httpx

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8725776252:AAE1QI_Sl_UgsFvBZtnYa71PE6n5h8qyoh0"

CHAT_IDS = [
    586687616,
    "@rassvetpotemki",
]

QUOTE_TIMES = [
    (8, 10),
    (18, 30),
]
PAINTING_TIME = (13, 5)

TIMEZONE = "Europe/Moscow"

sys.path.insert(0, os.path.dirname(__file__))
from quotes import QUOTES
from paintings import PAINTINGS

random.shuffle(QUOTES)
random.shuffle(PAINTINGS)

quote_index = 0
painting_index = 0

HEADERS = {
    "User-Agent": "WisdomBot/1.0 (educational Telegram bot; contact via Telegram @rassvetpotemki)"
}


async def fetch_image_bytes(url: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=20) as client:
            r = await client.get(url)
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content
            else:
                print(f"Bad response {r.status_code} for {url}")
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
    return None


async def get_wikipedia_image_url(filename: str) -> str | None:
    """Get direct image URL via Wikipedia API"""
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
            r = await client.get(api_url, params=params)
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                imageinfo = page.get("imageinfo", [])
                if imageinfo:
                    return imageinfo[0].get("url")
    except Exception as e:
        print(f"Wikipedia API error: {e}")
    return None


async def send_to_all(bot, message, photo_bytes=None, photo_url=None):
    for chat_id in CHAT_IDS:
        try:
            if photo_bytes:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_bytes,
                    caption=message,
                    parse_mode="Markdown"
                )
            elif photo_url:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message + f"\n\n[Смотреть картину]({photo_url})",
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")


async def get_painting_image(painting: dict) -> bytes | None:
    url = painting.get("image", "")
    if not url:
        return None

    # Try direct fetch first
    img = await fetch_image_bytes(url)
    if img:
        return img

    # If failed, try to extract filename and use Wikipedia API
    if "wikipedia/commons" in url or "wikipedia/en" in url:
        # Extract filename from URL
        filename = url.split("/")[-1]
        if "px-" in filename:
            # thumbnail - get original name
            filename = filename.split("px-", 1)[1]
        api_url = await get_wikipedia_image_url(filename)
        if api_url:
            img = await fetch_image_bytes(api_url)
            if img:
                return img

    return None


async def send_daily_quote(context: ContextTypes.DEFAULT_TYPE):
    global quote_index
    quote = QUOTES[quote_index % len(QUOTES)]
    quote_index += 1
    message = f"{quote['title']}\n\n_{quote['text']}_\n\n{quote['reflection']}"
    await send_to_all(context.bot, message)


async def send_painting(context: ContextTypes.DEFAULT_TYPE):
    global painting_index
    painting = PAINTINGS[painting_index % len(PAINTINGS)]
    painting_index += 1
    caption = f"{painting['title']}\n\n{painting['description']}"
    if len(caption) > 1024:
        caption = caption[:1021] + "..."

    img = await get_painting_image(painting)
    await send_to_all(context.bot, caption, photo_bytes=img, photo_url=painting.get("image") if not img else None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Мудрость древних и великие картины\n\n"
        "Цитаты: каждый день в 8:10 и 18:30 по Москве\n"
        "Картины: каждый день в 13:05 по Москве\n\n"
        f"Цитат в коллекции: {len(QUOTES)}\n"
        f"Картин в коллекции: {len(PAINTINGS)}\n\n"
        "/quote - получить цитату сейчас\n"
        "/painting - получить картину сейчас"
    )


async def quote_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global quote_index
    quote = QUOTES[quote_index % len(QUOTES)]
    quote_index += 1
    message = f"{quote['title']}\n\n_{quote['text']}_\n\n{quote['reflection']}"
    await update.message.reply_text(message, parse_mode="Markdown")


async def painting_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global painting_index
    painting = PAINTINGS[painting_index % len(PAINTINGS)]
    painting_index += 1
    caption = f"{painting['title']}\n\n{painting['description']}"
    if len(caption) > 1024:
        caption = caption[:1021] + "..."

    await update.message.reply_text("Загружаю картину...")
    img = await get_painting_image(painting)

    try:
        if img:
            await update.message.reply_photo(photo=img, caption=caption, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                caption + f"\n\n[Смотреть картину]({painting['image']})",
                parse_mode="Markdown"
            )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quote", quote_now))
    app.add_handler(CommandHandler("painting", painting_now))

    tz = pytz.timezone(TIMEZONE)

    for hour, minute in QUOTE_TIMES:
        send_time = time(hour=hour, minute=minute, tzinfo=tz)
        app.job_queue.run_daily(
            send_daily_quote,
            time=send_time,
            name=f"quote_{hour}_{minute}"
        )
        print(f"Quotes scheduled at {hour}:{minute:02d} Moscow time")

    painting_send_time = time(hour=PAINTING_TIME[0], minute=PAINTING_TIME[1], tzinfo=tz)
    app.job_queue.run_daily(
        send_painting,
        time=painting_send_time,
        name="painting"
    )
    print(f"Paintings scheduled at {PAINTING_TIME[0]}:{PAINTING_TIME[1]:02d} Moscow time")

    print(f"Bot started. Quotes: {len(QUOTES)}, Paintings: {len(PAINTINGS)}")
    app.run_polling()


if __name__ == "__main__":
    main()
