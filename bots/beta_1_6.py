import telebot
import sqlite3
from telebot import types

"""Итак, телеграм бот учёта должников beta 1.6,. Здесь есть: аутентификация преподавателя и куратора, возможность
 просмотреть долги по фамилии(студенту), просмотреть должников группы(куратор), прокомментировать текущую
  задолженность(куратор), создать новую запись о задолженности(куратор)"""

bot = telebot.TeleBot('')
message_dict = {}
subjects_dict ={}
groups_dict = {}

"""боту не нужны картинки, видео и стикеры - удалит"""
@bot.message_handler(content_types=['video', 'photo', 'sticker'])
def delete_message(message):
    bot.delete_message(message.chat.id, message.message_id)


# здесь обозначено то, что происходит при запуске работы с ботом юзера
# + команда mode, чтоб можно было вернуться к этому без очистки диалога
@bot.message_handler(commands=['start', 'mode'])
def start(message):
    # обозначить кнопки выбора режима работы
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('студент')
    btn2 = types.KeyboardButton('куратор')
    btn3 = types.KeyboardButton('преподаватель')
    # собрать их и вывести
    markup.row(btn1, btn2, btn3)
    # отправить сообщение с преждесобранными кнопками
    bot.send_message(message.chat.id, 'Приветствуем. Выберите режим просматривающего/редактирующего',
                     reply_markup=markup)
    # !!! ВОТ! команда, позволяющая связывать функции. Принцип ясен:
    # в первой связываемой функции есть команда, второй аргумент которой - вторая связываемая функция
    bot.register_next_step_handler(message, after_start)


# связываемая функция выведения кнопок(кнопки просто позволяют юзеру
# своими потными пальчиками выбирать определенный режим без ввода текста
def after_start(message):
    # структура неизменна во всех ответвлениях, разнятся лишь вторые связываемые функции
    if message.text == 'преподаватель':
        bot.send_message(message.chat.id, "Введите пароль")
        bot.register_next_step_handler(message, teacher_autentification)

    if message.text == 'куратор':
        bot.send_message(message.chat.id, "Введите пароль")
        bot.register_next_step_handler(message, kurator_autentification)

    if message.text == 'студент':
        # неплохо бы добавить ещё функций студентам
        bot.send_message(message.chat.id, "Введите фамилию для проверки текущих долгов")
        bot.register_next_step_handler(message, print_debts)

# аутентификация преподавателя
def teacher_autentification(message):
    # связаться с базой данных паролей
    conn = sqlite3.connect("passwords.db")
    cur = conn.cursor()
    # обратиться к таблице паролей преподавателей
    # и установление флажка прохождения аутентификации
    correct = False
    quantity = 0
    subjects=[]
    # пройти по базе данных с помощью селекта одной записи
    for row in cur.execute("SELECT password, subject FROM teacher_passwords"):
        # сверить с введённым пользователем текстом
        if message.text == row[0]:
            # если да, то вынести в словарь дисциплин предмет, преподаваемый текущим юзером
            subjects_dict[(message.chat.id, quantity)] = row[1]
            correct = True
            quantity += 1
    # закрыть базу данных
    conn.close()
    if correct:
        # оповещение и переброс
        bot.send_message(message.chat.id, "успешный вход")
        teacher_inter(message)
        subjects_dict[message.chat.id] = quantity
        for i in range(0,quantity):
            subjects.append(subjects_dict[(message.chat.id, i)])
        print(f"user {message.chat.username} is the teacher, subjects are {subjects}")
    else:
        # то же самое
        bot.send_message(message.chat.id,"неправильный пароль")
        start(message)


def kurator_autentification(message):
    """if message.text == "parol":
        print("user "+message.chat.username+" is kurator")
        kurator_inter(message)
    else:
        bot.send_message(message.chat.id, "kurator неверный пароль")
        start(message)"""
    # здесь присоединение к базу данных паролей
    conn = sqlite3.connect("passwords.db")
    cur = conn.cursor()
    # и установление флажка прохождения аутентификации
    correct = False
    # пройти по базе данных с помощью селекта одной записи
    for row in cur.execute("SELECT password, stgroup FROM kurator_passwords"):
        # если пароль верный, то установить значение флажка True и вынести зна
        if message.text == row[0]:
            groups_dict[message.chat.id] = row[1]
            correct = True
    # закрыть базу данных
    conn.close()
    # проверить флажок, здесь ещё кнопки - рудимент, которым я пытался остановить поток бреда
    if correct:
        markup = types.ReplyKeyboardMarkup()
        markup.add("Продолжить",row_width=2)
        print(f"user {message.chat.username} is the kurator, subject is {groups_dict[message.chat.id]}")
        bot.send_message(message.chat.id, 'успешный вход', reply_markup=markup)
        bot.register_next_step_handler(message,kurator_inter)
    # по назначению
    else:
        bot.send_message(message.chat.id, "неправильный пароль")
        start(message)
def kurator_inter(message):
    # вывести конпки функций для куратора
    markup = types.ReplyKeyboardMarkup()
    btns = []
    btn1 = types.InlineKeyboardButton('Просмотреть список должников')
    btn2 = types.InlineKeyboardButton('прокомментировать существующую задолженность')
    btn3 = types.InlineKeyboardButton('создать долг')
    btns.append(btn1)
    btns.append(btn2)
    btns.append(btn3)
    # выводятся кнопки через массив
    for btn in btns:
        markup.row(btn)
    print(message.text)
    bot.send_message(message.chat.id, 'Выберите команду', reply_markup=markup)
    bot.register_next_step_handler(message, after_kurator)


def teacher_inter(message):
    markup = types.ReplyKeyboardMarkup()
    btns = []
    btn1 = types.InlineKeyboardButton('Просмотреть список должников по предмету')
    btn2 = types.InlineKeyboardButton('Создать запись о задолженности')
    btn3 = types.InlineKeyboardButton('Удалить запись о задолженности')
    btn4 = types.InlineKeyboardButton('Изменить запись о задолженности')
    btns.append(btn1)
    btns.append(btn2)
    btns.append(btn3)
    btns.append(btn4)
    # выводятся кнопки через массив
    for btn in btns:
        markup.row(btn)
    print(message.text)
    bot.send_message(message.chat.id, 'Выберите команду', reply_markup=markup)
    bot.register_next_step_handler(message, after_teacher)


def after_student(message):
    # у студента пока заглушка
    bot.send_message(message.chat.id, "Введите фамилию для сверки задолженностей")
    bot.register_next_step_handler(message, print_debts)


def after_kurator(message):
    # на предмет работы с должниками - а чёё там есть
    if message.text == 'Просмотреть список должников':
        print("user " + message.chat.username + " (kurator) is looking at list of debtors")
        # начнётся просмотр списка должников группы, к которой приставлен куратор
        get_debtors_kurator(message, 1)
    if message.text == 'прокомментировать существующую задолженность':
        print("user " + message.chat.username + " (kurator) is ready to comment")
        # запустится цепочка для внесения комментария относительно текущего долга
        # её желательно не прерывать
        choose_debtor_kurator(message)
    if message.text == 'создать долг':
        print("user "+ message.chat.username + " (kurator) is ready to create a debt note")
        create_debtor_kurator(message)
        # тут начнётся последовательность выполнения функций для создания записи долге, которую делает Куратор
    if message.text == "":
        print("empty")
        kurator_inter(message)

def after_teacher(message):
    if message.text == "Просмотреть список должников по предмету":
        print(f"user {message.chat.username} is looking at subject debtors")
        choose_subject_teacher(message,"look")
    if message.text == "Создать запись о задолженности":
        print(f"user {message.chat.username} is creating subject debt")
        choose_subject_teacher(message,"create")
    if message.text == "Удалить запись о задолженности":
        print(f"user {message.chat.username} is deleting subject debt")
        choose_subject_teacher(message, "delete")
    if message.text == "Изменить запись о задолженности":
        print(f"user {message.chat.username} is editing subject debt")
        choose_subject_teacher(message,"edit")


@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/start')
    markup.row(btn1)
    bot.send_message(message.chat.id, "бот отображает задолженности студента по фамилии\n"
                     + "бот пишет комментарии к долгам с помощью куратора\n"
                     + "бот создаёт долг с помощью куратора/деканатора"
                     , reply_markup=markup)


# функция возврата фамилий должников
def debts_surnames():
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    debtors = []
    surnames = []
    for row in cur.execute("SELECT fullname, study_group, subject, desc FROM debtors ORDER BY subject"):
        debtors.append(row)
    for note in debtors:
        if not (note in surnames):
            surnames.append((note[0],note[1]))
    conn.close()
    return surnames


# функция возврата предметов и описаний(не используется)
def debts_subjects():
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


# функция возврата долгов по фамилии
def get_debts_by_surname(surname):
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()

    i = 0
    debts = []
    details = []
    # будемо выводить:
    # фамилию, группу, предмет, описание задолженности и комментарии(пока что только от куратора)
    for row in cur.execute("SELECT fullname, study_group, subject, desc, comments FROM debtors ORDER BY fullname"):
        if surname in row[0]:
            details.append(row[1])
            details.append(row[2])
            details.append(row[3])
            details.append(row[4])
        debts.append(details.copy())
        details.clear()

    while i < len(debts):
        if len(debts[i]) == 0:
            debts.pop(i)
        else:
            i += 1
    return debts

def get_debts_by_subject(subject):
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()

    i = 0
    debts = []
    details = []
    # будемо выводить:
    # фамилию, группу, предмет, описание задолженности и комментарии(пока что только от куратора)
    for row in cur.execute("SELECT fullname, study_group, subject, desc, comments FROM debtors ORDER BY fullname"):
        # если есть совпадение введенного предмета и предмета в базе данных
        if subject in row[2]:
            # занести фамилию должника, группу должника, описание задолженности и комментарии по ней
            details.append(row[0])
            details.append(row[1])
            details.append(row[3])
            details.append(row[4])
        # вот эти детали в виде списка(не кортежа, хотя тут разницы бы не было) подаются как долг
        debts.append(details.copy())
        details.clear()
    # не все долги есть, некоторые записи будут пусты, соответственно, надо очистить список долгов
    while i < len(debts):
        if len(debts[i]) == 0:
            debts.pop(i)
        else:
            i += 1
    # собственно, вернуть список списков деталей задолженностей по определенному предмету
    return debts


""" БЛОК выбора предмета для преподавателя"""


def choose_subject_teacher(message,mode):
    markup = types.ReplyKeyboardMarkup()
    subjects = []
    # если преподаватель ведёт несколько дисциплин, их всех нужно вывести
    for number in range(0, subjects_dict[message.chat.id]):
        subjects.append(subjects_dict[(message.chat.id, number)])
    # здесь это делается с помощью кнопок
    for subject in subjects:
        markup.row(subject)
    bot.send_message(message.chat.id,"Выберите предмет",reply_markup=markup)
    print(f"user {message.chat.username} (teacher) is choosing subject")
    if mode == "look":
        bot.register_next_step_handler(message,look_debtors_teacher)
    if mode == "create":
        bot.register_next_step_handler(message,choose_debtor_teacher_create)
    if mode == "edit":
        bot.register_next_step_handler(message,choose_debtor_teacher_edit)
    if mode == "delete":
        bot.register_next_step_handler(message,choose_debtor_teacher_delete)


""" БЛОК с функциями вывода долгов (на экран и в качестве значения фф)"""

# для куратора
def get_debtors_kurator(message, number):
    if number == 1:
        inter_surnames = debts_surnames()
        surnames = ''
        for surname in inter_surnames:
            print(surname[1])
            if surname[1] == groups_dict[message.chat.id]:
                surnames += surname[0]
                surnames += '\n'
        bot.send_message(message.chat.id, surnames, reply_markup=types.ReplyKeyboardRemove())
        print("JORA")
        kurator_inter(message)
    else:
        bot.delete_message(message.chat.id, message.message_id)

def look_debtors_teacher(message):
    debt_note = ""
    debt_details = get_debts_by_subject(message.text)
    for note in debt_details:
        print(note)
        debt_note += "Фамилия: "
        debt_note += note[0]
        debt_note += "\nГруппа: "
        debt_note += note[1]
        debt_note += "\nОписание задолженности: "
        debt_note += note[2]
        debt_note += "\nКомментарии: "
        if str(note[3]) == "None":
            debt_note += "нет"
        else:
            debt_note += note[3]

        bot.send_message(message.chat.id, debt_note)
        debt_note = ""
    teacher_inter(message)



""" БЛОК с функциями выбора должника и комментирования задолженности (куратор)"""
# его бы тоже изменить наподобие блока записи о задолженности
def choose_debtor_kurator(message):
    inter_surnames = debts_surnames()
    markup = types.ReplyKeyboardMarkup()
    for surname in inter_surnames:
        if surname[1] == groups_dict[message.chat.id]:
            # выводятся кнопки через массив
            markup.row(surname[0])
    bot.send_message(message.chat.id, 'Выберите должника', reply_markup=markup)
    print("user " + message.chat.username + " (kurator) is choosing debtor")
    bot.register_next_step_handler(message, choose_subject_kurator)
def choose_subject_kurator(message):
    # блок, возвращающий к выбору функций куратора
    # интересно, работает ли реально так? Нужен блок else или без него в порядке всё?
    if message.text == "отмена":
        bot.send_message(message.chat.id,"хорошо")
        print("user " + message.chat.username + " (kurator) is cancelled")
        kurator_inter(message)
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    # в словарь вносится имя выбранного должника, ключ - id чата и id сообщения
    # проблема с обращением к чужим данным может возникнуть,
    # если для разных пользователей id чата с ботом будет одинаковый
    message_dict[(message.chat.id,message.message_id)] = message.text

    markup = types.ReplyKeyboardMarkup()
    for row in cur.execute("SELECT fullname, subject FROM debtors"):
        if message.text in row[0]:
            markup.row(row[1])
    bot.send_message(message.chat.id, 'Выберите предмет', reply_markup=markup)
    print("user " + message.chat.username + " (kurator) is choosing subject")
    conn.close()
    bot.register_next_step_handler(message, type_comment_kurator)
def type_comment_kurator(message):
    if message.text == "отмена":
        bot.send_message(message.chat.id,"хорошо")
        print("user " + message.chat.username + " (kurator) cancelled watching")
        kurator_inter(message)
    else:
        # занести в словарь название предмета
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id,"введите комментарий")
        print("user " + message.chat.username + " (kurator) is commenting")
        bot.register_next_step_handler(message, comment_debts_kurator)
def comment_debts_kurator(message):

    surname = message_dict[(message.chat.id, message.message_id-4)]
    subject = message_dict[(message.chat.id, message.message_id-2)]
    comment = message.text

    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE debtors SET comments = '{comment}' WHERE fullname = '{surname}' AND subject = '{subject}'")
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id,"орошо, нормально")
    kurator_inter(message)


""" БЛОК с функциями создания задолженности (куратор)"""
def create_debtor_kurator(message):

    bot.send_message(message.chat.id, 'Введите имя должника или введите слово отмена,'
                                      ' чтобы уйти от внесения записи о должнике')
    print("user " + message.chat.username + " (kurator) is creating name of debtor")
    bot.register_next_step_handler(message, create_debtor_subject_kurator)
"""def create_debtor_group_kurator(message):
    if message.text.lower() != ("отмена" or "/start"):
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, 'Введите группу, в которой находится должник')
        print("user " + message.chat.username + " (kurator) is creating group of debtor")
        bot.register_next_step_handler(message, create_debtor_subject_kurator)
    # если заккхочется всё отрубить
    elif message.text == "/start":
        bot.send_message(message.chat.id,"VAS PONYAL")
        start(message)
    else:
        markup = types.ReplyKeyboardMarkup()
        markup.add("Продолжить", row_width=2)
        print(f"user {message.chat.username} (kurator) cancelled writing")
        bot.send_message(message.chat.id, 'хорошо', reply_markup=markup)
        bot.register_next_step_handler(message, kurator_inter)"""
def create_debtor_subject_kurator(message):
    # вот здесь проблему я решал, и она решилась
    if message.text.lower() != ("отмена" or "/start"):
        # занести в словарь фамилию должника, группа та же, к которой приставлен куратор
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, 'Введите предмет, по которому есть задолженность')
        print("user " + message.chat.username + " (kurator) is creating subject of debt")
        bot.register_next_step_handler(message, create_debt_description_kurator)
    elif message.text == "/start":
        bot.send_message(message.chat.id,"VAS PONYAL")
        start(message)
    else:
        bot.send_message(message.chat.id, "хорошо")
        print("user " + message.chat.username + " (kurator) cancelled writing")
        kurator_inter(message)
def create_debt_description_kurator(message):
    if message.text.lower() != ("отмена" or "/start"):
        # занести в словарь дисциплину, по которой есть задолженность
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, 'Введите описание задолженности (можно оставить прочерк)')
        print("user " + message.chat.username + " (kurator) is creating description of debt")
        bot.register_next_step_handler(message, create_debt_comment_kurator)
    elif message.text == "/start":
        bot.send_message(message.chat.id,"VAS PONYAL")
        start(message)
    else:
        bot.send_message(message.chat.id, "хорошо")
        print("user " + message.chat.username + " (kurator) cancelled writing")
        kurator_inter(message)
def create_debt_comment_kurator(message):
    if message.text.lower() != ("отмена" or "/start"):
        # занести в словарь описание задолженности
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, 'Введите комментарий по задолженности (можно оставить прочерк)')
        print("user " + message.chat.username + " (kurator) is creating comment of debt")
        bot.register_next_step_handler(message, create_debt_kurator)
    elif message.text == "/start":
        bot.send_message(message.chat.id,"VAS PONYAL")
        start(message)
    else:
        bot.send_message(message.chat.id, "хорошо")
        print("user " + message.chat.username + " (kurator) cancelled writing")
        kurator_inter(message)
def create_debt_kurator(message):
    # комментарию позволено быть любым
    if message.text == "/start":
        bot.send_message(message.chat.id,"VAS PONYAL")
        start(message)
    else:
        # надо вспомнить, что вводили ранее
        surname = message_dict[(message.chat.id, message.message_id - 6)]
        group = groups_dict[message.chat.id]
        subject = message_dict[(message.chat.id, message.message_id - 4)]
        description = message_dict[(message.chat.id, message.message_id - 2)]
        comment = message.text
        print(f"vvedi bot {surname}, {group}, {subject}, {description}, {comment}")

        conn = sqlite3.connect("list_1_3.db")
        cur = conn.cursor()
        cur.execute(f"INSERT INTO debtors VALUES ('{surname}','{group}','{subject}','{description}','{comment}')")
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "клас, внесли запись")
        kurator_inter(message)


""" БЛОК с функциями для создания задолженности (преподаватель)"""

def choose_debtor_teacher_create(message):
    # в словарь вносится название выбранного предмета, ключ - id чата и id сообщения
    message_dict[(message.chat.id, message.message_id)] = message.text
    bot.send_message(message.chat.id, 'Введите фамилию студента или введите слово отмена')
    print("user " + message.chat.username + " (teacher) is choosing student")
    bot.register_next_step_handler(message,type_debtor_group_teacher_create)
def type_debtor_group_teacher_create(message):
    if message.text != "отмена":
        # здесь в словарь заносится фамилия должника
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, "Введите группу студента")
        bot.register_next_step_handler(message,type_debt_description_teacher_create)
    else:
        bot.send_message(message.chat.id, "отмена принята")
        teacher_inter(message)
def type_debt_description_teacher_create(message):
    if message.text != "отмена":
        # здесь в словарь заносится группа должника
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, "Введите описание задолженности (можно оставить прочерк)")
        bot.register_next_step_handler(message,create_debt_teacher)
    else:
        bot.send_message(message.chat.id, "отмена принята")
        teacher_inter(message)
def create_debt_teacher(message):
    subject = message_dict[(message.chat.id, message.message_id-6)]
    surname = message_dict[(message.chat.id, message.message_id-4)]
    group = message_dict[(message.chat.id, message.message_id-2)]
    description = message.text

    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    cur.execute(f"INSERT INTO debtors VALUES ('{surname}','{group}','{subject}','{description}','-')")
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id,"Запись о задолженности создана")
    teacher_inter(message)



""" БЛОК с функциями удаления задолженности (преподаватель)"""


def choose_debtor_teacher_delete(message):
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    # в словарь вносится название выбранного предмета, ключ - id чата и id сообщения
    message_dict[(message.chat.id, message.message_id)] = message.text

    markup = types.ReplyKeyboardMarkup()

    for row in cur.execute("SELECT fullname, subject FROM debtors"):
        if message.text in row[1]:
            markup.row(row[0])
    bot.send_message(message.chat.id, 'Выберите студента', reply_markup=markup)
    print("user " + message.chat.username + " (teacher) is choosing student")
    conn.close()
    bot.register_next_step_handler(message,delete_debt)


def delete_debt(message):
    # сохранить в отдельные переменные название предмета и фамилию должника
    subject = message_dict[(message.chat.id,message.message_id-2)]
    student_name = message.text

    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    cur.execute(f"DELETE FROM debtors WHERE fullname = '{student_name}' AND subject = '{subject}'")
    conn.commit()

    bot.send_message(message.chat.id,"Удалили запись")
    teacher_inter(message)


""" БЛОК с функциями для изменения записи о задолженности(преподаватель)"""

def choose_debtor_teacher_edit(message):
    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    # в словарь вносится название выбранного предмета, ключ - id чата и id сообщения
    message_dict[(message.chat.id, message.message_id)] = message.text

    markup = types.ReplyKeyboardMarkup()

    for row in cur.execute("SELECT fullname, subject FROM debtors"):
        if message.text in row[1]:
            markup.row(row[0])
    bot.send_message(message.chat.id, 'Выберите студента', reply_markup=markup)
    print("user " + message.chat.username + " (teacher) is choosing student")
    conn.close()
    bot.register_next_step_handler(message,type_new_desc_teacher)
def type_new_desc_teacher(message):
    if message.text.lower() != ("отмена" or "/start"):
        # занести в словарь дисциплину, по которой есть задолженность
        message_dict[(message.chat.id, message.message_id)] = message.text
        bot.send_message(message.chat.id, 'Введите новое описание задолженности')
        print(f"user {message.chat.username} (teacher) cancelled editing")
        bot.register_next_step_handler(message,edit_debt_teacher)
    elif message.text == "/start":
        bot.send_message(message.chat.id,"VAS PONYAL")
        start(message)
    else:
        bot.send_message(message.chat.id, "хорошо")
        print("user " + message.chat.username + " (teacher) cancelled editing")
        kurator_inter(message)
def edit_debt_teacher(message):
    # вынести необходимую информацию(фамилию и группу для сверки, комментарий для создания изменения)
    subject = message_dict[(message.chat.id, message.message_id - 4)]
    student_name = message_dict[(message.chat.id, message.message_id - 2)]
    description = message.text

    conn = sqlite3.connect("list_1_3.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE debtors SET desc = '{description}' WHERE"
                f" fullname = '{student_name}' AND subject = '{subject}'")
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id,"Изменения внесены")
    teacher_inter(message)

""" Для студент"""
def print_debts(message):
    debt_note = ""
    debt_details = get_debts_by_surname(message.text)
    for note in debt_details:
        print(note)
        debt_note += "группа: "
        debt_note += note[0]
        debt_note += "\nпредмет: "
        debt_note += note[1]
        debt_note += "\nописание: "
        debt_note += note[2]
        debt_note += "\nкомментарии: "
        if str(note[3]) == "None":
            debt_note+= "нет"
        else:
            debt_note += note[3]

        bot.send_message(message.chat.id, debt_note)
        debt_note = ""
    pass


bot.infinity_polling()
