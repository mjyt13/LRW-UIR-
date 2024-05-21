import telebot
import sqlite3
from telebot import types


bot = telebot.TeleBot('')


@bot.message_handler(content_types=['video', 'photo', 'sticker'])
def delete_message(message):
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Пока что функционал заключается в том, чтобы вывести предполагаемый долг')


@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('по предметам')
    btn2 = types.KeyboardButton('по фамилиям')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, f"{message.from_user.first_name}"
                                      f" {message.from_user.last_name} , попробуем вывести кнопки"
                     , reply_markup=markup)

"""
def onclick(message):
    if message.text == 'по фамилиям':
        inter_surnames = print_surname()
        surnames = ''
        for surname in inter_surnames:
            surnames += surname
            surnames += '\n'
        bot.send_message(message.chat.id, surnames)

    if message.text == 'по предметам':
        inter_subjects = print_subject()
        subjects = ''
        for subject in inter_subjects:
            subjects += subject
            subjects += '\n'
        bot.send_message(message.chat.id, subjects)
    
"""

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
def get_data(message):
    if message.text.lower() == 'по фамилиям':
        inter_surnames = print_surname()
        surnames = ''
        for surname in inter_surnames:
            surnames += surname
            surnames += '\n'
        bot.send_message(message.chat.id, surnames,reply_markup=types.ReplyKeyboardRemove())
    elif message.text.lower() == 'по предметам':
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
