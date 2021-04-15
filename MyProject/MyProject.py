import requests
from bs4 import BeautifulSoup
import fake_useragent
import re
import datetime

from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.pagelayout import PageLayout
# TODO: Сделать салйдер для инструкций
# TODO: Криво выводятся недели //Готово

#Приложение подходит только для студентов РЭУ

week = []


class connect:

    def __init__(self, week_number=0):
        # Создаём объект session для того, чтобы сохранить куки и не перезаходить на сайт постоянно
        session = requests.Session()

        link = "Ссылка на сайт для авторизации"  # Ссылка на страницу авторизации

        user = fake_useragent.UserAgent().random  # Фейковый юзерагент, чтобы сайт дал его спарсить
        header = {'User-Agent': user}

        # Создаём словарь с ключами для авторизации
        datas = {
            'AUTH_FORM': 'Y',
            'TYPE': 'AUTH',
            'backurl': '/index.php',
            'USER_LOGIN': 'Логин',
            'USER_PASSWORD': 'Пароль',
            'Login': 'Войти'
        }

        response = session.post(link, data=datas, headers=header).text

        user_info = "ссылка на страницу с расписанием" + str(week_number)
        profile_response = session.get(user_info, headers=header)

        cookie_dict = [
            {"domain": key.domain, "name": key.name, "path": key.path, "value": key.value}
            for key in session.cookies
        ]

        session2 = requests.Session()

        for cookies in cookie_dict:
            session2.cookies.set(**cookies)

        resp = session2.get(user_info, headers=header).text

        td_contents = []
        soup = BeautifulSoup(resp, 'lxml')
        table = soup.find('table', class_="table table-bordered table_lessons")
        # lesson = block.find_all('p')[1].text

        for td in table.find_all('td'):
            td_contents.append(td.text.split('\n'))  # получаем массив разбитый по переносам

        result = []  # Новый массив для хранения матрицы расписания
        for elements in td_contents:
            x = list(filter(None, elements))  # Удаляем пустые элементы из массива
            temp = []
            for el in x:
                el = el.lstrip()  # Удалили пробелы
                el = el.rstrip()
                temp.append(el)
            result.append(temp)  # Создание массива массивов

        # file = open("result.txt", "+w", encoding="utf-8")
        # for el in result:
        #     for elem in el:
        #         file.write(str(elem) + ' \n')
        #
        # file.close

        week.append(result[0][0])
        for lessons in range(1, 100, 18):

            # Вывод дня недели
            week.append(result[lessons][0])

            for les in range(lessons + 1, lessons + 17, 2):

                # Вывод номера пары и времени
                week.append(result[les][0] + " (" + result[les][1] + ") ")

                if len(result[les + 1]) > 0:

                    if result[les + 1][4].startswith("Элективные"):
                        # Вывод пары по физре
                        if result[les + 1][11].startswith("Аудитория"):
                            week.append(result[les + 1][4])
                            week.append(result[les + 1][11] + " / " + result[les + 1][22])
                            week.append(result[les + 1][3] + " / " + result[les + 1][13])
                            week.append(result[les + 1][7] + " / " + result[les + 1][17])

                        else:
                            week.append(result[les + 1][4])
                            week.append(result[les + 1][12] + " / " + result[les + 1][23])
                            week.append(result[les + 1][3] + " / " + result[les + 1][14])
                            week.append(result[les + 1][7] + " / " + result[les + 1][18])

                    else:

                        # Вывод названия пары
                        week.append(result[les + 1][3])

                        for elem in range(0, len(result[les + 1]), 1):
                            if result[les + 1][elem].startswith("Аудитория"):
                                # Вывод аудитории
                                week.append(result[les + 1][elem])

                        # Вывод что за пара и ФИО препода
                        week.append(result[les + 1][4])
                        week.append(result[les + 1][6])

                else:
                    week.append("Пары нету")

                week.append("")

            week.append("//////////////////////////////////////")
            week.append("//////////////////////////////////////")
            week.append("")


class MainWindow(BoxLayout):

    def process_command_date(self):

        self.ids.text_lable.text = ""
        self.date = datetime.date.today()
        self.date_next = self.date + datetime.timedelta(days=1)

        self.PATTERN_IN = "%d.%m.%Y"
        self.date = datetime.datetime.strftime(self.date, self.PATTERN_IN)
        self.date_next = datetime.datetime.strftime(self.date_next, self.PATTERN_IN)

        connect()
        self.ids.text_lable.text = str(week[0]) + '\n\n'

        for i in range(1, len(week)):
            if str(self.date) in week[i]:
                for j in range(i, len(week) - 1):
                    if str(self.date_next) in week[j + 1]:
                        break
                    else:
                        self.ids.text_lable.text += str(week[j]) + '\n'
        week.clear()

    def process_command(self):

        if self.ids.button_command.text == "Очистить экран":
            week.clear()
            self.ids.button_command.text = "Получить расписание на неделю"
            self.ids.week_number_text.text = ' '
            self.ids.text_lable.text = ""

        else:
            if self.ids.week_number_text.text != "":
                self.number = self.ids.week_number_text.text
            else:
                self.number = 0

            #self.remove_widget(self.ids.week_number_text.text)

            connect(int(self.number))
            self.ids.text_lable.text = str(week[0]) + '\n\n'

            for i in range(1, len(week)):
                self.ids.text_lable.text += str(week[i]) + '\n'

            self.ids.button_command.text = "Очистить экран"

    def week_given(self):
        pass


class MainApp(App):

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    MainApp().run()

