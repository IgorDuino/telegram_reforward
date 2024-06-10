import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update

from reforward import settings

from tgbot.bot import message_texts as m
from tgbot.models import User

from tgbot.bot.keyboards.start import start_keyboard


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def start_handler(update: Update, context: CallbackContext):
    if update.effective_user.id not in (settings.TELEGRAM_ID, settings.TELEGRAM_ADMIN_ID):
        await update.message.reply_text(m.NOT_AUTHORIZED)
        return ConversationHandler.END

    u, _ = await User.get_user_and_created(update, context)

    context.user_data.clear()

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=m.START,
            reply_markup=start_keyboard(enabled=u.is_forwarding_enabled),
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=m.START,
        reply_markup=start_keyboard(enabled=u.is_forwarding_enabled),
    )

    return ConversationHandler.END


async def compose_restart(update: Update, context: CallbackContext):
    await update.callback_query.edit_message_text(
        text=m.RESTART,
    )

    import os
    os.system("cd /reforward && docker compose restart")

    return ConversationHandler.END