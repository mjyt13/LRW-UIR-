import csv
import statistics as stat

with open('studentsInfo.csv') as csvfile:
    students = [row for row in csv.DictReader(csvfile)]

keys = list(students[0])
disciplines = keys[1:]


def SumGrades(student):
    return sum([int(student[discipline]) for discipline in disciplines])


def StudentMean(student):
    return round(sum([int(student[discipline]) for discipline in disciplines]) / len(disciplines), 2)


def GradeModa(discipline):
    return stat.mode([int(student[discipline]) for student in students])


def GradeMax(discipline):
    return max([int(student[discipline]) for student in students])


def GradeMin(discipline):
    return min([int(student[discipline]) for student in students])


def GradeMiddle(discipline):
    return stat.median([int(student[discipline]) for student in students])


# mode - критерий по предметам
#      0 - все
#      1 - Математика
#      2 - ИСИС
#      3 - Социология
#      4 - ИГКГ
#      5 - ЯПМТ
#      6 - Курсовая по ЯПМТ

# среднее арифметическое/оценки по дисциплине, выводит список, 1 индексом строку названия mode
#   при выборе mode 0 - по группе, выводит с 1 индекса список вида [ФИО,число]
#   при выборе mode > 1 - по предмету, выводит 1 индексом среднее арифметическое/оценки по дисциплине

def ArithmeticMean(mode, sortStud=students):
    if mode == 0:
        grades = [[student[keys[0]], StudentMean(student)] for student in sortStud]
        return ['По всем'] + grades
    elif mode > 0 and mode <= len(disciplines):
        grades = [int(student[disciplines[mode - 1]]) for student in sortStud]
        return [disciplines[mode - 1], round(sum(grades) / len(students), 2)]
    else:
        print("Неверное значение для предмета")


def DisciplineGrades(mode, sortStud=students):
    if mode == 0:
        grades = [[student[keys[0]], student[discipline]] for student in sortStud for discipline in disciplines]
        return ['По всем'] + grades
    elif mode > 0 and mode <= len(disciplines):
        grades = [[student[keys[0]], student[disciplines[mode - 1]]] for student in sortStud]
        return [disciplines[mode - 1]] + grades
    else:
        print("Неверное значение для предмета")


def sortByGrades(mode, reverse=False):  # сортировка Пузырьком
    studentsCopy = students.copy()
    if mode == 0:
        for i in range(len(studentsCopy) - 1):
            for j in range(i + 1, len(studentsCopy)):
                if SumGrades(studentsCopy[i]) > SumGrades(studentsCopy[j]):
                    studentsCopy[i], studentsCopy[j] = studentsCopy[j], studentsCopy[i]
    elif mode > 0 and mode <= len(disciplines):
        for i in range(len(students) - 1):
            for j in range(i + 1, len(students)):
                if studentsCopy[i][disciplines[mode - 1]] > studentsCopy[j][disciplines[mode - 1]]:
                    studentsCopy[i], studentsCopy[j] = studentsCopy[j], studentsCopy[i]
    else:
        print("Неверное значение для предмета")

    return studentsCopy[::-1] if reverse else studentsCopy


# След функции выводят массив: 0 индекс - название предмета, 1 индекс - значение функции(max, min, moda, mid),
#                             индексы со 2 - ФИО студентов подходящих под критерии функции

def Middle(mode):
    if mode == 0:
        grades = [GradeMiddle(discipline) for discipline in disciplines]
        middle = ['По всем', stat.median(grades)]
        for student in students:
            StudDrades = [int(student[discipline]) for discipline in disciplines]
            if middle[1] in StudDrades: middle.append(student[keys[0]])
        return middle
    elif mode > 0 and mode <= len(disciplines):
        middle = [disciplines[mode - 1], GradeMiddle(disciplines[mode - 1])]
        for student in students:
            if middle[1] == int(student[middle[0]]): middle.append(student[keys[0]])
        return middle
    else:
        print("Неверное значение для предмета")


def Min(mode):
    if mode == 0:
        grades = [GradeMin(discipline) for discipline in disciplines]
        Min = ['По всем', min(grades)]
        for student in students:
            StudDrades = [int(student[discipline]) for discipline in disciplines]
            if Min[1] in StudDrades: Min.append(student[keys[0]])
        return Min
    elif mode > 0 and mode <= len(disciplines):
        Min = [disciplines[mode - 1], GradeMin(disciplines[mode - 1])]
        for student in students:
            if Min[1] == int(student[Min[0]]): Min.append(student[keys[0]])
        return Min
    else:
        print("Неверное значение для предмета")


def Max(mode):
    if mode == 0:
        grades = [GradeMax(discipline) for discipline in disciplines]
        Max = ['По всем', max(grades)]
        for student in students:
            StudDrades = [int(student[discipline]) for discipline in disciplines]
            if Max[1] in StudDrades: Max.append(student[keys[0]])
        return Max
    elif mode > 0 and mode <= len(disciplines):
        Max = [disciplines[mode - 1], GradeMax(disciplines[mode - 1])]
        for student in students:
            if Max[1] == int(student[Max[0]]): Max.append(student[keys[0]])
        return Max
    else:
        print("Неверное значение для предмета")


def Moda(mode):
    if mode == 0:
        grades = [GradeModa(discipline) for discipline in disciplines]
        moda = ['По всем', stat.mode(grades)]
        for student in students:
            StudDrades = [int(student[discipline]) for discipline in disciplines]
            if moda[1] in StudDrades: moda.append(student[keys[0]])
        return moda
    elif mode > 0 and mode <= len(disciplines):
        moda = [disciplines[mode - 1], GradeModa(disciplines[mode - 1])]
        for student in students:
            if moda[1] == int(student[moda[0]]): moda.append(student[keys[0]])
        return moda
    else:
        print("Неверное значение для предмета")


##for i in ArithmeticMean(0):
#    print(i)
# print()
# for i in ArithmeticMean(0, sortByGrades(0, True)):
#    print(i)

# немного функций от Максима
def retranslate(number):
    if number == 3:
        return "Удовлетворительно" + " (" + str(number) + ")"
    if number == 4:
        return "Хорошо" + " (" + str(number) + ")"
    if number == 5:
        return "Отлично" + " (" + str(number) + ")"


def ArithmeticMeanEntire(ArithmeticMean):
    summ = 0
    amount = 0.0
    for counter in range(1, len(ArithmeticMean)):
        summ += ArithmeticMean[counter][1]
        amount += 1
    return summ / amount

def SortingListEntire(ArithmeticMean):
    SortedList="Среднее арифметическое по всем предметам у одного студента:\n"
    for counter in range(1,len(ArithmeticMean)):
        SortedList = SortedList + ArithmeticMean[counter][0] + " " + str(ArithmeticMean[counter][1]) + "\n"
    return SortedList

def SortingListSubject(number):
    SortedList = "Отметки у каждого студента(ФИО, отметка):\n"
    for counter in range(1,len(DisciplineGrades(number))):
        SortedList = SortedList + DisciplineGrades(number)[counter][0] + " " + str(DisciplineGrades(number)[counter][1]) + "\n"
    return SortedList
