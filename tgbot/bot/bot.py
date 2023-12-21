import asyncio

import telegram
from telegram.ext import MessageHandler, filters, Application, CommandHandler

from reforward.settings import TELEGRAM_TOKEN
from tgbot.bot.handle_start import start_handler


def setup_application(app):
    app.add_handler(CommandHandler("start", start_handler))


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
