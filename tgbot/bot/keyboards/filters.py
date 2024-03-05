from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from typing import List

from tgbot.models import Filter, FilterTriggerTemplate


def filters_keyboard(filters: List[Filter], rule=None) -> InlineKeyboardMarkup:
    buttons = []

    for filter_ in filters:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{'🟢' if filter_.is_active else '🔴'} [{filter_.name if filter_.name else filter_.id}]",
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
                "Отключить фильтр" if filter_.is_active else "Включить фильтр",
                callback_data=f"toggle:filter:0:{filter_.id}" if filter_.is_active else f"toggle:filter:1:{filter_.id}",
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


def add_filter_trigger_keyboard(
    trigger_templates: List[FilterTriggerTemplate],
) -> InlineKeyboardMarkup:
    buttons = []

    for trigger_template in trigger_templates:
        buttons.append(
            [
                InlineKeyboardButton(
                    trigger_template.name,
                    callback_data=f"add_filter_trigger:{trigger_template.id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "Отмена",
                callback_data="cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def add_filter_action_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Заменить", callback_data="add_filter_action:R"),
        InlineKeyboardButton(
            "Пропустить сообщение", callback_data="add_filter_action:S"
        ),
        InlineKeyboardButton("Выключить правило", callback_data="add_filter_action:D"),
        InlineKeyboardButton("Отмена", callback_data="cancel"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def add_filter_replace_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("УДАЛИТЬ", callback_data="delete"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def add_filter_confirm_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Подтвердить", callback_data="add_filter_confirm"),
        InlineKeyboardButton("Отмена", callback_data="cancel"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)
