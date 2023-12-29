import asyncio

import telegram
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.ext import filters

from reforward.settings import TELEGRAM_TOKEN

from tgbot.bot.handlers.start import start_handler
from tgbot.bot.handlers.rules import (
    rules_handler,
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

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning


filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


def setup_application(app):
    app.add_handler(CommandHandler("start", start_handler))

    app.add_handler(CallbackQueryHandler(rules_handler, pattern="rules"))

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


def run_polling():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    setup_application(app)
    print(f"Polling of bot started, PTB version: {telegram.__version__}")
    app.run_polling()


def main():
    return run_polling()


application = (
    Application.builder()
    .token(TELEGRAM_TOKEN)
    .read_timeout(30)
    .write_timeout(30)
    .pool_timeout(30)
    .connect_timeout(30)
    .build()
)
setup_application(application)
loop = asyncio.get_event_loop()
bot = application.bot
