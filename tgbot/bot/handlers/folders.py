import logging

from telegram.ext import CallbackContext
from telegram import Update

from tgbot.bot import message_texts as m
from tgbot.models import User, Folder

from tgbot.bot.keyboards.general import cancel_keyboard
from tgbot.bot.keyboards.folders import chose_folder_keyboard

from tgbot.bot.handlers.start import start_handler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def add_folder_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    await update.callback_query.edit_message_text(
        text=m.ADD_FOLDER_NAME,
        reply_markup=cancel_keyboard(),
    )

    return "ADD_FOLDER_NAME"


async def add_folder_name_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    context.user_data["folder_name"] = update.message.text

    await update.message.reply_text(
        text=m.ADD_FOLDER_PARENT,
        reply_markup=chose_folder_keyboard([folder async for folder in Folder.objects.all()]),
    )

    return "ADD_FOLDER_PARENT"


async def add_folder_parent_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    if "nofolder" in update.callback_query.data:
        context.user_data["folder_parent"] = None
    else:
        context.user_data["folder_parent"] = await Folder.objects.aget(
            id=int(update.callback_query.data.split(":")[1])
        )

    await Folder.objects.create(
        name=context.user_data["folder_name"],
        parent=context.user_data["folder_parent"],
    )

    await update.callback_query.edit_message_text(
        text=m.FOLDER_CREATED,
    )

    return await start_handler(update, context)
