import asyncio
import logging

import telegram
from telegram.ext import ContextTypes

from tgbot.bot import message_texts as m
from tgbot.models import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def start_handler(update, context: ContextTypes.DEFAULT_TYPE):
    u, created = await User.get_user_and_created(update, context)

    if created:
        await update.message.reply_text(m.START_FIRST_TIME)
        return

    await update.message.reply_text(m.START_NOT_FIRST_TIME)
