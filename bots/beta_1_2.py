import telebot
import webbrowser
import sqlite3
from telebot import types

bot = telebot.TeleBot('')


def get_sticker(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('кнопка пилотка', url='https://studio.youtube.com/channel/'
                                                            'UC5uBvzduav7zPojDQ0Ydqyw/analytics/'
                                                            'tab-overview/period-default')
    markup.row(btn1)
    bot.reply_to(message, 'Ты что наделал 2...', reply_markup=markup)


@bot.message_handler(content_types=['video','photo','sticker'])
def get_media(message):
    bot.delete_message(message.chat.id, message.message_id)



@bot.message_handler(commands=['start'])
def main(message):
    connexion = sqlite3.connect('debtlist.sql')
    curx = connexion.cursor()
    curx.execute('CREATE TABLE IF NOT EXISTS users(id int auto_increment primary key, name varchar(50), passw varchar(50))')
    connexion.commit()
    curx.close()
    connexion.close()

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('долги')
    markup.row(btn1)
    bot.send_message(message.chat.id, 'Пока что функционал заключается в том, чтобы вывести предполагаемый долг'
                     , reply_markup=markup)
    bot.register_next_step_handler(message, onclick)


def onclick(message):
    if message.text == 'долги':
        username = message.from_user.first_name
        userpassw = message.from_user.last_name
        connexion = sqlite3.connect('debtlist.sql')
        curx = connexion.cursor()

        curx.execute(f"INSERT INTO users(name, passw) VALUES ('%s','%s')" % (username, userpassw))
        connexion.commit()
        curx.close()
        connexion.close()


@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, f"Сверка, полагаю. Ты ведь не {message.from_user.first_name}"
                                      f" {message.from_user.last_name} ?")

@bot.message_handler(commands=['list'])
def list(message):
    bot.send_message(message.chat.id,"Щас вам всё покажу")
    connexion = sqlite3.connect('debtlist.sql')
    curx = connexion.cursor()

    curx.execute('SELECT * FROM users')
    userlist = curx.fetchall()

    info = ''
    for element in userlist:
        info += f'Имena: {element[1]}, Esche Imena: {element[2]}\n'
    curx.close()
    connexion.close()

    bot.send_message(message.chat.id,info)


@bot.message_handler(commands=['here'])
def main(message):
    bot.send_message(message.chat.id, 'Кто так научил говорить тебя: "здеся"? Здесь!')


@bot.message_handler(text=['долги'])
def main(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} {message.from_user.last_name}\n'
                                      f',<b>И Я ВЕРНУЛСЯ</b>', 'html')


@bot.message_handler()
def not_care(message):
    if message.text.lower() == 'vvvv':
        bot.reply_to(message, f'{message.from_user.first_name} {message.from_user.last_name}\n')
    elif message.text.lower() == 'я пивас':
        bot.send_message(message.chat.id, "я тоже, лови объяснение метода нового храма")
        webbrowser.open("https://gofman39.narod.ru/Igor23.html")
    elif message.text.lower() == 'вычислительная математика':
        conn = sqlite3.connect("list_1_21.db")
        cur = conn.cursor()
        debtors=[]
        for row in cur.execute("SELECT fullname, subject FROM debtlist ORDER BY subject"):
            debtors.append(row)
        for note in debtors:
            if note[1].lower() == 'вычислительная математика':
                bot.send_message(message.chat.id, note[0])
        conn.close()
    else:
        bot.send_message(message.chat.id, "Это не то,что мне нужно")


bot.infinity_polling()
