from django.apps import AppConfig
from reforward.settings import WEBHOOK_URL
import asyncio
import logging
import sys

logger = logging.getLogger("bot")

logger.info("Loading tgbot/apps.py")


async def check_and_set_webhook():
    from tgbot.bot.bot import bot

    webhook = await bot.get_webhook_info()
    while webhook.url != WEBHOOK_URL:
        print(webhook)
        print("Setting webhook")
        print(await bot.set_webhook(WEBHOOK_URL))
        webhook = await bot.get_webhook_info()
        await asyncio.sleep(4)
    else:
        print("Webhook already set")


class TgbotConfig(AppConfig):
    name = "tgbot"

    def ready(self):
        if "reforward.asgi:application" in sys.argv:
            from tgbot.bot.bot import bot

            asyncio.get_event_loop().run_until_complete(check_and_set_webhook())

            from tgbot.models import FilterTriggerTemplate
            from django.core.management import call_command

            if not FilterTriggerTemplate.objects.exists():
                call_command("loaddata", "initial_filter_trigger_templates.json")
