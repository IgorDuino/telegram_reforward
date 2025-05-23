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


async def rules_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    folder = None
    if (
        "folder" in update.callback_query.data
        and "nofolder" not in update.callback_query.data
    ):
        folder = await Folder.objects.aget(id=update.callback_query.data.split(":")[1])
        rules = [
            rule
            async for rule in Rule.objects.filter(folder=folder)
            .order_by("created_at")
            .all()
        ]
        folders = [
            folder
            async for folder in Folder.objects.filter(parent=folder)
            .order_by("created_at")
            .all()
        ]
    else:
        rules = [
            rule
            async for rule in Rule.objects.filter(folder=None)
            .order_by("created_at")
            .all()
        ]
        folders = [
            folder
            async for folder in Folder.objects.filter(parent=None)
            .order_by("created_at")
            .all()
        ]

    if len(rules) + len(folders) == 0:
        await update.callback_query.edit_message_text(
            text=m.RULES_EMPTY,
            reply_markup=start_keyboard(u.is_forwarding_enabled),
        )

        return ConversationHandler.END

    keyboard = rules_keyboard(folders, rules, folder=folder)

    await update.callback_query.edit_message_text(
        text=m.RULES,
        reply_markup=keyboard,
    )

    return ConversationHandler.END


async def rule_handler(update: Update, context: CallbackContext):
    rule = await Rule.objects.aget(id=update.callback_query.data.split(":")[1])

    await update.callback_query.edit_message_text(
        text=m.RULE.format(
            name=rule.name,
            a_chat_id=rule.a_chat_id,
            b_chat_id=rule.b_chat_id,
            notify_myself="Yes" if rule.notify_myself else "No",
            notify_a="Yes" if rule.notify_a else "No",
            notify_b="Yes" if rule.notify_b else "No",
            direction="One way" if rule.direction == "O" else "Two way",
            top_signature=rule.top_signature,
            bottom_signature=rule.bottom_signature,
            signature_direction=rule.signature_direction,
        ),
        reply_markup=rule_keyboard(rule),
    )

    return ConversationHandler.END
