import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


logger = logging.getLogger(__name__)


async def extract_user_data_from_update(update) -> dict:
    """python-telegram-bot's Update instance --> User info"""
    if update.message is not None:
        user = update.message.from_user.to_dict()
    elif update.inline_query is not None:
        user = update.inline_query.from_user.to_dict()
    elif update.chosen_inline_result is not None:
        user = update.chosen_inline_result.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.from_user is not None:
        user = update.callback_query.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.message is not None:
        user = update.callback_query.message.chat.to_dict()
    else:
        raise Exception(f"Can't extract user data from update: {update}")

    return dict(
        user_id=user["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )


async def delete_message(bot, user_id, message_id):
    try:
        await bot.deleteMessage(chat_id=user_id, message_id=message_id)
    except Exception as e:  # can't delete old message
        logger.debug(f"Can't delete old message {message_id} from user {user_id}")
        await bot.editMessageReplyMarkup(
            chat_id=user_id,
            message_id=message_id,
            reply_markup=None,
        )


ALL_TG_FILE_TYPES = [
    "document",
    "video_note",
    "voice",
    "sticker",
    "audio",
    "video",
    "animation",
    "photo",
]


def get_file_id(m):
    """extract file_id from message (and file type?)"""

    for doc_type in ALL_TG_FILE_TYPES:
        if doc_type in m and doc_type != "photo":
            return m[doc_type]["file_id"]

    if "photo" in m:
        best_photo = m["photo"][-1]
        return best_photo["file_id"]
