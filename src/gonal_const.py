DATABASE = "shop.sqlite"
BUY = "💵 Купить"
FAQ = "ℹ FAQ"
REVIEW = "👨‍💻 Поддержка"
SUPPORT = "📮 Обращения"
SUPPORT_HISTORY = "📒 История"
SUPPORT_MES = "📋 Описание поддержки"
EDIT_FAQ = "✒ Редактировать FAQ"
ADD_ITEM = "📚 Добавить товар"
DELETE_ITEM = "🚫 Удалить товар"
ADD_CATEGORY = "📁 Добавить категорию"
ADD_SUBCATEGORY = "📁 Добавить подкатегорию"
DELETE_CATEGORY = "🚫 Удалить категорию"
DELETE_SUBCATEGORY = "🚫 Удалить подкатегорию"
ITEMS_WORK = "📚 Товары"
WORK_PAY = "🔐 Работа с кошельками"
SENDING = "📧 Создать рассылку"
OTHER = "📁 Прочее"
STAT = "📊 Статистика"
REPORT = "📆 Отчеты"
GENERAL = "📋 Общая"
NEXT = "Вперед ➡"
BACK = "⬅ Назад"
CLOSE = "🚫 Закрыть"
YES = "✔ Да"
NO = "❌ Нет"

CONST = [
    DATABASE, BUY, FAQ, REVIEW,
    SUPPORT, SUPPORT_HISTORY, SUPPORT_MES, EDIT_FAQ,
    ADD_ITEM, DELETE_ITEM, ADD_CATEGORY, ADD_SUBCATEGORY,
    DELETE_CATEGORY, DELETE_SUBCATEGORY, ITEMS_WORK, WORK_PAY,
    SENDING, OTHER, STAT, REPORT,
    GENERAL, NEXT, BACK, CLOSE,
    YES, NO
]

def not_const(text):
    return not str(text) in CONST
