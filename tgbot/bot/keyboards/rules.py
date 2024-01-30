from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from typing import List

from tgbot.models import Folder, Rule


def rules_keyboard(
    folders: List[Folder], rules: List[Rule], folder=None
) -> InlineKeyboardMarkup:
    buttons = []

    for folder_ in folders:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"📂 {folder_.name}", callback_data=f"folder:{folder_.id}"
                )
            ]
        )

    for i, rule in enumerate(rules):
        buttons.append(
            [
                InlineKeyboardButton(
                    f"[{i}] {'🟢' if rule.is_active else '🔴'} {rule.name}",
                    callback_data=f"rule:{rule.id}",
                )
            ]
        )

    if folder:
        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        "⬆️ Вверх",
                        callback_data=f"folder:{folder.parent.id}"
                        if folder.parent
                        else "rules",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Удалить папку",
                        callback_data=f"delete:folder:{folder.id}",
                    )
                ],
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "🔙 Назад",
                callback_data="start",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


def rule_keyboard(rule: Rule) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="🟢 Включить" if not rule.is_active else "🔴 Выключить",
                callback_data=f"toggle:rule:1:{rule.id}"
                if not rule.is_active
                else f"toggle:rule:0:{rule.id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="🌪 Фильтры",
                callback_data=f"filters:{rule.id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Добавить фильтр",
                callback_data=f"add_filter:{rule.id}",
            )
        ],
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete:rule:{rule.id}")],
        [
            InlineKeyboardButton(
                "🔙 Назад",
                callback_data=f"folder:{rule.folder.id}" if rule.folder else "rules",
            )
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def choose_rule_direction_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("One way", callback_data="one_way"),
        InlineKeyboardButton("Two way", callback_data="two_way"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def yes_no_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Да", callback_data="yes"),
        InlineKeyboardButton("Нет", callback_data="no"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def who_notify_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Уведомлять чат A", callback_data="notify:a"),
        InlineKeyboardButton("Уведомлять чат B", callback_data="notify:b"),
        InlineKeyboardButton("Уведомлять A и B", callback_data="notify:ab"),
        InlineKeyboardButton("Никого не уведомлять", callback_data="notify:_"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def skip_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("ПРОПУСТИТЬ", callback_data="skip"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def notify_myself_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Уведомлять меня", callback_data="notify_myself:1"),
        InlineKeyboardButton("Не уведомлять меня", callback_data="notify_myself:0"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def signature_direction_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("A -> B", callback_data="signature_direction:AB"),
        InlineKeyboardButton("B -> A", callback_data="signature_direction:BA"),
        InlineKeyboardButton("A <-> B", callback_data="signature_direction:X"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def chat_members_control_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            "Участники чата A", callback_data="chat_members_control:a"
        ),
        InlineKeyboardButton(
            "Участники чата A", callback_data="chat_members_control:b"
        ),
        InlineKeyboardButton(
            "Участники обоих чатов", callback_data="chat_members_control:ab"
        ),
        InlineKeyboardButton("Только я", callback_data="chat_members_control:_"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)
