START = "Здравствуйте"

NOT_AUTHORIZED = "Вы не авторизованы"
RULES_EMPTY = "Правил нет"
RULES = "Корневые правила и папки:"
RULE = """
Имя: {name}
Пересылка из: `{a_chat_id}`
Пересылка в: `{b_chat_id}`
Направление: `{direction}`
Верхняя подпись: `{top_signature}`
Нижняя подпись: `{bottom_signature}`
"""
DONE = "Выполнено"
DELETED = "Удалено"

RULE_FILTERS = "Фильтры правила `{rule}`:"
GENERAL_FILTERS = "Общие фильтры:"
FILTER = """
Фильтр `{filter_name}`
Trigger: `{trigger}`
Действие: `{action}`
Замена на: `{replacement}`
"""
FILTERS_EMPTY = "Фильтров нет"
ADD_FOLDER_NAME = "Отправьте название папки"
ADD_FOLDER_PARENT = "Выберите родительскую папку"
FOLDER_CREATED = "Папка создана"


ADD_FILTER_NAME = "Введите название фильтра"
ADD_FILTER_TRIGGER = "Введите триггер фильтра или выберите из списка"
ADD_FILTER_ACTION = "Выберите действие фильтра"
ADD_FILTER_REPLACEMENT = (
    "Введите замену или нажмите УДАЛИТЬ чтобы заменить триггер на пустую строку"
)
ADD_FILTER_CONFIRM = """
Подтвердите создание фильтра:
Имя: `{name}`
Trigger: `{trigger}`
Действие: `{action}`
Замена на: `{replacement}`
"""
FILTER_CREATED = "Фильтр создан"
