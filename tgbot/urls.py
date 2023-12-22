from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    path("telegram-bot-webhook/", csrf_exempt(views.TelegramBotWebhookView.as_view())),
]
