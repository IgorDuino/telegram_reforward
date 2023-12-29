from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Правила", callback_data="rules"),
        InlineKeyboardButton("Новое правило", callback_data="add_rule"),
        InlineKeyboardButton("Общие фильры", callback_data="general_filters"),
        InlineKeyboardButton("Новый общий фильтр", callback_data="add_general_filter"),
        InlineKeyboardButton(
            "Отключить пересылку" if enabled else "Включить пересылку",
            callback_data="disable_forwarding" if enabled else "enable_forwarding",
        ),
    ]

    return InlineKeyboardMarkup.from_column(buttons)
