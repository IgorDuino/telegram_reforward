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


def signature_formatter(signature: str, message: Message) -> str:
    signature = signature.replace("{first_name}", message.from_user.first_name or "")
    signature = signature.replace("{last_name}", message.from_user.last_name or "")
    signature = signature.replace("{username}", message.from_user.username or "")
    signature = signature.replace("{title}", message.chat.title or "")
    signature = signature.replace("{chat_id}", str(message.chat.id))
    signature = signature.replace("{user_id}", str(message.from_user.id))

    return signature


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
        filters = Filter.objects.filter(Q(rule=None) | Q(rule=rule))
        async for filter in filters:
            if not filter.is_match_on_message(message):
                continue

            if filter.action == FilterActionEnum.SKIP:
                skip = True
                break

            if filter.action == FilterActionEnum.DISABLE_RULE:
                skip = True
                await rule.disable()
                break

            if filter.action == FilterActionEnum.REPLACE:
                message = filter.apply_on_message(message)

        if skip:
            continue

        if message.text:
            if rule.top_signature:
                message.text = f"{rule.top_signature}\n{message.text}"
            if rule.bottom_signature:
                message.text = f"{message.text}\n{rule.bottom_signature}"
        if message.caption:
            if rule.top_signature:
                message.caption = f"{rule.top_signature}\n{message.caption}"
            if rule.bottom_signature:
                message.caption = f"{message.caption}\n{rule.bottom_signature}"

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

        new_message = await message.copy(chat_id=chat_id, reply_to_message_id=reply_to_message_id)

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
