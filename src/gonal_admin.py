import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["token"]
get_id = config["settings"]["admin_id"]
COMMENT_PAY = config["settings"]["comment_pay"]
ADMIN_ID = []

if "," in get_id:
    get_id = get_id.split(",")
    for a in get_id:
        ADMIN_ID.append(str(a))
else:
    try:
        ADMIN_ID = [str(get_id)]
    except ValueError:
        ADMIN_ID = [0]
        print("Не указан Admin_ID")

def is_admin(user):
    return str(user) in ADMIN_ID
