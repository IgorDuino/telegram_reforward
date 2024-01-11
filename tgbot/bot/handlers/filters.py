import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update

from tgbot.bot import message_texts as m
from tgbot.models import User, Rule, Folder, Filter

from tgbot.bot.keyboards.filters import filters_keyboard, filter_keyboard


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def filters_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    rule_id = update.callback_query.data.split(":")[1]
    rule_id = int(rule_id) if rule_id != "general" else None

    rule = None if rule_id is None else await Rule.objects.aget(id=rule_id)

    filters = [f async for f in Filter.objects.filter(rule=rule).all()]
    text = m.RULE_FILTERS.format(rule=rule) if rule_id else m.GENERAL_FILTERS
    await update.callback_query.edit_message_text(
        text=text if len(filters) > 0 else m.FILTERS_EMPTY,
        reply_markup=filters_keyboard(filters, rule=rule),
    )

    return ConversationHandler.END


async def filter_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    filter_ = Filter.objects.get(id=int(update.callback_query.data.split(":")[1]))

    await update.callback_query.edit_message_text(
        text=m.FILTER.format(
            filter_name=filter_.name if filter_.name else filter_.id,
            trigger=filter_.regex,
            action=filter_.action,
            replacement=filter_.replacement,
        ),
        reply_markup=filter_keyboard(filter_),
    )

    return ConversationHandler.END
