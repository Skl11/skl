# -*- coding: utf-8 -*-
import configparser
import os
import time
from datetime import datetime
import telebot
from telebot.util import async_dec
import random

from src import gonal_const as const
from src import gonal_admin as admin
import gonal_database as shop_db
import gonal_payment as payment
import gonal_strings as string_help

bot = telebot.AsyncTeleBot(admin.TOKEN, parse_mode="MARKDOWN")

admin_keyboard = telebot.types.ReplyKeyboardMarkup(True)
admin_keyboard.row(const.BUY, const.FAQ)
admin_keyboard.row(const.ITEMS_WORK, const.WORK_PAY)
admin_keyboard.row(const.STAT)
admin_keyboard.row(const.REVIEW)
admin_keyboard.row(const.OTHER)

user_keyboard = telebot.types.ReplyKeyboardMarkup(True)
user_keyboard.row(const.BUY, const.FAQ)
user_keyboard.row(const.REVIEW)

database = shop_db.ShopDB()

payment.database = database
payment.comment = admin.COMMENT_PAY
qiwi = payment.Qiwi()

@bot.message_handler(commands=['start'])
def start_message(message):
    if admin.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, 'Добро пожаловать! Если не появились кнопки, напишите /start',
                         reply_markup=admin_keyboard)
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать! Если не появились кнопки, напишите /start',
                         reply_markup=user_keyboard)
    database.input_user(message.chat.id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # Купить
    if message.text == const.BUY:
        keyboard, count = get_categories("select_category=")
        if count:
            bot.send_message(message.from_user.id, "📂 Доступные категории", reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id, "😔 В данный момент товары отсутствуют")

    # FAQ
    elif message.text == const.FAQ:
        bot.send_message(message.chat.id, database.get_faq(), parse_mode="HTML")

    # Написать отзыв
    elif message.text == const.REVIEW:
        if admin.is_admin(message.from_user.id):
            keyboard = telebot.types.ReplyKeyboardMarkup(True)
            keyboard.row(const.SUPPORT, const.SUPPORT_HISTORY)
            keyboard.row(const.SUPPORT_MES)
            keyboard.row(const.BACK)
            bot.send_message(message.chat.id, const.REVIEW, reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id, database.get_support_main_mes(), parse_mode="HTML")

            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text="❓ Вопрос", callback_data="support_user=❓ Вопрос"))
            keyboard.add(telebot.types.InlineKeyboardButton(text="💳 Оплата", callback_data="support_user=💳 Оплата"))
            keyboard.add(telebot.types.InlineKeyboardButton(text="📚 Товары", callback_data="support_user=📚 Товары"))
            keyboard.add(telebot.types.InlineKeyboardButton(text="📝 Прочее", callback_data="support_user=📝 Прочее"))
            keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK, callback_data="cancel"))
            bot.send_message(message.from_user.id, "📝 Выберите категорию обращения", reply_markup=keyboard)

    # Админ Панель
    # Прочее
    elif message.text == const.OTHER and admin.is_admin(message.from_user.id):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row(const.SENDING)
        keyboard.row(const.EDIT_FAQ)
        keyboard.row(const.BACK)
        bot.send_message(message.chat.id, const.OTHER, reply_markup=keyboard)

    # Рассылки
    elif message.text == const.SENDING and admin.is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "📝 Введите текст рассылки")
        bot.register_next_step_handler(message, create_sending)

    # Обращения в поддержку без ответа
    elif message.text == const.SUPPORT and admin.is_admin(message.from_user.id):
        get_support_messages(message, False)

    # История запросов
    elif message.text == const.SUPPORT_HISTORY and admin.is_admin(message.from_user.id):
        get_support_messages(message, True)

    # описание поддержки
    elif message.text == const.SUPPORT_MES and admin.is_admin(message.from_user.id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="✏ Редактировать",
                                                        callback_data="edit_supmes"))
        bot.send_message(message.from_user.id, database.get_support_main_mes(), reply_markup=keyboard)

    # Редактирование FAQ
    elif message.text == const.EDIT_FAQ and admin.is_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "✒ Введите новый текст FAQ")
        bot.register_next_step_handler(message, edit_faq)

    # Работа с товарами
    elif message.text == const.ITEMS_WORK and admin.is_admin(message.from_user.id):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row(const.ADD_ITEM, const.DELETE_ITEM)
        keyboard.row(const.ADD_CATEGORY, const.DELETE_CATEGORY)
        keyboard.row(const.BACK)
        bot.send_message(message.chat.id, const.ITEMS_WORK, reply_markup=keyboard)

    # Добавить товар
    elif message.text == const.ADD_ITEM and admin.is_admin(message.from_user.id):
        keyboard, b = get_categories("category=")

        if b:
            bot.send_message(message.chat.id, "📚 Выберите категорию товара", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "😔 Нет доступных категорий")

    # Удалить товар
    elif message.text == const.DELETE_ITEM and admin.is_admin(message.from_user.id):
        keyboard, b = get_categories("cat_del=")

        if b:
            bot.send_message(message.chat.id, "📚 Выберите категорию товара", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "😔 Нет доступных категорий")

    # Добавить категорию
    elif message.text == const.ADD_CATEGORY and admin.is_admin(message.from_user.id):
        keyboard, b = get_categories("sub_cat_add=")

        keyboard.add(telebot.types.InlineKeyboardButton(text="📝 Добавить новую категорию",
                                                        callback_data="category=new_category"))
        bot.send_message(message.chat.id, "📂 Существующие категории \n"
                                          "📁 Для добавления подкатегории *нажмите на нужную категорию*",
                         reply_markup=keyboard)

    # Удалить категорию
    elif message.text == const.DELETE_CATEGORY and admin.is_admin(message.from_user.id):
        keyboard, b = get_categories("categ_del=")
        if b:
            bot.send_message(message.chat.id, "📁 Выберите категорию", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "😔 Нет доступных категорий")

    # Работа с кошельками
    elif message.text == const.WORK_PAY and admin.is_admin(message.from_user.id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🥝 QIWI", callback_data="payment=qiwi"))

        bot.send_message(message.chat.id, "💳 Выберите кошелек", reply_markup=keyboard)

    # Статистика
    elif message.text == const.STAT and admin.is_admin(message.from_user.id):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row(const.REPORT, const.GENERAL)
        keyboard.row(const.BACK)
        bot.send_message(message.chat.id, const.STAT, reply_markup=keyboard)

    # Отчеты
    elif message.text == const.REPORT and admin.is_admin(message.from_user.id):
        create_date_list()
        keyboard = create_report_keyboard(0)

        bot.send_message(message.from_user.id, "📆 Выберите дату отчета", reply_markup=keyboard)

    # Общая статистка
    elif message.text == const.GENERAL and admin.is_admin(message.from_user.id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        user_count = len(database.get_user_list())
        sales_list = database.get_sales()
        sales_len = len(sales_list)

        sales_sum = 0
        sales_most = dict()
        buyers_most = dict()
        for i in range(sales_len):
            sales_sum += int(sales_list[i][4])

            buyer = sales_list[i][0]
            name = sales_list[i][1]
            if name in sales_most:
                sales_most.update({name: int(sales_most.get(name)) + 1})
            else:
                sales_most[name] = int(1)

            if buyer in buyers_most:
                buyers_most.update({buyer: int(buyers_most.get(buyer) + 1)})
            else:
                buyers_most[buyer] = int(1)


        sales_sort = sorted(sales_most, key=sales_most.get, reverse=True)
        buyers_sort = sorted(buyers_most, key=buyers_most.get, reverse=True)

        sales_list = {}
        buyers_list = {}
        for i in sales_sort:
            sales_list[i] = sales_most[i]
        for i in buyers_sort:
            buyers_list[i] = buyers_most[i]

        sales = get_ten_data(sales_sort, sales_most)
        buyers = get_ten_data(buyers_sort, buyers_most)

        msg = "📊 Статистика магазина\n\n" \
              f"💻 Количество пользователей: {user_count}\n" \
              f"💰 Прибыль магазина: {sales_sum} руб.\n\n" \
              f"🛒 Часто покупаемые товары: \n{sales}\n" \
              f"💳 Активные покупатели: \n{buyers}"

        keyboard.add(telebot.types.InlineKeyboardButton(text=const.CLOSE,
                                                        callback_data="cancel"))
        bot.send_message(message.from_user.id, msg, reply_markup=keyboard)


    # Назад
    elif message.text == const.BACK:
        if admin.is_admin(message.from_user.id):
            bot.send_message(message.chat.id, "🔹 Главное меню 🔹", reply_markup=admin_keyboard)
        else:
            bot.send_message(message.chat.id, "🔹 Главное меню 🔹", reply_markup=user_keyboard)

    # Если неизвестная команда
    else:
        if admin.is_admin(message.from_user.id):
            bot.send_message(message.from_user.id, "❗ Неизвестная команда! Введите /start",
                             reply_markup=admin_keyboard)
        else:
            bot.send_message(message.from_user.id, "❗ Неизвестная команда! Введите /start",
                             reply_markup=user_keyboard)

def get_ten_data(dict, list):
    count = 0
    data = ""
    while count < 10 and count < len(list):
        data += f"▫ {dict[count]} – {list.get(dict[count])}\n"
        count += 1

    return data

# Создание клавиатуры с отчетами
def create_report_keyboard(cur_page):
    page = int(cur_page)
    next_page = page + 10
    keyboard = telebot.types.InlineKeyboardMarkup()
    while page < next_page and page < len(date_sort):
        date = date_sort[page]
        keyboard.add(telebot.types.InlineKeyboardButton(
            text=date, callback_data=f"report={date}|{cur_page}"))
        page += 1
    btn_list = []
    if next_page < len(date_sort):
        btn_list.append(telebot.types.InlineKeyboardButton(text=const.NEXT,
                                                           callback_data=f"get_report={next_page}"))
    if int(cur_page) >= 10:
        prev_page = int(cur_page) - 10
        btn_list.append(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                           callback_data=f"get_report={prev_page}"))
    if len(btn_list) == 2:
        keyboard.row(btn_list[1], btn_list[0])
    elif len(btn_list) == 1:
        keyboard.row(btn_list[0])
    btn_close = telebot.types.InlineKeyboardButton(text=const.CLOSE,
                                                   callback_data="cancel")
    keyboard.row(btn_close)
    return keyboard


# генерация массива с датами
def create_date_list():
    sales_list = database.get_sales_data()
    date_list = []
    for i in range(len(sales_list)):
        date = sales_list[i][0]
        if date not in date_list:
            date_list.append(date)
    dates = []
    for i in date_list:
        date = datetime.strptime(i, "%d/%m/%Y")
        if date not in dates:
            dates.append(date)
    dates.sort()

    global date_sort
    date_sort = []
    for date in dates:
        date_str = f"{date.day}/{date.month}/{date.year}"
        date_sort.append(date_str)


# клавиатура с категориями
def get_categories(method):
    keyboard = telebot.types.InlineKeyboardMarkup()
    categories = database.get_categories()

    length = len(categories)

    b = True
    if length > 0:
        for i in range(length):
            keyboard.add(telebot.types.InlineKeyboardButton(
                text=str(categories[i][1]), callback_data=f"{method}{str(categories[i][0])}"))
    else:
        b = False

    return keyboard, b


# клавиатура с подкатегориями
def get_subcategories(method, category):
    keyboard = telebot.types.InlineKeyboardMarkup()
    subcat = database.get_subcategorys(category)

    count = False

    for i in range(len(subcat)):
        if method == "subitem_add=":
            on_click = method + str(subcat[i][0])
        else:
            on_click = method + f"{str(subcat[i][0])}|{str(category)}"

        keyboard.add(
                telebot.types.InlineKeyboardButton(text=subcat[i][1], callback_data=on_click))
        count = True


    return keyboard, count


# заполнить клавиатуру товарами
def get_items(keyboard, category, sub_category, delete):
    items = database.get_items(category, sub_category)
    count = False

    if not delete:
        method = "selected_item="
    else:
        method = "del_it="

    for i in range(len(items)):
        name_item = str(items[i][1])
        if not delete:
            price_item = str(items[i][3])
            count_item = str(items[i][6])

            if count_item == "file":
                item_str = f"{name_item} {price_item}руб."
            else:
                item_str = f"{name_item} {price_item}руб. ({count_item} шт.)"
        else:
            item_str = f"{name_item}"

        keyboard.add(
            telebot.types.InlineKeyboardButton(text=item_str, callback_data=f"{method}{name_item}"))
        count = True


    return keyboard, count


# генерация клавиатуры покупки
def create_buy_buttons(method_buy, method_back):
    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.add(telebot.types.InlineKeyboardButton(text="💰 Купить", callback_data=method_buy))
    keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK, callback_data=method_back))

    return keyboard


# генерация клавиатуры с оплатой и проверкой
def create_check_buttons(method_url, method_check, method_back):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="💳 Оплатить", url=method_url))
    keyboard.add(telebot.types.InlineKeyboardButton(text="🔄 Проверка оплаты", callback_data=method_check))
    keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK, callback_data=method_back))

    return keyboard


# отправка сообщений админам
def send_admin_mes(msg):
    for i in range(len(admin.ADMIN_ID)):
        bot.send_message(admin.ADMIN_ID[i], msg)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    call_data = call.data.split("=")

    # Главное меню
    if call_data[0] == "main_menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, count = get_categories("select_category=")
        if count:
            bot.send_message(call.message.chat.id, "📂 Доступные категории", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, "😔 В данный момент товары отсутствуют")

    # Выбранная категория
    elif call_data[0] == "select_category":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, count = get_subcategories("subcat=", call_data[1])

        keyboard, item = get_items(keyboard, call_data[1], "", False)

        keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK, callback_data="main_menu"))

        if count is True or item is True:
            bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             "😔 В данный момент товары отсутствуют", reply_markup=keyboard)

    # Подкатегория
    elif call_data[0] == "subcat":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        categories = call_data[1].split("|")

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard, count = get_items(keyboard, categories[1], categories[0], False)

        keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                        callback_data=f"select_category={str(categories[1])}"))
        if count:
            bot.send_message(call.message.chat.id, "📙 Доступные товары", reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id,
                             "😔 В данный момент товары отсутствуют", reply_markup=keyboard)

    # Выбранный предмет
    elif call_data[0] == "selected_item":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        item = database.get_item(call_data[1])

        keyboard = telebot.types.InlineKeyboardMarkup()

        if str(item[5]) == "":
            method_back = f"select_category={str(item[4])}"
        else:
            method_back = f"subcat={str(item[5])}|{str(item[4])}"

        if item[6] != 0 or item[6] == "file":
            method_buy = f"buy_item={str(item[1])}"

            keyboard = create_buy_buttons(method_buy, method_back)

            bot.send_message(call.message.chat.id,
                             string_help.get_info_message(str(item[1]), str(item[2]), str(item[3]), str(item[6])),
                             reply_markup=keyboard, parse_mode="HTML")
        else:
            keyboard.add(telebot.types.InlineKeyboardButton(
                text=const.BACK, callback_data=method_back))
            bot.send_message(call.message.chat.id, "😔 Извините, но данного товара сейчас нет в наличии",
                             reply_markup=keyboard)

    # Покупка
    elif call_data[0] == "buy_item":
        bot.delete_message(call.message.chat.id, call.message.message_id)

        if not qiwi.check_available():
            bot.send_message(call.message.chat.id,
                             "😔 Извините, но оплата на данный момент не работает \n Приносим свои извинения")
            send_admin_mes("❗ Не работает оплата через *QIWI* ❗")
            return

        num = qiwi.num
        item = database.get_item(call_data[1])

        item_id = item[0]
        item_name = item[1]
        item_price = item[3]
        count = item[6]

        comment, qiwi_url = qiwi.create_key(item_price)

        if count == "file" or count > 0:
            message_pay = string_help.get_buy_message(item_name, num, comment, item_price)

            selected_item = f"selected_item={item_name}"

            if item_id is None:
                item_id = database.get_item(call_data[1])[0]

            check = f"check-pay={comment}|{item_id}"

            keyboard = create_check_buttons(qiwi_url, check, selected_item)
            bot.send_message(call.message.chat.id, message_pay, reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, "😔 Извините, но данного товара сейчас нет в наличии")

    # Проверка оплаты
    elif call_data[0] == "check-pay":
        data = call_data[1].split("|")
        comment = data[0]

        item = database.get_item_by_id(data[1])

        item_name = item[1]
        item_id = database.get_item_id(item_name)
        item_price = item[3]
        count = item[6]

        is_buy_item = qiwi.payment_ver(comment, item_price)

        if is_buy_item:
            not_received = qiwi.received_item(call.message.chat.id, item_id)

            if not_received:
                item_data = database.get_item_data(item_id)
                date = datetime.now()
                day = date.day
                month = date.month
                year = date.year
                format_date = f"{day}/{month}/{year}"

                database.input_info_buy(call.message.chat.id, item_name, item_id,
                                        comment, item_price, item_data, count, format_date)

                msg = string_help.get_sold_message(call.message.chat.username, item_name, item_price)
                if count == "file":
                    bot.send_document(call.message.chat.id,
                                      open(item_data, "rb"),
                                      caption=f"✨ Поздравляем вас с приобретением {item_name} \n")
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f"✨ Поздравляем вас с приобретением {item_name} \n"
                                               f"🎁 Данные товара:\n*{item_data}*")
                    msg += f"\n🔹 Данные: {item_data}"

                send_admin_mes(msg)
            else:
                bot.send_message(call.from_user.id, "❗ Ваша покупка не найдена или была выдана ❗")
        else:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text="❗ Пополнение не найдено ❗\n Попробуйте еще раз")

    # Обращение в поддержку
    elif call_data[0] == "support_user":
        global theme_support
        theme_support = call_data[1]
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✏ Введите текст обращения")
        bot.register_next_step_handler(call.message, send_support)

    # # # # # # # # #
    # Админ Команды
    # Категории
    elif call_data[0] == "category":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call_data[1] == "new_category":
            bot.send_message(call.message.chat.id, "📁 Введите название категории\n*Одна категория - Одна строка*")
            bot.register_next_step_handler(call.message, new_category)
        else:
            global main_category
            main_category = call_data[1]
            keyboard, b = get_subcategories("subitem_add=", main_category)

            keyboard.add(telebot.types.InlineKeyboardButton(text="📚 Добавить товар",
                                                            callback_data=f"add_item={str(main_category)}"))
            bot.send_message(call.message.chat.id,
                             "📕 Выберите подкатегорию для товара \nИли можете добавить его в данную категорию",
                             reply_markup=keyboard)

    # Добавление подкатегорий
    elif call_data[0] == "sub_cat_add":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        global sub_category

        keyboard = telebot.types.InlineKeyboardMarkup()
        sub = ""

        sub_cat = database.get_subcategorys(call_data[1])
        for i in range(len(sub_cat)):
            sub += f"▪ {sub_cat[i][1]}\n"

        keyboard.add(telebot.types.InlineKeyboardButton(
            text="📝 Добавить новую подкатегорию", callback_data=f"new_subcategory={call_data[1]}"))

        bot.send_message(call.message.chat.id,
                         f"📂 Доступные подкатегории \n{sub}", reply_markup=keyboard)

    # Добавление подкатегории
    elif call_data[0] == "new_subcategory":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        global subcategory_for
        subcategory_for = call_data[1]

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "📁 Введите название подкатегории\n"
                                               "*Одна подкатегория - Одна строка*")
        bot.register_next_step_handler(call.message, new_subcategory)


    # Добавление товара
    # В подкатегорию
    elif call_data[0] == "subitem_add":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        sub_cat = call_data[1]
        sub_category = sub_cat

        bot.send_message(call.message.chat.id, "📚 Введите название товара")
        bot.register_next_step_handler(call.message, add_item_name)

    # В категорию
    elif call_data[0] == "add_item":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        sub_category = ""

        bot.send_message(call.message.chat.id, "📚 Введите название товара")
        bot.register_next_step_handler(call.message, add_item_name)

    # Удаление товара/категории
    # Выбор категории где удалить товар
    # вывод всех категорий
    elif call_data[0] == "all_cat_del":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, b = get_categories("cat_del=")

        bot.send_message(call.message.chat.id, "📚 Выберите категорию товара", reply_markup=keyboard)

    # выбрана категория
    elif call_data[0] == "cat_del":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, b = get_subcategories("del_it_sub=", call_data[1])
        keyboard, count = get_items(keyboard, call_data[1], "", True)

        keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                        callback_data="all_cat_del="))
        bot.send_message(call.message.chat.id, "📙 Выберите товар\категорию", reply_markup=keyboard)

    # выбрана подкатегория
    elif call_data[0] == "del_it_sub":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()

        categories = call_data[1].split("|")

        keyboard, count = get_items(keyboard, categories[1], categories[0], True)
        keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                        callback_data="cat_del=" + str(categories[1])))
        bot.send_message(call.message.chat.id, "📙 Выберите товар для удаления", reply_markup=keyboard)

    # Удаление выбранного товара
    elif call_data[0] == "del_it":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.YES, callback_data=f"del_item={call_data[1]}"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.NO, callback_data="main_menu"))

        bot.send_message(call.message.chat.id, f"❓ Удалить товар *{call_data[1]}*❓", reply_markup=keyboard)
    elif call_data[0] == "del_item":
        bot.delete_message(call.message.chat.id, call.message.message_id)

        database.delete_item(call_data[1])
        bot.send_message(call.message.chat.id, f"❗ Товар *{call_data[1]}* удален")

    # Удаление категории
    elif call_data[0] == "categ_del":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard, b = get_subcategories("!del_subcat=", call_data[1])
        keyboard.add(telebot.types.InlineKeyboardButton(text="🚫 Удалить всю категорию",
                                                        callback_data=f"!del_cat={str(call_data[1])}"))
        bot.send_message(call.message.chat.id, "📁 Выберите категорию", reply_markup=keyboard)

    # удаление категории
    elif call_data[0] == "!del_cat":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()

        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.YES, callback_data=f"del_cat={call_data[1]}"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.NO, callback_data="cancel"))

        bot.send_message(call.message.chat.id, f"❓ Удалить категорию *{database.get_category(call_data[1])}*❓ \n"
                                               "*Будут удалены ВСЕ ТОВАРЫ в данной категории*", reply_markup=keyboard)
    elif call_data[0] == "del_cat":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        category = database.get_category(call_data[1])
        database.delete_category(call_data[1])
        bot.send_message(call.message.chat.id, f"❗ Категория *{category}* удалена")

    # Удаление подкатегории
    elif call_data[0] == "!del_subcat":
        cat = call_data[1].split("|")

        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        sub_cat = database.get_subcategory(cat[0])
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.YES, callback_data=f"del_subcat={call_data[1]}"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=const.NO, callback_data="cancel"))

        bot.send_message(call.message.chat.id, f"❓ Удалить категорию *{sub_cat}*❓ \n"
                                               "*Будут удалены ВСЕ ТОВАРЫ в данной категории*", reply_markup=keyboard)
    elif call_data[0] == "del_subcat":
        bot.delete_message(call.message.chat.id, call.message.message_id)

        cat = call_data[1].split("|")
        c = database.get_category(cat[1])
        sc = database.get_subcategory(cat[0])
        database.delete_subcategory(cat[0], cat[1])
        bot.send_message(call.message.chat.id, f"❗ Категория *{sc}* удалена")

    # Ответ на обращение
    elif call_data[0] == "ans_sup":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        global chat_id_answer
        chat_id_answer = call_data[1]

        bot.send_message(call.message.chat.id, "✏ Напишите ответ")
        bot.register_next_step_handler(call.message, send_support_answer)

    # Удалить обращение
    elif call_data[0] == "del_sup":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        database.delete_support(call_data[1])

    # редактировать сообщение поддержки
    elif call_data[0] == "edit_supmes":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "📝 Введите сообщение")
        bot.register_next_step_handler(call.message, edit_sup_mes)

    # след страница отчета
    elif call_data[0] == "get_report":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = create_report_keyboard(call_data[1])
        bot.send_message(call.message.chat.id, "📆 Выберите дату отчета", reply_markup=keyboard)

    # обработка отчета
    elif call_data[0] == "report":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        temp = call_data[1].split("|")

        data = database.get_sales_info_day(temp[0])
        msg = f"📆 Отчет за {temp[0]}\n\n"

        buyer_list = []
        sum = 0
        for i in range(len(data)):
            buyer = data[i][0]
            if buyer not in buyer_list:
                msg += f"➖ {buyer}\n"
                for j in range(len(data)):
                    if data[j][0] == buyer:
                        msg += f"  ▪ {data[j][1]} : {data[j][4]} руб.\n"
                        sum += int(data[j][4])
                buyer_list.append(buyer)
            else:
                continue

        msg += f"\n💰 Прибыль: {sum} руб."

        keyboard.add(telebot.types.InlineKeyboardButton(text=const.BACK,
                                                        callback_data=f"get_report={temp[1]}"))
        keyboard.add(telebot.types.InlineKeyboardButton(text=const.CLOSE,
                                                        callback_data="cancel"))

        bot.send_message(call.message.chat.id, msg, reply_markup=keyboard)

    # Кошельки
    elif call_data[0] == "payment":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="🔄 Проверить доступность",
                                                        callback_data=f"check={call_data[1]}"))
        keyboard.add(telebot.types.InlineKeyboardButton(text="✏ Изменить кошелек",
                                                        callback_data=f"edit={call_data[1]}"))
        if call_data[1] == "qiwi":
            bot.send_message(call.message.chat.id, "🥝 QIWI-Кошелек", reply_markup=keyboard)

    # Проверка кошельков
    elif call_data[0] == "check":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call_data[1] == "qiwi":
            if qiwi.check_available():
                bot.send_message(call.message.chat.id, "✅ Кошелек доступен")
            else:
                bot.send_message(call.message.chat.id, "❗ Кошелек не доступен, измените токен ❗")

    # Редактирование кошельков
    elif call_data[0] == "edit":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call_data[1] == "qiwi":
            bot.send_message(call.message.chat.id, "✏ Введите номер кошелька")
            bot.register_next_step_handler(call.message, qiwi_payment)

    # Отмена
    elif call_data[0] == "cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)

# FAQ
def edit_faq(message):
    if const.not_const(message.text):
        database.input_faq(message.text)
        bot.send_message(message.from_user.id, "ℹ FAQ успешно обновлен")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Рассылка
@async_dec()
def create_sending(message):
    user_list = database.get_user_list()

    sending_text = message.text
    all_send_mes = 0
    limit = 0

    if const.not_const(message.text):
        for i in range(len(user_list)):
            try:
                if limit <= 20:
                    bot.send_message(user_list[i][0], sending_text)
                    limit += 1
                    all_send_mes += 1
                else:
                    limit = 0
                    time.sleep(2)
            except:
                continue

        bot.send_message(message.from_user.id, string_help.get_text_send(all_send_mes))
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return

# сообщения в поддержку
def get_support_messages(message, state):
    appeals = database.get_support_mes(state)
    length = len(appeals)

    if int(length) > 0:
        counter = 0
        for i in range(length):
            if counter <= 20:
                mes = f"🔹 ID Пользователя: <b>{appeals[i][1]}</b>\n" \
                      f"🔹 Тип обращения: {appeals[i][3]}\n" \
                      f"🔹 Сообщение: {appeals[i][2]}\n"

                keyboard = telebot.types.InlineKeyboardMarkup()
                btn_delete = telebot.types.InlineKeyboardButton(text="🗑 Удалить",
                                                                callback_data=f"del_sup={str(appeals[i][0])}")
                if state is False:
                    ans_sup = f"ans_sup={appeals[i][0]}"
                    keyboard.add(telebot.types.InlineKeyboardButton(text="✏ Ответить",
                                                                    callback_data=ans_sup))
                    btn_1 = telebot.types.InlineKeyboardButton(text="📦 Отложить", callback_data="cancel")
                    keyboard.row(btn_1, btn_delete)
                else:
                    mes += f"🔹 Ответ:\n {appeals[i][6]}"

                    keyboard.row(btn_delete)

                bot.send_message(message.from_user.id, mes, reply_markup=keyboard, parse_mode="HTML")
                counter += 1
            else:
                counter = 0
                time.sleep(2)

    else:
        bot.send_message(message.from_user.id, "🚫 Обращений не найдено")


# Текст обращения в поддержку
def send_support(message):
    if const.not_const(message.text):
        if message.text is not None:
            id_user = message.chat.id
            support_mess = message.text
            support_theme = theme_support

            database.send_appeal(id_user, support_mess, support_theme)

            msg = "❗ *Обращение в поддержку*\n" \
                  f"🔹 ID Пользователя: *{message.from_user.username}*\n" \
                  f"🔹 Тип обращения: {support_theme}\n" \
                  f"🔹 Сообщение: {support_mess}"

            send_admin_mes(msg)

            bot.send_message(message.from_user.id,
                             "✅ Ваше обращение было доставлено\n⏲Ждите ответа в ближайшее время")
        else:
            bot.send_message(message.from_user.id, "❗ Обращение не может быть пустым ❗")
            return
    else:
        bot.send_message(message.from_user.id, "❗ Обращение не может содержать в себе названия кнопок ❗")
        return

# Ответ на обращение
def send_support_answer(message):
    id_chat = chat_id_answer

    if const.not_const(message.text):
        answer = str(message.text)
        user_id = database.send_appeal_answer(id_chat, answer)
        mes = f"✅ Ваше обращение было рассмотрено: \n\n" + answer

        bot.send_message(user_id, mes)
        send_admin_mes(f"{message.chat.username} ответил на запрос от {user_id} \n{answer}")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return

# сообщение поддержки
def edit_sup_mes(message):
    msg = str(message.text)

    if const.not_const(msg):
        database.input_sup_mes(msg)
        bot.send_message(message.from_user.id, "✅ Сообщение обновлено")
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Кошельки
# QIWI
def qiwi_payment(message):
    if const.not_const(message.text):
        global qiwi_number
        qiwi_number = message.text

        bot.send_message(message.from_user.id, "✏ Введите токен QIWI")
        bot.register_next_step_handler(message, qiwi_token_payment)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# токен
def qiwi_token_payment(message):
    bot.send_message(message.from_user.id, "🔎 Проверка кошелька...")
    try:
        bot.delete_message(message.chat.id, message.message_id)
        qiwi_update = qiwi.check_available_data(message.text, qiwi_number)
        if qiwi_update:
            database.input_qiwi(message.text, qiwi_number)
            bot.send_message(message.from_user.id, "🔐 Токен был успешно изменен!")
        else:
            bot.send_message(message.from_user.id, "❗ Неверный токен ❗")

    except:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.from_user.id, "❗ Ошибка токена ❗")


# Добавление категории / подкатегории
# Категория
def new_category(message):
    global main_category
    main_category = str(message.text)

    cat_list = main_category.split("\n")
    count = 0

    for i in range(len(cat_list)):
        if not database.get_category_name(cat_list[i]) and const.not_const(cat_list[i]):
            database.input_category(cat_list[i])
            count += 1

    bot.send_message(message.from_user.id, string_help.get_text_cat(count))


# Подкатегория
def new_subcategory(message):
    sub_category = str(message.text)
    subcat_for = subcategory_for

    sub_list = sub_category.split("\n")

    count = 0
    for i in range(len(sub_list)):
        if not database.get_subcat_name(sub_list[i]) and const.not_const(sub_list[i]):
            database.input_subcategory(sub_list[i], subcat_for)

            count += 1

    bot.send_message(message.from_user.id, string_help.get_text_cat(count))


# Добавление товара
# Название
def add_item_name(message):
    global name
    name = message.text
    if const.not_const(name):
        bot.send_message(message.from_user.id, "✏ Введите описание товара")
        bot.register_next_step_handler(message, add_item_desc)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Описание
def add_item_desc(message):
    global desc
    desc = message.text
    if const.not_const(desc):
        bot.send_message(message.from_user.id, "💵 Введите стоимость товара (в рублях)")
        bot.register_next_step_handler(message, add_item_price)
    else:
        bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
        return


# Цена
def add_item_price(message):
    global price

    try:
        price = int(message.text)
        if const.not_const(price):
            bot.send_message(message.from_user.id, "🔐 Введите данные товара \n*Один товар - Одна строка* \n"
                                                   "💾 Или же загрузите архив или файл с товаром")
            bot.register_next_step_handler(message, add_item_data)
        else:
            bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
            return
    except Exception:
        bot.send_message(message.from_user.id, "❗ Ошибка при вводе ❗")
        bot.send_message(message.from_user.id, "💵 Введите стоимость товара (в рублях)")
        bot.register_next_step_handler(message, add_item_price)


# Данные товаров
def add_item_data(message):
    name_item = name
    desc_item = desc
    price_item = price
    category_item = main_category

    try:
        subcategory_item = sub_category
    except Exception:
        subcategory_item = ""

    if message.document is not None:
        # архив
        try:
            file_info = bot.get_file(message.document.file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()

            folder = f"items"
            if not os.path.exists(folder):
                os.mkdir(folder)

            src = f"{folder}/{message.document.file_name}"
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
        except:
            bot.send_message(message.from_user.id, "❗ Ошибка при загрузке ❗")
            return

        database.input_item_file(name_item, desc_item, price_item, subcategory_item, category_item, src)

        bot.send_message(message.from_user.id, "📦 Товар был добавлен")
    else:
        # текст
        global data
        data = str(message.text)
        data_list = data.split("\n")

        if const.not_const(data_list):
            count = len(data_list)
            database.input_item(name_item, desc_item, price_item, subcategory_item, category_item, data_list)

            bot.send_message(message.from_user.id, string_help.get_text_itmes(count))
        else:
            bot.send_message(message.from_user.id, "❗ Неправильный формат данных ❗")
            return


# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            print("Бот запущен!")
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(5)
