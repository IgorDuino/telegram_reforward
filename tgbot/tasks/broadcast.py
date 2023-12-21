import time
import random
import asyncio
import telegram
from telegram.error import BadRequest
from celery.utils.log import get_task_logger

from django.utils.timezone import now

from reforward.celery import app
from reforward.settings import TELEGRAM_TOKEN

from tgbot.models import User


logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def broadcast_message(user_ids, message):
    """Broadcast text to all users"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(broadcast_message_async(user_ids, message))


async def broadcast_message_async(user_ids, message):
    logger.info(f"Going to send message: '{message}' to {len(user_ids)} users")

    for user_id in user_ids:
        # TODO: optimize this
        try:
            u = await User.objects.aget(user_id=user_id)
            await u.send_message(message=message, parse_mode=telegram.constants.ParseMode.MARKDOWN)
            logger.info(f"Broadcast message was sent to {u}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        await asyncio.sleep(0.2)

    logger.info("Broadcast finished!")


@app.task(ignore_result=True)
def broadcast_photo(user_ids, message, file_id, button_text, button_url):
    """Broadcasts photo to user_ids with message"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        broadcast_photo_async(user_ids, message, file_id, button_text, button_url)
    )


async def broadcast_photo_async(user_ids, message, file_id, button_text=None, button_url=None):
    logger.info(f"Going to send photo with caption: '{message}' to {len(user_ids)} users")

    bot = telegram.Bot(TELEGRAM_TOKEN)
    keyboard = None
    if button_url and button_text:
        keyboard = telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton(text=button_text, url=button_url)]]
        )
    # TODO: make this a batch job + set up anti-throttling
    for user_id in user_ids:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=file_id,
                caption=message,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
            logger.info(f"Broadcast photo was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        await asyncio.sleep(0.2)

    logger.info("Broadcast finished!")
