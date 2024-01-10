import logging

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update

from tgbot.bot import message_texts as m
from tgbot.models import User, Rule, Folder

from tgbot.bot.keyboards.start import start_keyboard
from tgbot.bot.keyboards.rules import (
    rules_keyboard,
    rule_keyboard,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
