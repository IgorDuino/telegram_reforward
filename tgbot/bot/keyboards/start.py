from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("Правила", callback_data="rules"),
        InlineKeyboardButton("Новое правило", callback_data="add_rule"),
        InlineKeyboardButton("Новая папка", callback_data="add_folder"),
        InlineKeyboardButton("Общие фильтры", callback_data="filters:general"),
        InlineKeyboardButton("Новый общий фильтр", callback_data="add_filter:general"),
        InlineKeyboardButton(
            "Отключить пересылку" if enabled else "Включить пересылку",
            callback_data="toggle:forwarding:0" if enabled else "toggle:forwarding:1",
        ),
    ]

    return InlineKeyboardMarkup.from_column(buttons)
