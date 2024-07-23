import requests
import telebot as tg
from telebot import types

from config import TOKEN

bot = tg.TeleBot(TOKEN)
Choose_School_Count = False
Id_School = None
U_School_Admin = False
Add_dish = 0
Set_dish = 0
Del_dish = 0
Schools_list = requests.get(f'https://12447695.pythonanywhere.com/api/schools')
Schools_list = Schools_list.json()
Schools = dict()
for i, j, j1 in Schools_list:
    Schools[i] = [j, j1]

@bot.message_handler(commands=['start'])
def start(message):
    global Choose_School_Count
    Choose_School_Count = False
    bot.send_message(message.from_user.id, "Здравствуйте", reply_markup=types.ReplyKeyboardRemove(),
                     parse_mode='Markdown')
    bot.send_message(message.from_user.id, "найдите и напишите уникальный айди вашей школы в нашем каталоге")
    for i, j in Schools.items():
        bot.send_message(message.from_user.id, i + ": " + j[0])


@bot.message_handler(commands=['admin'])
def Input_Admin_Password(message):
    global U_School_Admin
    if Choose_School_Count:
        s = str(message.text)
        s = s[6:]
        s = s.strip()
        if s == Schools[Id_School][1]:
            bot.send_message(message.from_user.id, "Вы Админ")
            U_School_Admin = True
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton("Все меню")
            button2 = types.KeyboardButton("меню на Сегодня")
            button3 = types.KeyboardButton("Расписание всех классов")
            button4 = types.KeyboardButton("Добавить новое блюдо в меню")
            button5 = types.KeyboardButton("Изменить блюдо в меню")
            button6 = types.KeyboardButton("Удалить блюдо из меню")
            markup.add(button1, button2, button3, button4, button5, button6)
            bot.send_message(message.from_user.id, "Для вас открылся доступ к нескольким кнопкам", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "Сначала нужно выбрать школу")


@bot.message_handler(content_types=['text'])
def Choose_School(message):
    global Choose_School_Count, Id_School
    global Add_dish, Set_dish, Del_dish
    tg_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if str(message.text) in Schools.keys() and Choose_School_Count is False:
        Choose_School_Count = True
        Id_School = str(message.text).strip()
        button1 = types.KeyboardButton("Все меню")
        button2 = types.KeyboardButton("меню на Сегодня")
        button3 = types.KeyboardButton("Расписание всех классов")
        markup.add(button1, button2, button3)
        bot.send_message(message.from_user.id, "Для вас открылся доступ к нескольким кнопкам", reply_markup=markup)
    elif Choose_School_Count is False:
        bot.send_message(message.from_user.id, "Вы ошиблись с айди попробуйте заново")
    elif str(message.text) == "Все меню" and Choose_School_Count:
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{Id_School}')
        r = r.json()
        for i, j in r.items():
            bot.send_message(message.from_user.id, str(i) + ": " + str(j))
    elif str(message.text) == "меню на Сегодня" and Choose_School_Count:
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{Id_School}/now')
        r = r.json()
        for i, j in r.items():
            bot.send_message(message.from_user.id, str(i) + ": " + str(j))
    elif str(message.text) == "Расписание всех классов" and Choose_School_Count:
        pass  # хз т.к api нет, а хранить
        pass  # на соб. ноуте не собираюсь слишком долго будет при чем админ не сможет вносить правки
    elif str(message.text) == "Добавить новое блюдо в меню" and Choose_School_Count and U_School_Admin:
        bot.send_message(message.from_user.id, "Напишите в одну строчку через пробел")
        bot.send_message(message.from_user.id, "название блюда, его цену,")
        bot.send_message(message.from_user.id, "а также если оно сегодня есть в меню напишите 1 если нет то 0")
        Add_dish = 1
    elif str(message.text) == "Изменить блюдо в меню" and Choose_School_Count and U_School_Admin:
        bot.send_message(message.from_user.id, "Напишите в одну строчку через пробел")
        bot.send_message(message.from_user.id, "название блюда которое вы хотите изменить, его новую цену,")
        bot.send_message(message.from_user.id, "а также если оно сегодня есть в меню напишите 1 если нет то 0")
        Set_dish = 1
    elif str(message.text) == "Удалить блюдо из меню" and Choose_School_Count and U_School_Admin:
        bot.send_message(message.from_user.id, "Напишите в одну строчку название блюда, которого вы хотите удалить")
        Del_dish = 1
    elif Add_dish == 1:
        s = str(message.text)
        s.split()
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{Id_School}/add/{s[0]}/{s[1]}/{s[2]}')
        bot.send_message(message.from_user.id, "блюдо было успешно добавлено")
        Add_dish = 0
    elif Set_dish == 1:
        s = str(message.text)
        s.split()
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{Id_School}/set/{s[0]}/{s[1]}/{s[2]}')
        bot.send_message(message.from_user.id, "блюдо было успешно изменино")
        Set_dish = 0
    elif Del_dish == 1:
        s = str(message.text)
        s = s.strip()
        r = requests.get(f'https://12447695.pythonanywhere.com/api/dishes/{Id_School}/del/{s}')
        bot.send_message(message.from_user.id, "блюдо было успешно удалено")
        Del_dish = 0


bot.polling(none_stop=True, interval=0)
