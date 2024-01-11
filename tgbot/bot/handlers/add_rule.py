import logging

from telegram.ext import CallbackContext
from telegram import Update, ReplyKeyboardRemove

from tgbot.bot import message_texts as m
from tgbot.models import Rule, Folder

from tgbot.bot.keyboards.general import cancel_keyboard
from tgbot.bot.keyboards.rules import (
    choose_rule_direction_keyboard,
    yes_no_keyboard,
    who_notify_keyboard,
    skip_keyboard,
)
from tgbot.bot.keyboards.folders import chose_folder_keyboard

from tgbot.bot.handlers.start import start_handler


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def add_rule_handler(update: Update, context: CallbackContext):
    await update.callback_query.edit_message_text(
        text="Отправьте первый chat id",
        reply_markup=cancel_keyboard(),
    )

    return "ADD_RULE_A_CHAT_ID"


async def add_rule_handler_a_chat_id(update: Update, context: CallbackContext):
    if update.message.forward_from:
        context.user_data["a_chat_id"] = update.message.forward_from.id
    else:
        context.user_data["a_chat_id"] = update.message.text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправьте второй chat id",
        reply_markup=cancel_keyboard(),
    )

    return "ADD_RULE_B_CHAT_ID"


async def add_rule_handler_b_chat_id(update: Update, context: CallbackContext):
    if update.message.forward_from:
        context.user_data["b_chat_id"] = update.message.forward_from.id
    else:
        context.user_data["b_chat_id"] = update.message.text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите направление пересылки",
        reply_markup=choose_rule_direction_keyboard(),
    )

    return "ADD_RULE_DIRECTION"


async def add_rule_handler_direction(update: Update, context: CallbackContext):
    direction = update.callback_query.data

    if direction == "one_way":
        context.user_data["direction"] = "O"
    elif direction == "two_way":
        context.user_data["direction"] = "X"

    await update.callback_query.edit_message_text(
        text="Добавить правило в папку?",
        reply_markup=yes_no_keyboard(),
    )

    return "ADD_RULE_FOLDER_OR_NOT"


async def add_rule_handler_folder_or_not(update: Update, context: CallbackContext):
    folder_or_not = update.callback_query.data

    if folder_or_not == "yes":
        folders = []
        async for folder in Folder.objects.all():
            folders.append(folder)

        await update.callback_query.edit_message_text(
            text="Выберите папку",
            reply_markup=chose_folder_keyboard(folders),
        )

        return "ADD_RULE_FOLDER"

    context.user_data["folder_id"] = None

    await update.callback_query.edit_message_text(
        text="Кого нужно оповещать когда пересылка включается или выключается?",
        reply_markup=who_notify_keyboard(),
    )

    return "ADD_RULE_WHO_NOTIFY"


async def add_rule_handler_folder(update: Update, context: CallbackContext):
    folder_id = update.callback_query.data.split(":")[1]
    folder_id = None if folder_id == "nofolder" else int(folder_id)
    context.user_data["folder_id"] = folder_id

    await update.callback_query.edit_message_text(
        text="Кого нужно оповещать когда пересылка включается или выключается?",
        reply_markup=who_notify_keyboard(),
    )

    return "ADD_RULE_WHO_NOTIFY"


async def add_rule_handler_who_notify(update: Update, context: CallbackContext):
    who_notify = update.callback_query.data.split(":")[1]

    context.user_data["who_notify"] = who_notify

    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправьте подпись сверху или нажмите ПРОПУСТИТЬ",
        reply_markup=skip_keyboard(),
    )

    return "ADD_RULE_TOP_SIGNATURE"


async def add_rule_handler_top_signature(update: Update, context: CallbackContext):
    top_signature = update.message.text

    context.user_data["top_signature"] = top_signature if top_signature != "ПРОПУСТИТЬ" else ""

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправьте подпись снизу или нажмите ПРОПУСТИТЬ",
        reply_markup=skip_keyboard(),
    )

    return "ADD_RULE_BOTTOM_SIGNATURE"


async def add_rule_handler_bottom_signature(update: Update, context: CallbackContext):
    bottom_signature = update.message.text

    context.user_data["bottom_signature"] = (
        bottom_signature if bottom_signature != "ПРОПУСТИТЬ" else ""
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправьте название правила",
        reply_markup=ReplyKeyboardRemove(),
    )

    return "ADD_RULE_NAME"


async def add_rule_handler_name(update: Update, context: CallbackContext):
    name = update.message.text

    context.user_data["name"] = name

    folder = None
    if context.user_data["folder_id"]:
        folder = await Folder.objects.aget(id=context.user_data["folder_id"])

    notify_a, notify_b = False, False
    if context.user_data["who_notify"] == "a":
        notify_a = True
    elif context.user_data["who_notify"] == "b":
        notify_b = True
    elif context.user_data["who_notify"] == "both":
        notify_a = True
        notify_b = True

    rule = Rule(
        a_chat_id=int(context.user_data["a_chat_id"]),
        b_chat_id=int(context.user_data["b_chat_id"]),
        direction=context.user_data["direction"],
        folder=folder,
        notify_a=notify_a,
        notify_b=notify_b,
        top_signature=context.user_data["top_signature"],
        bottom_signature=context.user_data["bottom_signature"],
        name=context.user_data["name"],
    )

    await rule.asave()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Правило {rule.name} успешно добавлено",
    )

    return await start_handler(update, context)
