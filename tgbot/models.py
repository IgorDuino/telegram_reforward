import logging
from typing import Optional

import re

import telegram

from django.db import models

from tgbot.bot import utils
from reforward.settings import TELEGRAM_TOKEN
from pyrogram import Client


logger = logging.getLogger(__name__)


class User(models.Model):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=8, null=True, blank=True)  # Telegram client's lang

    deep_link = models.CharField(max_length=64, null=True, blank=True)

    is_forwarding_enabled = models.BooleanField(default=True)

    is_blocked_bot = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    gender = models.CharField(
        max_length=1,
        choices=[("M", "Male"), ("F", "Female"), ("N", "Don't know")],
        blank=True,
        null=True,
    )

    latest_meme_sent_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"@{self.username} (id: {self.user_id})" if self.username else f"{self.user_id}"

    @classmethod
    async def get_user_and_created(cls, update, context):
        data = await utils.extract_user_data_from_update(update)
        u, created = await cls.objects.aupdate_or_create(user_id=data["user_id"], defaults=data)

        if (
            created
            and context is not None
            and context.args
            and str(context.args[0]).strip() != str(u.user_id).strip()
        ):
            u.deep_link = context.args[0]
            await u.asave()

        return u, created

    @classmethod
    async def get_user(cls, update, context):
        """python-telegram-bot's Update, Context --> User instance"""
        return (await cls.get_user_and_created(update, context))[0]

    @classmethod
    async def get_user_by_username_or_user_id(cls, string):
        """Search user in DB, return User or None if not found"""
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return await cls.objects.aget(user_id=int(username))
        return await cls.objects.aget(username__iexact=username)

    async def send_message(
        self,
        message,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        reply_markup=None,
        reply_to_message_id=None,
        disable_web_page_preview=None,
    ) -> Optional[telegram.Message]:
        bot = telegram.Bot(TELEGRAM_TOKEN)
        try:
            msg = await bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
                disable_web_page_preview=disable_web_page_preview,
            )
        except telegram.error.Forbidden:
            self.is_blocked_bot = True
            success = False
        except Exception as e:
            success = False
        else:
            success = True
            self.is_blocked_bot = False
        finally:
            await self.asave()
        return msg if success else None

    async def send_photo(self, *args, **kwargs) -> Optional[telegram.Message]:
        bot = telegram.Bot(TELEGRAM_TOKEN)
        try:
            msg = await bot.send_photo(
                chat_id=self.user_id,
                *args,
                **kwargs,
            )
        except telegram.error.Forbidden:
            self.is_blocked_bot = True
            success = False
        except Exception as e:
            success = False
        else:
            success = True
            self.is_blocked_bot = False
        finally:
            await self.asave()
        return msg if success else None

    @property
    def tg_str(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"


class Folder(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, null=True, blank=True)

    a_chat_id = models.BigIntegerField()
    b_chat_id = models.BigIntegerField()
    direction = models.CharField(
        max_length=1, choices=[("O", "One-way"), ("X", "Two-way")], default=("O", "One-way")
    )

    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    notify_a = models.BooleanField(default=False)
    notify_b = models.BooleanField(default=False)

    top_signature = models.CharField(max_length=1000, null=True, blank=True)
    bottom_signature = models.CharField(max_length=1000, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        if self.direction == "O":
            return f"{self.a_chat_id} -> {self.b_chat_id}"
        return f"{self.a_chat_id} <-> {self.b_chat_id}"

    async def change_active(self, is_active):
        if self.is_active == is_active:
            return
        self.is_active = is_active
        await self.asave()
        chat_ids = []
        if self.notify_a and self.a_chat_id:
            chat_ids = [self.a_chat_id, self.b_chat_id]
        elif self.notify_a:
            chat_ids = [self.a_chat_id]
        elif self.notify_b:
            chat_ids = [self.b_chat_id]

        # if chat_ids != []:
        #     async with Client(
        #         "", 0, "", session_string=TELEGRAM_USERBOT_SESSION_STRING, in_memory=True
        #     ) as client:
        #         for chat_id in chat_ids:
        #             try:
        #                 text = (
        #                     f"[REFORWARD] Пересылка {'отключена' if not is_active else 'включена'}"
        #                 )
        #                 await client.send_message(
        #                     chat_id=chat_id,
        #                     text=text,
        #                 )
        #             except Exception as e:
            
    async def enable(self):
        await self.change_active(True)

    async def disable(self):
        await self.change_active(False)


class FilterActionEnum(models.TextChoices):
    REPLACE = "R", "Replace"
    SKIP = "S", "Skip forwarding"
    DISABLE_RULE = "D", "Disable rule"


class Filter(models.Model):
    id = models.AutoField(primary_key=True)
    is_general = models.BooleanField(default=False)  # works for all rules
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, null=True, blank=True)
    regex = models.CharField(max_length=512)
    action = models.CharField(
        max_length=1,
        choices=FilterActionEnum.choices,
        default=FilterActionEnum.REPLACE,
    )
    replacement = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_match(self, text, ignore_case=True):
        flags = re.IGNORECASE if ignore_case else 0
        return bool(re.search(self.regex, text, flags=flags))

    def is_match_on_message(self, message, ignore_case=True):
        r = False
        if message.text:
            r = self.is_match(message.text, ignore_case)
        if message.caption:
            r = self.is_match(message.caption, ignore_case) or r
        return r

    def apply(self, text):
        return re.sub(self.regex, self.replacement, text)

    def apply_on_message(self, message):
        if message.text:
            message.text = self.apply(message.text)
        if message.caption:
            message.caption = self.apply(message.caption)
        return message


class Forwarding(models.Model):
    id = models.AutoField(primary_key=True)
    original_message_id = models.BigIntegerField()
    new_message_id = models.BigIntegerField()
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
