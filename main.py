import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import psycopg
from pgsql import save_user, get_user

#создаем соединение с СУБД. заменить на свои данные. Предварительно создать базу и таблицы в субд.
pg_server = 'postgresql://pyvkbot:pyvkbot@10.168.88.113:5432/py_vk_bot'
conn = psycopg.connect(pg_server)


def get_tokens(file_name):
    with open(file_name, 'r') as f:
        tokens = json.load(f)
    return tokens


def send_some_msg(id, some_text):
    gvk_session.method("messages.send", {"user_id": id, "message": some_text, "random_id": 0})


def show_kbd(id):
    gvk_session.method("messages.send", {"user_id": id, "message": 'Вот клавиатура', "keyboard": keyboard.get_keyboard(), "random_id": 0})


def get_user_bio(id):
    user_data = gvk_session.method("users.get", {"user_ids": id, "fields": "sex, bdate, city, country"})
    return user_data


def search_users(sex, city, offset, age=18):
    if sex == 1:
        sex = 2
    else:
        sex = 1
    result = vk_session.method("users.search", {"sort": 0, "offset": offset, "city": city['id'], "sex": sex, "age": age, "limit": 20, "fields": "sex, bdate, city, country"})
    return result

#file format {"app": "app_token", "group": "group_token"}
tokens = get_tokens('tokens')
vk_session = vk_api.VkApi(token=tokens['app'])
gvk_session = vk_api.VkApi(token=tokens['group'])
gsession_api = gvk_session.get_api()
glongpool = VkLongPoll(gvk_session)


keyboard = VkKeyboard(one_time=False)
keyboard.add_button('Начать', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Выключить', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button('Предыдущий', color=VkKeyboardColor.NEGATIVE)
keyboard.add_button('Следующий', color=VkKeyboardColor.POSITIVE)


for event in glongpool.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            udata = get_user_bio(id)[0]
            save_user(udata, conn)
            if msg == "hi":
                send_some_msg(id, "Hi friend!")
            elif msg == 'начать':
                result = search_users(udata['sex'], udata['city'], 0)
                for user in result['items']:
                    save_user(user, conn)
            elif msg == 'сохранить':
                exit()
            else:
                show_kbd(id)