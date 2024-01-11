from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def cancel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Отмена", callback_data="cancel"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)
