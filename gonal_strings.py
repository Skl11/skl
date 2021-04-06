import datetime


def format_str(count, form):
    form_str = ""
    if count == 1:
        form_str = form[0]
    elif 10 <= count % 100 <= 20:
        form_str = form[2]
    elif count % 10 == 1:
        form_str = form[0]
    elif 2 <= count % 10 <= 4:
        form_str = form[1]
    else:
        form_str = form[2]
    return form_str


def get_text_itmes(count):
    form = ["товар был добавлен",
            "товара было добавлено",
            "товаров было добавлено"]

    form_str = format_str(count, form)

    return f"✔ {count} {form_str} "

def get_text_cat(count):
    form = ["категория была добавлена",
            "категории было добавлено",
            "категорий было добавлено"]

    form_str = format_str(count, form)

    return f"📦 {count} {form_str}"


def get_text_send(count):
    form = ["сообщение отправлено!",
            "сообщения отправлено!",
            "сообщений отправлено!"]

    form_str = format_str(count, form)

    return f"✉ {count} {form_str}"

# Форматирование времени
def get_time_format():
    now = datetime.datetime.now()

    day = now.day
    month = now.month
    if int(month) < 10:
        month = f"0{month}"

    hour = now.hour
    min = now.minute
    if int(min) < 10:
        min = f"0{min}"

    return f"{day}/{month} {hour}:{min}"


# сообщение о покупке
def get_sold_message(user, item, price):
    return "🛒 Новая покупка\n" \
            f"🔹 Пользователь: @{user} \n" \
            f"🔹 Товар: {item} \n" \
            f"🔹 Сумма покупки: {price} руб"


# сообщение для покупки
def get_buy_message(name, num, comment, price):
    return "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                      f"Покупка товара *{name}*\n" \
                      "Для оплаты, нажмите кнопку *💳 Оплатить*\n" \
                      "Поля менять *не надо*\n" \
                      "*Обязательно указывайте комментарий к оплате указанный ниже, иначе бот не сможет выдать покупку*\n" \
                      "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                      f"📱 *Номер*: `{num}`\n" \
                      f"✏ *Комментарий*: `{comment}`\n" \
                      f"💰 *Сумма*: `{price} руб`\n" \
                      "После оплаты нажмите кнопку *🔄 Проверка оплаты*\n" \
                      "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"

# инфа о товаре
def get_info_message(name, desc, price, count):
    msg = "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n" + \
          f"▪ Имя товара: {name} \n" + \
          f"▪ Описание: \n {desc} \n" + \
          f"▪ Стоимость: {price} руб. \n"

    if count != "file":
        msg += f"▪ Осталось: {count} шт. \n"

    return msg + "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"