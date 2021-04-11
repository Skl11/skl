import sqlite3
from datetime import datetime

import gonal_strings as str_help

DATABASE = "shop.sqlite"

# подключится к БД
def connect_db():
    return sqlite3.connect(DATABASE)

class ShopDB:

    def __init__(self):
        connect_db()
        self.open_db()

    # открыть базу данных
    def open_db(self):
        with connect_db() as db:
            cur = db.cursor()

            # Товары
            try:
                cur.execute("SELECT * FROM Items")
                print("БД 'Товары' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE Items("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "name TEXT, "
                            "desc TEXT, "
                            "price INT, "
                            "category TEXT, "
                            "subCategory TEXT, "
                            "data TEXT)")
                print("БД 'Товары' создана")

            # Товары (Кол-во)
            try:
                cur.execute("SELECT * FROM ItemsCount")
                print("БД 'Товары Кол-во' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE ItemsCount("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "name TEXT, "
                            "desc TEXT, "
                            "price INT, "
                            "category TEXT, "
                            "subCategory TEXT, "
                            "count INT)")
                print("БД 'Товары Кол-во' создана")

            # Категории
            try:
                cur.execute("SELECT * FROM Category")
                print("БД 'Категории' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE Category("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "category TEXT)")
                print("БД 'Категории' создана")

            # Подкатегории
            try:
                cur.execute("SELECT * FROM SubCategory")
                print("БД 'Подкатегории' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE SubCategory("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "name_subcat TEXT, "
                            "main_category TEXT)")
                print("БД 'Подкатегории' создана")

            # FAQ
            try:
                cur.execute("SELECT * FROM Faq")
                print("БД 'FAQ' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE Faq("
                            "help TEXT)")
                row = cur.fetchone()
                if row is None:
                    cur.execute("DROP TABLE Faq")
                    cur.execute("CREATE TABLE Faq("
                                "help TEXT)")
                    cur.execute("INSERT INTO Faq VALUES(?)",
                                ("✒Пример FAQ для вашего магазина\nВы можете изменить его в главном меню "
                                 "\n`Разработано GonalInc`",))
                    print("БД 'FAQ' созданна")
                else:
                    print("БД 'FAQ' созданна")
            # Кошельки
            ## Qiwi
            try:
                cur.execute("SELECT * FROM Qiwi")
                print("БД 'Qiwi' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE Qiwi("
                            "number TEXT, "
                            "token TEXT)")
                row = cur.fetchone()
                if row is None:
                    cur.executemany("INSERT INTO Qiwi(number, token) "
                                    "VALUES (?, ?)", [("number", "token")])
                    print("БД 'Qiwi' создана")
                else:
                    print("БД 'Qiwi' создана")

            # Список покупателей
            try:
                cur.execute("SELECT * FROM Sales")
                print("БД 'Продажи' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE Sales("
                            "user TEXT,"
                            "item TEXT, "
                            "item_ID TEXT,"
                            "comment TEXT, "
                            "price TEXT, "
                            "data TEXT,"
                            "time TEXT)")
                print("БД 'Продажи' создана")

            # Обращения в поддержку
            try:
                cur.execute("SELECT * FROM SupportMes")
                print("БД 'Обращения' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE SupportMes("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "chatID TEXT, "
                            "message TEXT, "
                            "type TEXT, "
                            "state TEXT,"
                            "time TEXT,"
                            "answer TEXT)")
                print("БД 'Обращения' создана")

            try:
                cur.execute("SELECT * FROM SupportAdmin")
                print("БД 'Сообщение Поддержки' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE SupportAdmin("
                            "message TEXT)")
                cur.execute("INSERT INTO SupportAdmin VALUES (?)",
                            (
                                "✒ Пример сообщения поддержки, которое показывается пользователям\nЕго можно изменить в меню",))
                print("БД 'Сообщение Поддержки' работает")

            # Список всех пользователей
            try:
                cur.execute("SELECT * FROM UserList")
                print("БД 'Пользователи' работает")
            except sqlite3.OperationalError:
                cur.execute("CREATE TABLE UserList(chatID TEXT)")
                print("БД 'Пользователи' создана")

    # список пользователей
    def get_user_list(self):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM UserList")

        return cur.fetchall()

    # список категорий
    def get_categories(self):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Category")

        return cur.fetchall()

    # получить категорию
    def get_category(self, id):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Category WHERE id = ?", [id])

        return cur.fetchall()[0][1]

    def get_subcategory(self, id):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM SubCategory WHERE id = ?", [id])

        return cur.fetchall()[0][1]

    # присутствие категории
    def get_category_name(self, category):
        with connect_db() as db:
            cur = db.cursor()
            data = cur.execute("SELECT * FROM Category WHERE category = ?", [category]).fetchall()
            if len(data) > 0:
                return True
            else:
                return False

    # присутствие подкатегории
    def get_subcat_name(self, name):
        appended = False
        with connect_db() as db:
            cur = db.cursor()
            data = cur.execute("SELECT * FROM SubCategory WHERE name_subcat = ?", [name]).fetchall()
            if len(data) > 0:
                return True
            else:
                return False

    # FAQ
    def get_faq(self):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Faq")

        return cur.fetchall()

    # обращения в поддержку
    def get_support_mes(self, state):
        if state:
            s = "✅ Отвечено"
        else:
            s = "❌ Не отвечено"

        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM SupportMes WHERE state = ?", [s])

        return cur.fetchall()

    # сообщение поддержки
    def get_support_main_mes(self):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM SupportAdmin")

        return cur.fetchone()

    # подкатегории в подкатегории
    def get_subcategorys(self, category):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM SubCategory WHERE main_category = ?", [category])

        return cur.fetchall()

    # предметы в категории и в подкатегории
    def get_items(self, category, sub_cat):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM ItemsCount WHERE category = ? AND subCategory = ?", (category, sub_cat))

        return cur.fetchall()

    # предмет по имени
    def get_item(self, name):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM ItemsCount WHERE name = ?", [name])

        return cur.fetchone()

    # предмет по id
    def get_item_by_id(self, id):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM ItemsCount WHERE id = ?", [id])

        return cur.fetchone()

    # id товара
    def get_item_id(self, name):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Items WHERE name = ?", [name])
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                else:
                    id = row[0]
                    break
        return id

    # все покупки
    def get_sales(self):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Sales")

        return cur.fetchall()

    # покупка пользователя с id товара
    def get_sale_id(self, user, item_id):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Sales WHERE user = ? AND item_ID = ?",
                        (user, item_id))
            return cur.fetchall()


    # даты покупок
    def get_sales_data(self):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT time FROM Sales")

        return cur.fetchall()


    # информация о покупках за день
    def get_sales_info_day(self, date):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Sales WHERE time = ?", [date])

        return cur.fetchall()

    # данные товара
    def get_item_data(self, id):
        with connect_db() as db:
            cur = db.cursor()
            item_list = cur.execute("SELECT * FROM Items WHERE id = ?", [id]).fetchall()

        return str(item_list[0][6])

    # получить киви данные
    def get_qiwi(self, key):
        # 0 - номер
        # 1 - токен
        with connect_db() as db:
            cur = db.cursor()
            data = cur.execute("SELECT * FROM Qiwi").fetchall()[0][key]

        return data

    # добавить категорию
    def input_category(self, name):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("INSERT INTO Category (category) VALUES (?)", [name])

    # добавить подкатегорию
    def input_subcategory(self, name, main_category):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("INSERT INTO SubCategory (name_subcat, main_category) VALUES (?, ?)",
                        (name, main_category))

    # добавление товара в виде файла
    def input_item_file(self, name, desc, price, subcategory, category, file_path):
        with connect_db() as db:
            cur = db.cursor()
            if not self.is_available_item(name):
                cur.execute(
                    "INSERT INTO ItemsCount (name, desc, price, subCategory, category, count) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, desc, price, subcategory, category, "file"))

                cur.execute(
                    "INSERT INTO Items (name, desc, price, subCategory, category, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, desc, price, subcategory, category, file_path))
            else:
                data = self.get_item(name)
                if len(data) > 0:
                    cur.execute("UPDATE Items SET data = ? WHERE name = ?", (file_path, name))

    # добавление товара
    def input_item(self, name, desc, price, subcategory, category, data_list):
        count = len(data_list)
        with connect_db() as db:
            cur = db.cursor()
            if not self.is_available_item(name):
                # если не существует
                cur.execute(
                    "INSERT INTO ItemsCount (name, desc, price, subCategory, category, count) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, desc, price, subcategory, category, count))

                for i in range(count):
                    cur.execute(
                        "INSERT INTO Items (name, desc, price, subCategory, category, data) VALUES (?, ?, ?, ?, ?, ?)",
                        (name, desc, price, subcategory, category, data_list[i]))
            else:
                # если существует
                data = self.get_item(name)

                item_desc = data[2]
                item_price = data[3]
                item_cat = data[4]
                item_subcat = data[5]
                item_count = data[6]

                new_count = count + item_count

                for i in range(count):
                    cur.execute(
                        "INSERT INTO Items (name, desc, price, subCategory, category, data) VALUES (?, ?, ?, ?, ?, ?)",
                        (name, item_desc, item_price, item_subcat, item_cat, data_list[i]))

                cur.execute("UPDATE ItemsCount SET count = ? WHERE name = ?", (new_count, name))

    # проверка на существование товара
    def is_available_item(self, name):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM ItemsCount WHERE name = ?", (name,))

            is_available = False
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                if row[6] >= 0:
                    is_available = True
                    break

        return is_available

    # занесение данных, когда совершилась покупка
    def input_info_buy(self, user_id, item_name, item_id, comment, item_price, item_data, is_file, time):
        with connect_db() as db:
            cur = db.cursor()
            # Занесение покупателя в БД
            cur.executemany(
                "INSERT INTO Sales(user, item, item_ID, comment, price, data, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(user_id, item_name, item_id, comment, item_price, item_data, time)])

            # Получение кол-ва товара
            list_item = self.get_item(item_name)
            count = list_item[6]

            if is_file != "file":
                # Удаление товара
                cur.execute("DELETE FROM Items WHERE id = ?", [item_id])
                # Вычитание 1 товара из БД
                count = count - 1
                cur.execute("UPDATE ItemsCount SET count = ? WHERE name = ?", (count, item_name))

    # добавление пользователя в список
    def input_user(self, id):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM UserList WHERE chatID = ?", [id])
            row = cur.fetchall()
            if len(row) == 0:
                cur.execute("INSERT INTO UserList (chatID) VALUES (?)", [id])

    # сообщение поддержки
    def input_sup_mes(self, msg):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM SupportAdmin")
            row = cur.fetchone()

            cur.execute("UPDATE SupportAdmin SET message = ? WHERE message = ?", (msg, row[0]))

    # изменить FAQ
    def input_faq(self, text):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Faq")
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                cur.execute("UPDATE Faq SET help = ? WHERE help = ?", (text, row[0]))

    # добавить киви данные
    def input_qiwi(self, token, number):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM Qiwi")
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                old_num = row[0]
                cur.execute("UPDATE Qiwi SET number = ?, token = ? WHERE number = ?",
                            (number, token, old_num))

    # отправка обращения
    def send_appeal(self, id_user, message, theme):
        with connect_db() as db:
            cur = db.cursor()

            now = datetime.now()
            now_date = str_help.get_time_format()
            cur.execute("INSERT INTO SupportMes (chatID, message, type, state, time, answer) VALUES (?, ?, ?, ?, ?, ?)",
                        (id_user, message, theme, "❌ Не отвечено", now_date, ""))

    # отправка ответа на обращение
    def send_appeal_answer(self, id_chat, answer):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM SupportMes WHERE id = ?", (id_chat,))
            row = cur.fetchone()

            cur.execute("UPDATE SupportMes SET state = ? WHERE id = ?", ("✅ Отвечено", id_chat))
            cur.execute("UPDATE SupportMes SET answer = ? WHERE id = ?", (answer, id_chat))

        return row[1]

    # удалить товар
    def delete_item(self, name):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("DELETE FROM Items WHERE name = ?", [name])
            cur.execute("DELETE FROM ItemsCount WHERE name = ?", [name])

    # удалить категорию
    def delete_category(self, category):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("DELETE FROM Category WHERE id = ?", [category])
            cur.execute("DELETE FROM SubCategory WHERE main_category = ?", [category])
            cur.execute("DELETE FROM Items WHERE category = ?", [category])
            cur.execute("DELETE FROM ItemsCount WHERE category = ?", [category])

    # удалить подкатегорию
    def delete_subcategory(self, main_cat, sub_cat):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("DELETE FROM SubCategory WHERE id = ? AND main_category = ?", (main_cat, sub_cat))
            cur.execute("DELETE FROM ItemsCount WHERE subCategory = ? AND category = ?", (main_cat, sub_cat))
            cur.execute("DELETE FROM Items WHERE subCategory = ? AND category = ?", (main_cat, sub_cat))

    # удалить обращение
    def delete_support(self, id):
        with connect_db() as db:
            cur = db.cursor()
            cur.execute("DELETE FROM SupportMes WHERE id = ?", [id])
