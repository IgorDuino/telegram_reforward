from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from typing import List

from tgbot.models import Filter


def filters_keyboard(filters: List[Filter], rule=None) -> InlineKeyboardMarkup:
    buttons = []

    for filter_ in filters:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"[{filter_.name if filter_.name else filter_.id}]",
                    callback_data=f"filter:{filter_.id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "🔙 Назад",
                callback_data=f"rule:{rule.id}" if rule else "start",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def filter_keyboard(filter_: Filter) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                "🗑 Удалить фильтр",
                callback_data=f"delete:filter:{filter_.id}",
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Назад",
                callback_data="start",
            )
        ],
    ]

    return InlineKeyboardMarkup(buttons)
