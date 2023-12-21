import asyncio

import telegram

from reforward.celery import app
from tgbot.bot.bot import application, bot


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_telegram_event_async(update_json))


async def process_telegram_event_async(update_json):
    update = telegram.Update.de_json(update_json, bot)
    if not application._initialized:
        await application.initialize()
    await application.process_update(update)
