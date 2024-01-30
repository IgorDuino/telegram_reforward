from dotenv import load_dotenv

load_dotenv()

import django

django.setup()


from reforward import settings
from django.db.models import Q

import pyrogram.errors
from pyrogram import Client, filters, idle
from pyrogram.types import Message, Reaction
from pyrogram.enums import ParseMode
import logging
from tgbot.models import User, Filter, FilterActionEnum, Rule, Forwarding
from pyrogram_utils import copy

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from asgiref.sync import sync_to_async

from typing import List

import datetime


bot = telegram.Bot(settings.TELEGRAM_TOKEN)


def notification_keyboard(rule) -> InlineKeyboardMarkup:
    buttons = [
        [
            telegram.InlineKeyboardButton(
                "Удалить сообщение",
                callback_data="delete_notification",
            )
        ],
        [
            telegram.InlineKeyboardButton(
                "Включить пересылку", callback_data=f"toggle:rule:1:{rule.id}"
            )
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def signature_formatter(signature: str, message: Message) -> str:
    if signature:
        signature = signature.replace(
            "{first_name}", message.from_user.first_name or ""
        )
        signature = signature.replace("{last_name}", message.from_user.last_name or "")
        signature = signature.replace("{username}", message.from_user.username or "")
        signature = signature.replace("{title}", message.chat.title or "")
        signature = signature.replace("{chat_id}", str(message.chat.id))
        signature = signature.replace("{user_id}", str(message.from_user.id))

        return signature
    else:
        return ""


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Client(
    "userbot",
    workdir="sessions",
    phone_number=settings.PHONE_NUMBER,
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
)

app.start()

my_id = app.get_me().id

print(f"Userbot started, my ID: {my_id}")


@app.on_deleted_messages()
def deleted_messages_handler(client: Client, messages: list[Message]):
    if not User.objects.get(user_id=settings.TELEGRAM_ID).is_forwarding_enabled:
        return

    for message in messages:
        for forwarding in Forwarding.objects.filter(
            original_message_id=message.id
        ).all():
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.a_chat_id,
                    message_ids=forwarding.new_message_id,
                )
            except Exception as e:
                pass
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.b_chat_id,
                    message_ids=forwarding.new_message_id,
                )
            except Exception as e:
                pass

            forwarding.delete()

        for forwarding in Forwarding.objects.filter(new_message_id=message.id).all():
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.a_chat_id,
                    message_ids=forwarding.original_message_id,
                )
            except Exception as e:
                pass
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.b_chat_id,
                    message_ids=forwarding.original_message_id,
                )
            except Exception as e:
                pass

            forwarding.delete()


@app.on_message(
    filters=filters.command(
        ["on_reforward", "onrf", "off_reforward", "offrf", "check_reforward", "crf"]
    )
)
async def toggle_forwarding_handler(client: Client, message: Message):
    a = message.text.strip().split()
    if len(a) == 2:
        rule_id = a[1]
        rules = Rule.objects.filter(id=rule_id).all()
    else:
        rules = Rule.objects.filter(
            Q(a_chat_id=message.chat.id) | Q(b_chat_id=message.chat.id)
        ).all()

    allowed_rules: List = []

    async for rule in rules:
        if (
            rule.a_chat_id == message.chat.id and rule.allow_a_chat_members_control
        ) or (rule.b_chat_id == message.chat.id and rule.allow_b_chat_members_control):
            allowed_rules.append(rule)

    if len(allowed_rules) == 1:
        rule = allowed_rules[0]
        if message.text in ["/on_reforward", "/onrf"]:
            if rule.is_active:
                await message.reply_text(
                    "#reforwarder\n**__[Пересылка и так включена]__**"
                )
            else:
                await message.reply_text(
                    "#reforwarder\n**__[Пересылка успешно включена]__**"
                )
                rule.is_active = True
                await rule.asave()

        elif message.text in ["/off_reforward", "/offrf"]:
            if not rule.is_active:
                await message.reply_text(
                    "#reforwarder\n**__[Пересылка и так отключена]__**"
                )
            else:
                await message.reply_text(
                    "#reforwarder\n**__[Пересылка успешно отключена]__**"
                )
                rule.is_active = False
                await rule.asave()

        elif message.text in ["/check_reforward", "/crf"]:
            if rule.is_active:
                await message.reply_text("#reforwarder\n**__[Пересылка включена]__**")
            else:
                await message.reply_text("#reforwarder\n**__[Пересылка отключена]__**")

    elif len(allowed_rules) > 1:
        ids = "\n".join([f"[{rule.id}] - {rule}" for rule in allowed_rules])
        await message.reply_text(
            f"#reforwarder\n**__[Существует несколько правил, подключённых к данному чату, "
            f"которыми вы можете управлять. Пожалуйста, укажите ID правила, которым вы "
            f"хотите управлять]__**\n{ids}\n\nНужнно ввести команду, пробел id. Например /onfr 1"
        )

    else:
        await message.reply_text(
            "#reforwarder\n**__[У вас нет прав для управления пересылкой в этом чате]__**"
        )


@app.on_message(filters=filters.command("getid") & filters.user(settings.TELEGRAM_ID))
async def getid_handler(client: Client, message: Message):
    requested_chat_id = message.chat.id

    if message.chat.username:
        name = f"@{message.chat.username}"
    elif message.chat.title:
        name = message.chat.title
    elif message.chat.first_name or message.chat.last_name:
        name = f"{message.chat.first_name or ''} {message.chat.last_name or ''}"
    else:
        name = ""

    await client.delete_messages(chat_id=message.chat.id, message_ids=message.id)

    await client.send_message(
        chat_id=settings.TELEGRAM_ID,
        text=f"Запрошенный ID {name}: <code>{requested_chat_id}</code>",
        parse_mode=ParseMode.HTML,
    )
    await client.mark_chat_unread(chat_id=settings.TELEGRAM_ID)


@app.on_edited_message()
async def edited_message_handler(client: Client, message: Message):
    if not (
        (await User.objects.aget(user_id=settings.TELEGRAM_ID)).is_forwarding_enabled
    ):
        return

    if message.from_user.id == settings.TELEGRAM_ID:
        return

    forwardings = Forwarding.objects.filter(
        Q(original_message_id=message.id) | Q(new_message_id=message.id)
    ).all()

    async for forwarding in forwardings:
        rule: Rule = await sync_to_async(getattr)(forwarding, "rule")
        to_edit_chat_id = (
            rule.a_chat_id if rule.b_chat_id == message.chat.id else rule.b_chat_id
        )
        to_edit_message_id = (
            forwarding.new_message_id
            if message.id == forwarding.original_message_id
            else forwarding.original_message_id
        )

        filters = Filter.objects.filter(Q(rule=None) | Q(rule=rule))

        skip = False

        async for filter in filters:
            if not filter.is_match_on_message(message):
                continue

            if filter.action == FilterActionEnum.SKIP:
                skip = True
                break

            if filter.action == FilterActionEnum.DISABLE_RULE:
                skip = True
                await rule.disable()

                if rule.notify_myself:
                    await bot.send_message(
                        chat_id=settings.TELEGRAM_ID,
                        text=f"Пересылка {rule} отключена, так как сработал фильтр {filter}",
                        reply_markup=notification_keyboard(rule),
                    )

                break

            if filter.action == FilterActionEnum.REPLACE:
                message = filter.apply_on_message(message)

        if skip:
            try:
                await client.delete_messages(
                    chat_id=to_edit_chat_id,
                    message_ids=to_edit_message_id,
                )
            except Exception as e:
                pass

        top_sign = signature_formatter(rule.top_signature, message)
        bottom_sign = signature_formatter(rule.bottom_signature, message)

        if (
            (rule.signature_direction == "X")
            or (rule.signature_direction == "AB" and rule.a_chat_id == message.chat.id)
            or (rule.signature_direction == "BA" and rule.b_chat_id == message.chat.id)
        ):
            if message.text:
                if top_sign:
                    message.text = f"{top_sign}\n{message.text}"
                if bottom_sign:
                    message.text = f"{message.text}\n{bottom_sign}"

            if message.caption:
                if top_sign:
                    message.caption = f"{top_sign}\n{message.caption}"
                if bottom_sign:
                    message.caption = f"{message.caption}\n{bottom_sign}"

        try:
            if len(message.reactions.reactions) == 0:
                # remove reaction
                await client.send_reaction(
                    chat_id=to_edit_chat_id, message_id=to_edit_message_id
                )
            else:
                # set last reaction
                await client.send_reaction(
                    chat_id=to_edit_chat_id,
                    message_id=to_edit_message_id,
                    emoji=message.reactions.reactions[-1].emoji,
                )

        except Exception as e:
            pass

        try:
            if message.text:
                await client.edit_message_text(
                    chat_id=to_edit_chat_id,
                    message_id=to_edit_message_id,
                    text=message.text,
                    reply_markup=message.reply_markup,
                )

            elif message.caption:
                await client.edit_message_caption(
                    chat_id=to_edit_chat_id,
                    message_id=to_edit_message_id,
                    caption=message.caption,
                    reply_markup=message.reply_markup,
                )

            elif message.photo:
                await client.edit_message_media(
                    chat_id=to_edit_chat_id,
                    message_id=to_edit_message_id,
                    media=message.photo.file_id,
                    reply_markup=message.reply_markup,
                )

        except pyrogram.errors.exceptions.bad_request_400.MessageNotModified:
            pass


@app.on_message()
async def message_handler(client: Client, message: Message):
    if not (
        await User.objects.aget(user_id=settings.TELEGRAM_ID)
    ).is_forwarding_enabled:
        return

    if message.from_user.id == settings.TELEGRAM_ID:
        return

    skip_phrases = [
        "#reforwarder",
        "/on_reforward",
        "/off_reforward",
        "/check_reforward",
        "/onrf",
        "/offrf",
        "/crf",
    ]
    for skip_phrase in skip_phrases:
        if message.text and skip_phrase in message.text.lower():
            return

    rules_a = Rule.objects.filter(a_chat_id=message.chat.id, is_active=True).all()
    rules_b = Rule.objects.filter(
        b_chat_id=message.chat.id, direction="X", is_active=True
    ).all()
    rules = rules_a.union(rules_b)

    async for rule in rules:
        skip = False
        filters = Filter.objects.filter(Q(rule=None) | Q(rule=rule)).all()
        async for filter in filters:
            if not filter.is_match_on_message(message):
                continue

            if filter.action == FilterActionEnum.SKIP:
                skip = True
                break

            if filter.action == FilterActionEnum.DISABLE_RULE:
                skip = True
                await rule.disable()

                if rule.notify_myself:
                    await bot.send_message(
                        chat_id=settings.TELEGRAM_ID,
                        text=f"Пересылка {rule} отключена, так как сработал фильтр {filter}",
                        reply_markup=notification_keyboard(rule),
                    )

                break

            if filter.action == FilterActionEnum.REPLACE:
                message = filter.apply_on_message(message)

        if skip:
            continue

        top_sign = signature_formatter(rule.top_signature, message)
        bottom_sign = signature_formatter(rule.bottom_signature, message)

        if (
            (rule.signature_direction == "X")
            or (rule.signature_direction == "AB" and rule.a_chat_id == message.chat.id)
            or (rule.signature_direction == "BA" and rule.b_chat_id == message.chat.id)
        ):
            if message.text:
                if top_sign:
                    message.text = f"{top_sign}\n{message.text}"
                if bottom_sign:
                    message.text = f"{message.text}\n{bottom_sign}"
            if message.caption:
                if top_sign:
                    message.caption = f"{top_sign}\n{message.caption}"
                if bottom_sign:
                    message.caption = f"{message.caption}\n{bottom_sign}"

        chat_id = (
            rule.b_chat_id if rule.a_chat_id == message.chat.id else rule.a_chat_id
        )

        reply_to_message_id = None
        if message.reply_to_message_id:
            if await sync_to_async(
                Forwarding.objects.filter(
                    original_message_id=message.reply_to_message_id, rule=rule
                ).exists
            )():
                forwarding_a = await Forwarding.objects.filter(
                    original_message_id=message.reply_to_message_id, rule=rule
                ).afirst()
                reply_to_message_id = forwarding_a.new_message_id

            elif await sync_to_async(
                Forwarding.objects.filter(
                    new_message_id=message.reply_to_message_id, rule=rule
                ).exists
            )():
                forwarding_b = await Forwarding.objects.filter(
                    new_message_id=message.reply_to_message_id, rule=rule
                ).afirst()
                reply_to_message_id = forwarding_b.original_message_id

            else:
                # message wasnt forwarded by userbot, copy it

                reply_to_message = message.reply_to_message

                skip = False

                for skip_phrase in skip_phrases:
                    if (
                        reply_to_message.text
                        and skip_phrase in reply_to_message.text.lower()
                    ):
                        skip = True
                        break

                filters = Filter.objects.filter(Q(rule=None) | Q(rule=rule)).all()

                async for filter in filters:
                    if not filter.is_match_on_message(reply_to_message):
                        continue

                    if filter.action in [
                        FilterActionEnum.SKIP,
                        FilterActionEnum.DISABLE_RULE,
                    ]:
                        skip = True
                        break

                    elif filter.action == FilterActionEnum.REPLACE:
                        reply_to_message = filter.apply_on_message(reply_to_message)

                if skip:
                    continue

                datetime_str = reply_to_message.date.strftime("%Y-%m-%d %H:%M:%S")

                if reply_to_message.text:
                    reply_to_message.text = (
                        f"**__[In reply from {datetime_str}]__**\n"
                        + reply_to_message.text
                    )
                elif reply_to_message.caption:
                    reply_to_message.caption = (
                        f"**__[In reply from {datetime_str}]__**\n"
                        + reply_to_message.caption
                    )
                else:
                    await client.send_message(
                        chat_id=chat_id,
                        text=f"**__[In reply from {datetime_str}]__**",
                    )

                reply_to_message = await copy(
                    message=reply_to_message,
                    chat_id=chat_id,
                )

                reply_to_message_id = reply_to_message.id

        new_message = await copy(
            message=message,
            chat_id=chat_id,
            reply_to_message_id=reply_to_message_id,
        )

        if new_message:
            new_message: Message
            await Forwarding.objects.acreate(
                original_message_id=message.id,
                new_message_id=new_message.id,
                rule=rule,
            )
            logger.info(f"Forwarded message {message.id} to {chat_id}")

        else:
            logger.warning(f"Failed to forward message {message.id} to {chat_id}")


idle()
app.stop()
