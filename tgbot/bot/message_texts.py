START = "Здравствуйте"

NOT_AUTHORIZED = "Вы не авторизованы"
RULES_EMPTY = "Правил нет"
RULES = "Корневые правила и папки:"
RULE = """
Имя: {name}
Чат A: `{a_chat_id}`
Чат B: `{b_chat_id}`
Направление пересылки: `{direction}`
Верхняя подпись: `{top_signature}`
Нижняя подпись: `{bottom_signature}`
Направление применения подписи: `{signature_direction}`
Уведомлять чат А при включении/выключении правила?: `{notify_a}`
Уведомлять чат B при включении/выключении правила?: `{notify_b}`
Уведомлять меня при отключении из\-за фильтра?: `{notify_myself}`
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
ADD_FILTER_ERROR = "Ошибка создания фильтра, возможно проблема в регулярном выражении"
WRONG_CHAT_ID = "Неверный chat\_id, попробуйте еще раз"
RESTART = "Система будет перезапущена в ближайшее время\. Напишите /start через несколько минут"