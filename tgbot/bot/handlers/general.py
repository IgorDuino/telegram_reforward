import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update

from tgbot.bot import message_texts as m
from tgbot.models import User, Rule, Folder, Filter

from tgbot.bot.keyboards.start import start_keyboard


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def delete_notification(update: Update, context: CallbackContext):
    try:
        await update.callback_query.message.delete()
    except Exception as e:
        logger.exception(e)


async def toggle_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    a = update.callback_query.data.split(":")[1]

    if a == "rule":
        id = int(update.callback_query.data.split(":")[3])
        rule = await Rule.objects.aget(id=id)
        if bool(int(update.callback_query.data.split(":")[2])):
            await rule.enable()
        else:
            await rule.disable()

    elif a == "folder":
        id = int(update.callback_query.data.split(":")[3])

        folder = await Folder.objects.aget(id=id)
        folder.is_active = bool(int(update.callback_query.data.split(":")[2]))
        await folder.asave()

    elif a == "forwarding":
        u.is_forwarding_enabled = bool(int(update.callback_query.data.split(":")[2]))
        await u.asave()

    elif a == "filter":
        id = int(update.callback_query.data.split(":")[3])

        filter = await Filter.objects.aget(id=id)
        filter.is_active = bool(int(update.callback_query.data.split(":")[2]))
        await filter.asave()

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

    elif update.callback_query.data.split(":")[1] == "filter":
        filter = await Filter.objects.aget(id=id)
        await filter.adelete()

    await update.callback_query.edit_message_text(
        text=m.DELETED,
        reply_markup=start_keyboard(u.is_forwarding_enabled),
    )

    return ConversationHandler.END
