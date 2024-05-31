import telebot
import sqlite3
from telebot import types


bot = telebot.TeleBot('')


@bot.message_handler(content_types=['video', 'photo', 'sticker'])
def delete_message(message):
    bot.delete_message(message.chat.id, message.message_id)


# здесь обозначено то, что происходит при запуске работы с ботом юзера
# + команда mode, чтоб можно было вернуться к этому без очистки диалога
@bot.message_handler(commands=['start','mode'])
def start(message):
    # обозначить кнопки выбора режима работы
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('студент')
    btn2 = types.KeyboardButton('куратор')
    btn3 = types.KeyboardButton('работник деканата')
    # btn4 = types.KeyboardButton('преподаватель')
    # собрать их и вывести
    markup.row(btn1, btn2,btn3)
    # отправить сообщение с преждесобранными кнопками
    bot.send_message(message.chat.id, 'Приветствуем. Выберите режим просматривающего/редактирующего',
                     reply_markup=markup)
    # !!! ВОТ! команда, позволяющая связывать функции. Принцип ясен:
    # в первой связываемой функции есть команда, второй аргумент которой - вторая связываемая функция
    bot.register_next_step_handler(message,after_start)

# связываемая функция выведения кнопок(кнопки просто позволяют юзеру
# своими потными пальчиками вводить определенный текст
def after_start(message):
    if message.text == 'работник деканата':
        bot.send_message(message.chat.id,"Введите пароль")
        # структура неизменна во всех ответвлениях, разнятся лишь вторые связываемые функции
        bot.register_next_step_handler(message, dekanat_autentification)

    if message.text == 'куратор':
        bot.send_message(message.chat.id,"Введите пароль")
        # кстати, так можно отделить куратора и работника деканата - используйте разные фунции
        bot.register_next_step_handler(message, kurator_autentification)

    if message.text == 'студент':
        bot.send_message(message.chat.id,"Введите фамилию для проверки текущих долгов")
        bot.register_next_step_handler(message, after_student)


def after_student(message):
    # у студента пока заглушка
    bot.send_message(message.chat.id,"вы студент")


def dekanat_autentification(message):
    # здесь уже видна попытка в аутентификацию
    # было бы здорово это переработать в цикл
    if message.text == "пароль":
        bot.send_message(message.chat.id, "Отлично")
        bot.register_next_step_handler(message, after_dekanat)
    else:
        bot.send_message(message.chat.id, "dekanat неверный пароль")


def kurator_autentification(message):
    # а вот самое крутое - куратор(ибо больше всего наполнения)
    if message.text == "parol":

        bot.send_message(message.chat.id, "Хорошо")
        # это задел на выбор конкретного предмета
        markup = types.ReplyKeyboardMarkup()
        btns =[]
        btn1 = types.KeyboardButton('Просмотреть список должников')
        btn2 = types.KeyboardButton('поугрожать упырю о долге')
        btn3 = types.KeyboardButton('изменить запись')
        btns.append(btn1); btns.append(btn2); btns.append(btn3)
        # выводятся кнопки через массив
        for btn in btns:
            markup.row(btn)
        bot.send_message(message.chat.id, 'Выберите команду',reply_markup=markup)
        bot.register_next_step_handler(message, after_kurator)
    else:
        bot.send_message(message.chat.id, "kurator неверный пароль")


def after_dekanat(message):
    # ещё одна заглушка
    bot.send_message(message.chat.id,"tak vi dekanator")


def after_kurator(message):
    # функции куратора(было бы неплохо спросить Анастасию Петровну
    # на предмет работы с должниками - а чёё там есть
    if message.text == 'Просмотреть список должников':
        get_data(message,1)
    if message.text == 'поугрожать упырю о долге':
        pass# тут типа команда внесения в ещё несозданный столбик какого-нибудь мата
    if message.text == 'изменить запись':
        pass # тут запрос на изменение


# функция админа... БЕЗ АУТЕНТИФИКАЦИИ)))
@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('по предметам')
    btn2 = types.KeyboardButton('по фамилиям')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, f"{message.from_user.first_name}"
                                      f" {message.from_user.last_name} , попробуем вывести кнопки"
                     , reply_markup=markup)

# функция вывода фамилий должников
def print_surname():
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    debtors = []
    surnames = []
    for row in cur.execute("SELECT fullname, study_group, subject, desc FROM debtors ORDER BY subject"):
        debtors.append(row)
    for note in debtors:
        if not (note in surnames):
            surnames.append(note[0])
    conn.close()
    return surnames


# функция вывода предметов и описаний
def print_subject():
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    debtors = []
    subjects = []
    for row in cur.execute("SELECT fullname, study_group, subject, desc FROM debtors ORDER BY subject"):
        debtors.append(row)
    for note in debtors:
        subjects.append(note[2])
        subjects.append(note[3])
    conn.close()
    return subjects


@bot.message_handler()
def get_data(message,number):
    if number==1:
        inter_surnames = print_surname()
        surnames = ''
        for surname in inter_surnames:
            surnames += surname
            surnames += '\n'
        bot.send_message(message.chat.id, surnames,reply_markup=types.ReplyKeyboardRemove())
    elif number==2:
        inter_subjects = print_subject()
        subjects = ''
        for i in range(0,len(inter_subjects),2):
            subjects += inter_subjects[i]
            subjects += " : "
            subjects += inter_subjects[i+1]
            subjects += '\n'
        bot.send_message(message.chat.id, subjects,reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.delete_message(message.chat.id, message.message_id)


bot.infinity_polling()
