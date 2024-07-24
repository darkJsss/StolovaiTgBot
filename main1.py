import requests
import telebot as tg
from telebot import types

from config import TOKEN

bot = tg.TeleBot(TOKEN)
users = {}
Schools_list = requests.get(f'https://12447695.pythonanywhere.com/api/schools').json()
Schools_list_ids = list(str(i["id"]) for i in Schools_list)
Schools_list_passwords = list(str(i["password"]) for i in Schools_list)


@bot.message_handler(commands=['start'])
def start(message):
    global users
    user_id = message.from_user.id
    users[user_id] = {
        "Choose_School_Count": False,
        "Id_School": None,
        "U_School_Admin": False,
    }
    bot.send_message(message.from_user.id, "Здравствуйте", reply_markup=types.ReplyKeyboardRemove(),
                     parse_mode='Markdown')
    bot.send_message(message.from_user.id, "найдите и напишите уникальный айди вашей школы в нашем каталоге")
    text = ""
    for i in Schools_list:
        text += f'{i["id"]} - {i["name"]}\n'
    bot.send_message(message.from_user.id, text)

    bot.register_next_step_handler(message, send_send)


def send_send(message):
    user_id = message.from_user.id
    global users
    if str(message.text) in Schools_list_ids:
        users[user_id] = {
            "Choose_School_Count": True,
            "Id_School": str(message.text),
            "U_School_Admin": False,
        }
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Все меню")
        button2 = types.KeyboardButton("Меню на сегодня")
        button3 = types.KeyboardButton("Расписание всех классов")
        markup.add(button1, button2, button3)
        bot.send_message(message.from_user.id, "Для вас открылся доступ к нескольким кнопкам", reply_markup=markup)
        return
    bot.send_message(message.from_user.id, "Такого кода школы нет")
    bot.register_next_step_handler(message, send_send)


@bot.message_handler(commands=['admin'])
def Input_Admin_Password(message):
    global users
    user_id = message.from_user.id
    user_condition = users[user_id]
    if user_condition["Choose_School_Count"]:
        s = str(message.text)
        s = s[6:]
        s = s.strip()
        if s in Schools_list_passwords and users[user_id]["Id_School"] == Schools_list_ids[
            Schools_list_passwords.index(s)]:
            bot.send_message(message.from_user.id, "Вы Админ")
            users[user_id]["U_School_Admin"] = True
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("Все меню")
            button2 = types.KeyboardButton("Меню на сегодня")
            button3 = types.KeyboardButton("Расписание всех классов")
            button4 = types.KeyboardButton("Добавить новое блюдо в меню")
            button5 = types.KeyboardButton("Изменить блюдо в меню")
            button6 = types.KeyboardButton("Удалить блюдо из меню")
            markup.add(button1, button2, button3, button4, button5, button6)
            bot.send_message(message.from_user.id, "Для вас открылся доступ к нескольким кнопкам", reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, "Вы ввели неправильный пароль")


@bot.message_handler(content_types=['text'])
def Choose_School(message):
    user_id = message.from_user.id
    user_condition = users[user_id]
    if str(message.text) == "Все меню":
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{user_condition["Id_School"]}').json()
        for i in r:
            s = i['count']
            s1 = i['isHere']
            if s1:
                s1 = 'в наличии на сегодня'
            else:
                s1 = 'не в наличии на сегодня'
            s2 = i['name']
            bot.send_message(message.from_user.id, f' {s2} - {s} руб. - {s1}')
    elif str(message.text) == "Меню на сегодня":
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{user_condition["Id_School"]}/now').json()
        bot.send_message(message.from_user.id, 'Все блюдо на сегодня')
        for i in r:
            s = i['count']
            s2 = i['name']
            bot.send_message(message.from_user.id, f'{s2} - {s} руб.')
    elif str(message.text) == "Расписание всех классов":
        pass
    elif str(message.text) == "Добавить новое блюдо в меню" and user_condition["U_School_Admin"]:
        bot.send_message(message.from_user.id, "Напишите в одну строчку через пробел подряд")
        bot.send_message(message.from_user.id, "Название блюда, его цену,")
        bot.send_message(message.from_user.id, "А также если оно сегодня есть в меню напишите 'Да' если нет, то 'Нет'")
        bot.register_next_step_handler(message, Add_dish)
    elif str(message.text) == "Изменить блюдо в меню" and user_condition["U_School_Admin"]:
        bot.send_message(message.from_user.id, "Напишите в одну строчку через пробел подряд")
        bot.send_message(message.from_user.id, "Название блюда которое вы хотите изменить, его новую цену,")
        bot.send_message(message.from_user.id, "А также если оно сегодня есть в меню напишите 'Да' если нет, то 'Нет'")
        bot.register_next_step_handler(message, Set_dish)
    elif str(message.text) == "Удалить блюдо из меню" and user_condition["U_School_Admin"]:
        bot.send_message(message.from_user.id, "Напишите в одну строчку подряд")
        bot.send_message(message.from_user.id, "Название блюда, которого вы хотите удалить")
        bot.register_next_step_handler(message, Del_dish)


def Add_dish(message):
    user_id = message.from_user.id
    s = str(message.text)
    s = s.strip()
    s = s.split()
    r = requests.get(
        f'https://12447695.pythonanywhere.com/api/dishes/{users[user_id]["Id_School"]}/add/{s[0].capitalize()}/{s[1]}/{s[2]}')
    bot.send_message(message.from_user.id, "Блюдо было успешно добавлено")
    bot.send_message(message.from_user.id, "Если вы прямо сейчас хотите отменить действие напишите 'Да'")
    bot.send_message(message.from_user.id, "Если же вы не хотите отменить действие напишите 'Нет'")
    bot.register_next_step_handler(message, Cancel_Add_dish)


def Set_dish(message):
    user_id = message.from_user.id
    s = str(message.text)
    s = s.strip()
    s = s.split()
    r = requests.get(
        f'https://12447695.pythonanywhere.com/api/dishes/{users[user_id]["Id_School"]}/set/{s[0].capitalize()}/{s[1]}/{s[2]}')
    bot.send_message(message.from_user.id, "Блюдо было успешно изменино")
    bot.send_message(message.from_user.id, "Если вы прямо сейчас хотите отменить действие напишите 'Да'")
    bot.send_message(message.from_user.id, "Если же вы не хотите отменить действие напишите 'Нет'")
    bot.register_next_step_handler(message, Cancel_Set_dish)

def Del_dish(message):
    user_id = message.from_user.id
    s = str(message.text)
    print(s)
    s = s.strip()
    r = requests.get(
        f'https://12447695.pythonanywhere.com/api/dishes/{users[user_id]["Id_School"]}/del/{s.capitalize()}')
    bot.send_message(message.from_user.id, "Блюдо было успешно удалено")
    bot.send_message(message.from_user.id, "Если вы прямо сейчас хотите отменить действие напишите 'Да'")
    bot.send_message(message.from_user.id, "Если же вы не хотите отменить действие напишите 'Нет'")
    bot.register_next_step_handler(message, Cancel_Del_dish)


def Cancel_Add_dish(message):
    user_id = message.from_user.id
    s = str(message).lower()
    s = s.strip()
    if s == "да":
        pass


def Cancel_Set_dish(message):
    user_id = message.from_user.id
    s = str(message).lower()
    s = s.strip()
    if s == "да":
        pass


def Cancel_Del_dish(message):
    user_id = message.from_user.id
    s = str(message).lower()
    s = s.strip()
    if s == "да":
        pass


bot.polling(none_stop=True, interval=0)