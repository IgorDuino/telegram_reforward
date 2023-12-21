import logging
from typing import Optional

import telegram

from django.db import models

from tgbot.bot import utils


logger = logging.getLogger(__name__)


class User(models.Model):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=8, null=True, blank=True)  # Telegram client's lang

    deep_link = models.CharField(max_length=64, null=True, blank=True)

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
        """python-telegram-bot's Update, Context --> User instance"""
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
        except Forbidden:
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
        except Forbidden:
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
