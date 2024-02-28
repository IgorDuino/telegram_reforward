import logging
from datetime import datetime
from functools import partial
from typing import List, Union, Optional
from pyrogram import types, utils, raw, enums


log = logging.getLogger("pyrogram")


async def copy(
    message: types.Message,
    chat_id: Union[int, str],
    caption: str = None,
    parse_mode: Optional["enums.ParseMode"] = None,
    caption_entities: List["types.MessageEntity"] = None,
    has_spoiler: bool = None,
    disable_notification: bool = None,
    message_thread_id: int = None,
    quote_text: str = None,
    reply_to_message_id: int = None,
    schedule_date: datetime = None,
    protect_content: bool = None,
    reply_markup: Union[
        "types.InlineKeyboardMarkup",
        "types.ReplyKeyboardMarkup",
        "types.ReplyKeyboardRemove",
        "types.ForceReply",
    ] = object,
) -> Union["types.Message", List["types.Message"]]:
    """Bound method *copy* of :obj:`~pyrogram.types.Message`.

    Use as a shortcut for:

    .. code-block:: python

        await client.copy_message(
            chat_id=chat_id,
            from_chat_id=message.chat.id,
            message_id=message.id
        )

    Example:
        .. code-block:: python

            await message.copy(chat_id)

    Parameters:
        chat_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages) you can simply use "me" or "message".
            For a contact that exists in your Telegram address book you can use his phone number (str).

        caption (``string``, *optional*):
            New caption for media, 0-1024 characters after entities parsing.
            If not specified, the original caption is kept.
            Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the new caption, which can be specified instead of *parse_mode*.

        has_spoiler (``bool``, *optional*):
            Pass True if the photo needs to be covered with a spoiler animation.

        disable_notification (``bool``, *optional*):
            Sends the message silently.
            Users will receive a notification with no sound.

        message_thread_id (``int``, *optional*):
            Unique identifier for the target message thread (topic) of the forum.
            for forum supergroups only.

        quote_text (``str``, *optional*):
            Text to quote.
            for reply_to_message only.

        reply_to_message_id (``int``, *optional*):
            If the message is a reply, ID of the original message.

        schedule_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the message will be automatically sent.

        protect_content (``bool``, *optional*):
            Protects the contents of the sent message from forwarding and saving.

        reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
            Additional interface options. An object for an inline keyboard, custom reply keyboard,
            instructions to remove reply keyboard or to force a reply from the user.
            If not specified, the original reply markup is kept.
            Pass None to remove the reply markup.

    Returns:
        :obj:`~pyrogram.types.Message`: On success, the copied message is returned.

    Raises:
        RPCError: In case of a Telegram RPC error.
    """
    if message.service:
        log.warning(
            "Service messages cannot be copied. chat_id: %s, message_id: %s",
            message.chat.id,
            message.id,
        )
    elif message.game and not await message._client.storage.is_bot():
        log.warning(
            "Users cannot send messages with Game media type. chat_id: %s, message_id: %s",
            message.chat.id,
            message.id,
        )
    elif message.empty:
        log.warning("Empty messages cannot be copied.")
    elif message.text:
        return await message._client.send_message(
            chat_id,
            text=message.text,
            entities=message.entities,
            parse_mode=parse_mode,
            disable_web_page_preview=not message.web_page_preview,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            schedule_date=schedule_date,
            protect_content=protect_content,
            reply_markup=message.reply_markup if reply_markup is object else reply_markup,
        )
    elif message.media:
        send_media = partial(
            message._client.send_cached_media,
            chat_id=chat_id,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            has_spoiler=has_spoiler,
            protect_content=protect_content,
            reply_markup=message.reply_markup if reply_markup is object else reply_markup,
        )

        if message.photo:
            file_id = message.photo.file_id
        elif message.audio:
            file_id = message.audio.file_id
        elif message.document:
            file_id = message.document.file_id
        elif message.video:
            file_id = message.video.file_id
        elif message.animation:
            file_id = message.animation.file_id
        elif message.voice:
            file_id = message.voice.file_id
        elif message.sticker:
            file_id = message.sticker.file_id
        elif message.video_note:
            file_id = message.video_note.file_id
        elif message.contact:
            return await message._client.send_contact(
                chat_id,
                phone_number=message.contact.phone_number,
                first_name=message.contact.first_name,
                last_name=message.contact.last_name,
                vcard=message.contact.vcard,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
            )
        elif message.location:
            return await message._client.send_location(
                chat_id,
                latitude=message.location.latitude,
                longitude=message.location.longitude,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
            )
        elif message.venue:
            return await message._client.send_venue(
                chat_id,
                latitude=message.venue.location.latitude,
                longitude=message.venue.location.longitude,
                title=message.venue.title,
                address=message.venue.address,
                foursquare_id=message.venue.foursquare_id,
                foursquare_type=message.venue.foursquare_type,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
            )
        elif message.poll:
            return await message._client.send_poll(
                chat_id,
                question=message.poll.question,
                options=[opt.text for opt in message.poll.options],
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
            )
        elif message.game:
            return await message._client.send_game(
                chat_id,
                game_short_name=message.game.short_name,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
            )
        elif message.web_page_preview:
            return await message._client.send_web_page(
                chat_id,
                url=message.web_page_preview.webpage.url,
                text=message.caption,
                entities=message.entities,
                parse_mode=parse_mode,
                large_media=message.web_page_preview.force_large_media,
                invert_media=message.web_page_preview.invert_media,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                reply_to_message_id=reply_to_message_id,
                quote_text=quote_text,
                schedule_date=schedule_date,
                protect_content=protect_content,
                reply_markup=message.reply_markup if reply_markup is object else reply_markup,
            )
        else:
            raise ValueError("Unknown media type")

        if message.sticker or message.video_note:  # Sticker and VideoNote should have no caption
            return await send_media(file_id=file_id, message_thread_id=message_thread_id)
        else:
            if caption is None:
                caption = message.caption or ""
                caption_entities = message.caption_entities

            return await send_media(
                file_id=file_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                has_spoiler=has_spoiler,
                message_thread_id=message_thread_id,
            )
    else:
        raise ValueError("Can't copy this message")
