from dotenv import load_dotenv

load_dotenv()

import django

django.setup()


from reforward import settings
from django.db.models import Q

from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import logging
from tgbot.models import User, Filter, FilterActionEnum, Rule, Forwarding
from pyrogram_utils import copy

import telegram

from asgiref.sync import sync_to_async


bot = telegram.Bot(settings.TELEGRAM_TOKEN)


def signature_formatter(signature: str, message: Message) -> str:
    if signature:
        signature = signature.replace("{first_name}", message.from_user.first_name or "")
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
    if not User.objects.get(user_id=my_id).is_forwarding_enabled:
        return

    for message in messages:
        for forwarding in Forwarding.objects.filter(original_message_id=message.id).all():
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.a_chat_id, message_ids=forwarding.new_message_id
                )
            except Exception as e:
                pass
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.b_chat_id, message_ids=forwarding.new_message_id
                )
            except Exception as e:
                pass

            forwarding.delete()

        for forwarding in Forwarding.objects.filter(new_message_id=message.id).all():
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.a_chat_id, message_ids=forwarding.original_message_id
                )
            except Exception as e:
                pass
            try:
                client.delete_messages(
                    chat_id=forwarding.rule.b_chat_id, message_ids=forwarding.original_message_id
                )
            except Exception as e:
                pass

            forwarding.delete()


@app.on_message(filters=filters.command("getid"))
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
        chat_id=my_id,
        text=f"Запрошенный ID {name}: <code>{requested_chat_id}</code>",
        parse_mode=ParseMode.HTML,
    )
    await client.mark_chat_unread(chat_id=my_id)


@app.on_edited_message()
async def edited_message_handler(client: Client, message: Message):
    if not ((await User.objects.aget(user_id=my_id)).is_forwarding_enabled):
        return

    forwardings = Forwarding.objects.filter(
        Q(original_message_id=message.id) | Q(new_message_id=message.id)
    ).all()

    async for forwarding in forwardings:
        rule = await sync_to_async(getattr)(forwarding, "rule")
        to_edit_chat_id = rule.a_chat_id if rule.b_chat_id == message.chat.id else rule.b_chat_id
        to_edit_message_id = (
            forwarding.new_message_id
            if message.id == forwarding.original_message_id
            else forwarding.original_message_id
        )

        print(message.id, message.chat.id)

        print(to_edit_chat_id, to_edit_message_id)

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
            rule.signature_direction == "X"
            or (forwarding.original_message_id == message.id and rule.signature_direction == "AB")
            or (forwarding.new_message_id == message.id and rule.signature_direction == "BA")
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


@app.on_message()
async def message_handler(client: Client, message: Message):
    if not (await User.objects.aget(user_id=my_id)).is_forwarding_enabled:
        return

    if message.from_user.id == my_id:
        return

    rules_a = Rule.objects.filter(a_chat_id=message.chat.id, is_active=True).all()
    rules_b = Rule.objects.filter(b_chat_id=message.chat.id, direction="X", is_active=True).all()
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
                    )

                break

            if filter.action == FilterActionEnum.REPLACE:
                message = filter.apply_on_message(message)

        if skip:
            continue

        top_sign = signature_formatter(rule.top_signature, message)
        bottom_sign = signature_formatter(rule.bottom_signature, message)

        if (rule.signature_direction == "X") or (
            rule.signature_direction == "AB" and rule.a_chat_id == message.chat.id
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

        chat_id = rule.b_chat_id if rule.a_chat_id == message.chat.id else rule.a_chat_id

        reply_to_message_id = None
        if message.reply_to_message_id:
            forwarding_a = await Forwarding.objects.filter(
                original_message_id=message.reply_to_message_id, rule=rule
            ).afirst()
            if forwarding_a:
                reply_to_message_id = forwarding_a.new_message_id
            else:
                forwarding_b = await Forwarding.objects.filter(
                    new_message_id=message.reply_to_message_id, rule=rule
                ).afirst()
                if forwarding_b:
                    reply_to_message_id = forwarding_b.original_message_id

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


from pyrogram.raw.types import UpdateEditMessage


@app.on_raw_update()
def reaction_handler(client: Client, update: UpdateEditMessage, users, chats):
    if not User.objects.get(user_id=my_id).is_forwarding_enabled:
        return

    try:
        recent_reactions = update.message.reactions.recent_reactions
        message: Message = update.message
    except Exception as e:
        return

    for forwarding in Forwarding.objects.filter(original_message_id=message.id).all():
        try:
            for reaction in recent_reactions:
                client.send_reaction(
                    chat_id=forwarding.rule.a_chat_id
                    if forwarding.rule.direction == "O"
                    else forwarding.rule.b_chat_id,
                    message_id=forwarding.new_message_id,
                    emoji=reaction.reaction.emoticon,
                )
        except Exception as e:
            pass

    for forwarding in Forwarding.objects.filter(new_message_id=message.id).all():
        try:
            for reaction in recent_reactions:
                client.send_reaction(
                    chat_id=forwarding.rule.a_chat_id
                    if forwarding.rule.direction == "O"
                    else forwarding.rule.b_chat_id,
                    message_id=forwarding.original_message_id,
                    emoji=reaction.reaction.emoticon,
                )
        except Exception as e:
            pass


idle()
app.stop()
