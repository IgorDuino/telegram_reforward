from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from typing import List

from tgbot.models import Folder, Rule


def rules_keyboard(folders: List[Folder], rules: List[Rule], folder=None) -> InlineKeyboardMarkup:
    buttons = []

    for folder in folders:
        buttons.append(
            [InlineKeyboardButton(f"📂 {folder.name}", callback_data=f"folder:{folder.id}")]
        )

    for rule in rules:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{'🟢' if rule.is_active else '🔴'} {rule.name}", callback_data=f"rule:{rule.id}"
                )
            ]
        )

    if folder:
        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        "🔙 Назад",
                        callback_data=f"folder:{folder.parent.id}" if folder.parent else "rules",
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

    return InlineKeyboardMarkup(buttons)


def rule_keyboard(rule: Rule) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="🟢 Включить" if not rule.is_active else "🔴 Выключить",
                callback_data=f"toggle:rule:1:{rule.id}"
                if rule.is_active
                else f"toggle:rule:1:{rule.id}",
            )
        ],
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete:rule:{rule.id}")],
    ]

    return InlineKeyboardMarkup(buttons)


def cancel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Отмена", callback_data="cancel"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


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
        InlineKeyboardButton("Уведомлять первого", callback_data="notify:a"),
        InlineKeyboardButton("Уведомлять второго", callback_data="notify:b"),
        InlineKeyboardButton("Уведомлять обоих", callback_data="notify:both"),
        InlineKeyboardButton("Никого не уведомлять", callback_data="notify:nobody"),
    ]

    return InlineKeyboardMarkup.from_column(buttons)


def skip_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        KeyboardButton("ПРОПУСТИТЬ"),
    ]

    return ReplyKeyboardMarkup.from_column(buttons)
