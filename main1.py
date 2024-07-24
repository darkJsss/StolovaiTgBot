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
        "Dish": {},
        "Markup": None
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
        users[user_id]["Choose_School_Count"] = True
        users[user_id]["Id_School"] = str(message.text)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Все меню")
        button2 = types.KeyboardButton("Меню на сегодня")
        button3 = types.KeyboardButton("Расписание всех классов")
        markup.add(button1, button2, button3)
        users[user_id]["Markup"] = markup
        bot.send_message(message.from_user.id, f"Вы присоединились к", reply_markup=markup)
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
            users[user_id]["Markup"] = markup
            bot.send_message(message.from_user.id, "Для вас открылся доступ к админ панели", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def Choose_School(message):
    user_id = message.from_user.id
    user_condition = users[user_id]
    if str(message.text) == "Все меню":
        dishes = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{user_condition["Id_School"]}').json()
        text = ""
        for i in dishes:
            text += f"{i['name']} - {i['count']} руб. \n"
        bot.send_message(message.from_user.id, text)
    elif str(message.text) == "Меню на сегодня":
        dishes = requests.get(
            f'https://12447695.pythonanywhere.com/api/dishes/{user_condition["Id_School"]}/now').json()
        bot.send_message(message.from_user.id, 'Все блюдо на сегодня')
        text = ""
        for i in dishes:
            text += f"{i['name']} - {i['count']} руб. \n"
        bot.send_message(message.from_user.id, text)
    elif str(message.text) == "Расписание всех классов":
        pass
    elif str(message.text) == "Добавить новое блюдо в меню" and user_condition["U_School_Admin"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Отмена")
        markup.add(button)

        bot.send_message(message.from_user.id, "Напишите название блюда", reply_markup=markup)
        bot.register_next_step_handler(message, Add_dish_name)
    elif str(message.text) == "Изменить блюдо в меню" and user_condition["U_School_Admin"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Отмена")
        markup.add(button)

        bot.send_message(message.from_user.id, "Напишите в одну строчку через пробел подряд")
        bot.send_message(message.from_user.id, "Название блюда которое вы хотите изменить, его новую цену,")
        bot.send_message(message.from_user.id, "А также если оно сегодня есть в меню напишите 'Да' если нет, то 'Нет'")
        bot.register_next_step_handler(message, Set_dish)
    elif str(message.text) == "Удалить блюдо из меню" and user_condition["U_School_Admin"]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Отмена")
        markup.add(button)

        bot.send_message(message.from_user.id, "Напишите название блюда, которого вы хотите удалить")
        bot.register_next_step_handler(message, Del_dish)


def Add_dish_name(message):
    if str(message.text).strip() == "Отмена":
        close_dish(message)
        return
    user_id = message.from_user.id
    users[user_id]["Dish"]["Name"] = str(message.text).strip()

    bot.send_message(message.from_user.id, "Напишите цену блюда")
    bot.register_next_step_handler(message, Add_dish_count)


def Add_dish_count(message):
    if str(message.text).strip() == "Отмена":
        close_dish(message)
        return
    user_id = message.from_user.id
    users[user_id]["Dish"]["Count"] = int(str(message.text).strip())

    bot.send_message(message.from_user.id, f"Напишите \"Да\", если блюдо есть в наличии, или \"Нет\", если нет")
    bot.register_next_step_handler(message, Add_dish_isHere)


def Add_dish_isHere(message):
    if str(message.text).strip() == "Отмена":
        close_dish(message)
        return

    isHere = 0
    if str(message.text).strip().lower() == "да":
        isHere = 1
    elif str(message.text).strip().lower() == "нет":
        isHere = 0
    else:
        bot.send_message(message.from_user.id, "Неверный формат")
        bot.register_next_step_handler(message, Add_dish_isHere)

    user_id = message.from_user.id
    requests.get(
        f'https://12447695.pythonanywhere.com/api/dishes'
        f'/{users[user_id]["Id_School"]}/add/{users[user_id]["Dish"]["Name"].capitalize()}/{users[user_id]["Dish"]["Count"]}/{isHere}')
    bot.send_message(message.from_user.id, "Блюдо было успешно добавлено", reply_markup=users[user_id]["Markup"])


def close_dish(message):
    user_id = message.from_user.id
    bot.send_message(message.from_user.id, "Вы отменили редактирование блюда", reply_markup=users[user_id]["Markup"])


def Set_dish(message):
    user_id = message.from_user.id
    s = str(message.text).strip().split()
    requests.get(
        f'https://12447695.pythonanywhere.com/api/dishes'
        f'/{users[user_id]["Id_School"]}/set/{s[0].capitalize()}/{s[1]}/{s[2]}')
    bot.send_message(message.from_user.id, "Блюдо было успешно изменино")


def Del_dish(message):
    user_id = message.from_user.id
    s = str(message.text)
    s = s.strip()
    requests.get(
        f'https://12447695.pythonanywhere.com/api/dishes'
        f'/{users[user_id]["Id_School"]}/del/{s.capitalize()}')
    bot.send_message(message.from_user.id, "Блюдо было успешно удалено")


bot.polling(none_stop=True, interval=0)
