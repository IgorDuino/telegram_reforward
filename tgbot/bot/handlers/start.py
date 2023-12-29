import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update

from tgbot.bot import message_texts as m
from tgbot.models import User

from tgbot.bot.keyboards.start import start_keyboard


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def start_handler(update: Update, context: CallbackContext):
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
