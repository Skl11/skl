import random

import requests

database = None
comment = ""

class Qiwi:
    def __init__(self):
        self.num = ""
        self.token = ""
        self.update()

    def update(self):
        self.num = database.get_qiwi(0)
        self.token = database.get_qiwi(1)

    # генерация ключа оплаты
    def create_key(self, price):
        key_pass = list("1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm")
        random.shuffle(key_pass)
        key_buy = "".join([random.choice(key_pass) for i in range(12)])

        com = f"{comment}:{key_buy}.{price}"

        url = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={self.num}&amountInteger={price}&amountFraction=0&extra%5B%27comment%27%5D={com}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

        return f"{com}", url

    # проверка оплаты
    def payment_ver(self, comment, price):
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + self.token
        params_get = {"rows": 10, "operation": "IN"}
        qiwi_get = request.get(
            f"https://edge.qiwi.com/payment-history/v2/persons/{self.num}/payments",
            params=params_get)
        qiwi_get = qiwi_get.json()["data"]

        is_buy_item = False

        comment_qiwi = []
        amount_qiwi = []
        curensy_qiwi = []

        for i in range(len(qiwi_get)):
            # обработка последних 10 платежей
            comment_qiwi.append(qiwi_get[i]["comment"])
            amount_qiwi.append(qiwi_get[i]["sum"]["amount"])
            curensy_qiwi.append(qiwi_get[i]["sum"]["currency"])

        for j in range(len(comment_qiwi)):
            # проверка если оплата присутсвует
            if str(comment) in str(comment_qiwi[j]) and str(price) == str(amount_qiwi[j]) and str(
                    curensy_qiwi[j]) == "643":
                is_buy_item = True
                break

        return is_buy_item

    # получен ли предмет
    def received_item(self, user_id, id_item):
        is_received = True

        sale = database.get_sale_id(user_id, id_item)
        if len(sale) > 0:
            is_received = False

        return is_received

    # доступен ли кошелек
    def check_available(self):
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + self.token
        param = {"rows": 5, "operation": "IN"}
        qiwi_Get = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{self.num}/payments",
                               params=param)

        if qiwi_Get.status_code == 200:
            return True
        else:
            return False

    # доступен ли кошелек (с параметрами)
    def check_available_data(self, token, number):
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + token
        parameters = {"rows": 5, "operation": "IN"}
        qiwi_Get = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{number}/payments",
                               params=parameters)

        if qiwi_Get.status_code == 200:
            return True
        else:
            return False
