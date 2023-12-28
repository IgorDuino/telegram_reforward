import ipaddress
import json

from django.http import JsonResponse
from django.views import View

from reforward import settings

from tgbot.bot.tasks import process_telegram_event


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        ip = ipaddress.ip_address(request.META.get("REMOTE_ADDR"))
        if (
            not settings.DEBUG
            and ip not in ipaddress.ip_network("149.154.160.0/20")
            and ip not in ipaddress.ip_network("91.108.4.0/22")
        ):
            return JsonResponse({"error": "Wrong IP"}, status=403)

        update_json = json.loads(request.body)

        process_telegram_event.delay(update_json)

        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"ok": "Get request processed. But nothing done"})
