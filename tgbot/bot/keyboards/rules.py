from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


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
