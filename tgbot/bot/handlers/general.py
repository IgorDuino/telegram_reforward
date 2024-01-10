import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update

from tgbot.bot import message_texts as m
from tgbot.models import User, Rule, Folder

from tgbot.bot.keyboards.start import start_keyboard
from tgbot.bot.keyboards.rules import (
    rules_keyboard,
    rule_keyboard,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def toggle_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    a = update.callback_query.data.split(":")[1]

    if a == "rule":
        id = int(update.callback_query.data.split(":")[3])
        rule = await Rule.objects.aget(id=id)
        rule.is_active = bool(int(update.callback_query.data.split(":")[2]))
        await rule.asave()

    elif a == "folder":
        id = int(update.callback_query.data.split(":")[3])

        folder = await Folder.objects.aget(id=id)
        folder.is_active = bool(int(update.callback_query.data.split(":")[2]))
        await folder.asave()

    elif a == "forwarding":
        u.is_forwarding_enabled = bool(int(update.callback_query.data.split(":")[2]))
        await u.asave()

    await update.callback_query.edit_message_text(
        text=m.DONE,
        reply_markup=start_keyboard(u.is_forwarding_enabled),
    )

    return ConversationHandler.END


async def delete_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    id = int(update.callback_query.data.split(":")[2])

    if update.callback_query.data.split(":")[1] == "rule":
        rule = await Rule.objects.aget(id=id)
        await rule.adelete()

    elif update.callback_query.data.split(":")[1] == "folder":
        folder = await Folder.objects.aget(id=id)
        await folder.adelete()

    await update.callback_query.edit_message_text(
        text=m.DELETED,
        reply_markup=start_keyboard(u.is_forwarding_enabled),
    )

    return ConversationHandler.END
