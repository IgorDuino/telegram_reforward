from django.apps import AppConfig
from reforward.settings import WEBHOOK_URL
import asyncio
import logging

logger = logging.getLogger(__name__)

logger.info("Loading tgbot/apps.py")
async def check_and_set_webhook():
    from tgbot.bot.bot import bot

    webhook = await bot.get_webhook_info()

    if webhook.url != WEBHOOK_URL:
        logger.info("Setting webhook")
        await bot.set_webhook(WEBHOOK_URL)
    else:
        logger.info("Webhook already set")


class TgbotConfig(AppConfig):
    name = "tgbot"

    def ready(self):
        from tgbot.bot.bot import bot

        asyncio.get_event_loop().run_until_complete(check_and_set_webhook())
