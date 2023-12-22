import json

from django.http import JsonResponse
from django.views import View

from tgbot.bot.tasks import process_telegram_event


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        update_json = json.loads(request.body)
        process_telegram_event.delay(update_json)

        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"ok": "Get request processed. But nothing done"})
