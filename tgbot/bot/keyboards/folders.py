from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from tgbot.models import Folder

from typing import List


def chose_folder_keyboard(folders: List[Folder]) -> InlineKeyboardMarkup:
    buttons = []

    for folder in folders:
        buttons.append([InlineKeyboardButton(folder.name, callback_data=f"folder:{folder.id}")])

    buttons.append([InlineKeyboardButton("Без папки", callback_data="folder:nofolder")])

    return InlineKeyboardMarkup.from_column(buttons)
