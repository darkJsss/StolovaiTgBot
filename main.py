import requests
import telebot as tg
from telebot import types

from config import TOKEN

bot = tg.TeleBot(TOKEN)
users = {}
Add_dish = 0
Set_dish = 0
Del_dish = 0
Schools_list = requests.get(f'https://12447695.pythonanywhere.com/api/schools').json()
Schools_list_ids = list(str(i["id"]) for i in Schools_list)


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
    if str(message.text) in Schools_list_ids:
        pass
        return

    bot.send_message(message.from_user.id, "Такого кода школы нет")
    bot.register_next_step_handler(message, send_send)


bot.polling(none_stop=True, interval=0)
