import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update
from telegram import ReplyKeyboardRemove

from tgbot.bot import message_texts as m
from tgbot.models import User, Rule, Filter, FilterTriggerTemplate, FilterActionEnum

from tgbot.bot.handlers.start import start_handler
from tgbot.bot.keyboards.filters import (
    filters_keyboard,
    filter_keyboard,
    add_filter_action_keyboard,
    add_filter_trigger_keyboard,
    add_filter_replace_keyboard,
    add_filter_confirm_keyboard,
)
from tgbot.bot.keyboards.general import cancel_keyboard


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

    filter_ = await Filter.objects.aget(
        id=int(update.callback_query.data.split(":")[1])
    )

    await update.callback_query.edit_message_text(
        text=m.FILTER.format(
            filter_name=filter_.name if filter_.name else filter_.id,
            trigger=filter_.regex,
            action=filter_.action_str,
            replacement=filter_.replacement,
        ),
        reply_markup=filter_keyboard(filter_),
    )

    return ConversationHandler.END


async def add_filter_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    rule_id = update.callback_query.data.split(":")[1]
    rule_id = int(rule_id) if rule_id != "general" else None

    rule = None if rule_id is None else await Rule.objects.aget(id=rule_id)
    context.user_data["filter_rule"] = rule

    await update.callback_query.edit_message_text(
        text=m.ADD_FILTER_NAME,
        reply_markup=cancel_keyboard(),
    )

    return "ADD_FILTER_NAME"


async def add_filter_name_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    context.user_data["filter_name"] = update.message.text

    templates = [t async for t in FilterTriggerTemplate.objects.all()]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=m.ADD_FILTER_TRIGGER,
        reply_markup=add_filter_trigger_keyboard(templates),
    )

    return "ADD_FILTER_TRIGGER"


async def add_filter_trigger_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    if update.callback_query:
        trigger = await FilterTriggerTemplate.objects.aget(
            id=int(update.callback_query.data.split(":")[1])
        )

        context.user_data["filter_trigger"] = trigger.trigger

        await update.callback_query.edit_message_text(
            text=m.ADD_FILTER_ACTION,
            reply_markup=add_filter_action_keyboard(),
        )

        return "ADD_FILTER_ACTION"

    context.user_data["filter_trigger"] = update.message.text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=m.ADD_FILTER_ACTION,
        reply_markup=add_filter_action_keyboard(),
    )

    return "ADD_FILTER_ACTION"


async def add_filter_action_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    action = update.callback_query.data.split(":")[1]
    action = FilterActionEnum(action)
    context.user_data["filter_action"] = action

    if action == FilterActionEnum.REPLACE:
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=m.ADD_FILTER_REPLACEMENT,
            reply_markup=add_filter_replace_keyboard(),
        )

        return "ADD_FILTER_REPLACEMENT"

    context.user_data["filter_replacement"] = ""

    await update.callback_query.edit_message_text(
        text=m.ADD_FILTER_CONFIRM.format(
            name=context.user_data["filter_name"],
            trigger=context.user_data["filter_trigger"],
            action=action.label,
            replacement=context.user_data["filter_replacement"],
        ),
        reply_markup=add_filter_confirm_keyboard(),
    )

    return "ADD_FILTER_CONFIRM"


async def add_filter_replacement_handler(update: Update, context: CallbackContext):
    u = await User.get_user(update, context)

    if update.callback_query:
        context.user_data["filter_replacement"] = ""
    else:
        context.user_data["filter_replacement"] = update.message.text

    text = m.ADD_FILTER_CONFIRM.format(
        name=context.user_data["filter_name"],
        trigger=context.user_data["filter_trigger"],
        action=FilterActionEnum(context.user_data["filter_action"]).label,
        replacement=context.user_data["filter_replacement"],
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=add_filter_confirm_keyboard(),
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=add_filter_confirm_keyboard(),
        )

    return "ADD_FILTER_CONFIRM"


async def add_filter_confirm_handler(update: Update, context: CallbackContext):
    rule = context.user_data["filter_rule"]
    name = context.user_data["filter_name"]
    regex = context.user_data["filter_trigger"]
    action = context.user_data["filter_action"]
    replacement = context.user_data["filter_replacement"]

    try:
        await Filter.objects.acreate(
            rule=rule,
            name=name,
            regex=regex,
            action=action,
            replacement=replacement,
        )
    except Exception as e:
        logger.error(e)
        await update.callback_query.edit_message_text(
            text=m.ADD_FILTER_ERROR,
        )
        return await start_handler(update, context)

    await update.callback_query.edit_message_text(
        text=m.FILTER_CREATED,
    )

    return await start_handler(update, context)
