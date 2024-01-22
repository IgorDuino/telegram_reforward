import pytz
import asyncio

import telegram
from telegram.ext import (
    Defaults,
    Application,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.ext import filters
from telegram.constants import ParseMode

from reforward.settings import TELEGRAM_TOKEN

from tgbot.bot.handlers.start import start_handler
from tgbot.bot.handlers.rules import rules_handler, rule_handler
from tgbot.bot.handlers.filters import filters_handler, filter_handler
from tgbot.bot.handlers.general import toggle_handler, delete_handler
from tgbot.bot.handlers.folders import (
    add_folder_handler,
    add_folder_name_handler,
    add_folder_parent_handler,
)
from tgbot.bot.handlers.add_rule import (
    add_rule_handler,
    add_rule_handler_a_chat_id,
    add_rule_handler_b_chat_id,
    add_rule_handler_direction,
    add_rule_handler_folder_or_not,
    add_rule_handler_folder,
    add_rule_handler_who_notify,
    add_rule_handler_top_signature,
    add_rule_handler_bottom_signature,
    add_rule_handler_name,
)
from tgbot.bot.handlers.filters import (
    add_filter_handler,
    add_filter_name_handler,
    add_filter_trigger_handler,
    add_filter_action_handler,
    add_filter_replacement_handler,
    add_filter_confirm_handler,
)

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning


filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


def setup_application(app):
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(start_handler, pattern="start"))

    add_filter_conv_handler = ConversationHandler(
        per_user=True,
        entry_points=[CallbackQueryHandler(add_filter_handler, pattern="add_filter:")],
        states={
            "ADD_FILTER_NAME": [
                MessageHandler(filters.TEXT, add_filter_name_handler),
            ],
            "ADD_FILTER_TRIGGER": [
                MessageHandler(filters.TEXT, add_filter_trigger_handler),
                CallbackQueryHandler(add_filter_trigger_handler, pattern="add_filter_trigger:"),
            ],
            "ADD_FILTER_ACTION": [
                CallbackQueryHandler(add_filter_action_handler, pattern="add_filter_action:"),
            ],
            "ADD_FILTER_REPLACEMENT": [
                MessageHandler(filters.TEXT, add_filter_replacement_handler),
            ],
            "ADD_FILTER_CONFIRM": [
                CallbackQueryHandler(add_filter_confirm_handler, pattern="add_filter_confirm"),
            ],
        },
        fallbacks=[CallbackQueryHandler(start_handler, pattern="cancel")],
    )
    app.add_handler(add_filter_conv_handler)

    add_folder_conv_handler = ConversationHandler(
        per_user=True,
        entry_points=[CallbackQueryHandler(add_folder_handler, pattern="add_folder")],
        states={
            "ADD_FOLDER_NAME": [
                MessageHandler(filters.TEXT, add_folder_name_handler),
            ],
            "ADD_FOLDER_PARENT": [
                CallbackQueryHandler(add_folder_parent_handler, pattern="folder:"),
            ],
        },
        fallbacks=[CallbackQueryHandler(start_handler, pattern="cancel")],
    )
    app.add_handler(add_folder_conv_handler)

    add_rule_conv_handler = ConversationHandler(
        per_user=True,
        entry_points=[CallbackQueryHandler(add_rule_handler, pattern="add_rule")],
        states={
            "ADD_RULE_A_CHAT_ID": [
                MessageHandler(filters.TEXT, add_rule_handler_a_chat_id),
            ],
            "ADD_RULE_B_CHAT_ID": [
                MessageHandler(filters.TEXT, add_rule_handler_b_chat_id),
            ],
            "ADD_RULE_DIRECTION": [
                CallbackQueryHandler(add_rule_handler_direction, pattern="one_way|two_way"),
            ],
            "ADD_RULE_FOLDER_OR_NOT": [
                CallbackQueryHandler(add_rule_handler_folder_or_not, pattern="yes|no"),
            ],
            "ADD_RULE_FOLDER": [
                CallbackQueryHandler(add_rule_handler_folder, pattern="folder:"),
            ],
            "ADD_RULE_WHO_NOTIFY": [
                CallbackQueryHandler(add_rule_handler_who_notify, pattern="notify:"),
            ],
            "ADD_RULE_TOP_SIGNATURE": [
                MessageHandler(filters.TEXT, add_rule_handler_top_signature),
            ],
            "ADD_RULE_BOTTOM_SIGNATURE": [
                MessageHandler(filters.TEXT, add_rule_handler_bottom_signature),
            ],
            "ADD_RULE_NAME": [
                MessageHandler(filters.TEXT, add_rule_handler_name),
            ],
        },
        fallbacks=[CallbackQueryHandler(start_handler, pattern="cancel")],
    )
    app.add_handler(add_rule_conv_handler)

    app.add_handler(CallbackQueryHandler(rules_handler, pattern="rules"))
    app.add_handler(CallbackQueryHandler(rules_handler, pattern="folder:"))
    app.add_handler(CallbackQueryHandler(rule_handler, pattern="rule:"))

    app.add_handler(CallbackQueryHandler(filters_handler, pattern="filters:"))
    app.add_handler(CallbackQueryHandler(filter_handler, pattern="filter:"))

    app.add_handler(CallbackQueryHandler(toggle_handler, pattern="toggle:"))
    app.add_handler(CallbackQueryHandler(delete_handler, pattern="delete:"))


defaults = Defaults(parse_mode=ParseMode.MARKDOWN_V2, tzinfo=pytz.timezone("Europe/Moscow"))


application = Application.builder().token(TELEGRAM_TOKEN).defaults(defaults).build()
setup_application(application)
loop = asyncio.get_event_loop()
bot = application.bot


def run_polling():
    setup_application(application)
    print(f"Polling of bot started, PTB version: {telegram.__version__}")
    application.run_polling()


def main():
    return run_polling()
