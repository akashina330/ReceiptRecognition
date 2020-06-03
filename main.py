import json  # формат хранения данных
import os  # работа с ОС (проход по файловой системе)
import re  # работа с регулярными выражениями (для поиска ключевых слов в распознанном тексте)
import sys  # работа с ОС на уровне командной строки
import logging # журнал работы (надо бы доделать)
from datetime import datetime  # работа с таймером (засекать время работы программы)
import requests  # работа с запросами на сервер
from PyQt5.QtCore import QSize
from bs4 import BeautifulSoup  # парсинг веб-страницы
import cv2  # OpenCV
import pytesseract  # Tesseract-OCR
from PyQt5 import QtWidgets, QtGui, Qt  # работа с интерфейсом
from pytesseract import Output  # форматированный вывод данных
import webbrowser  # для открытия веб-страницы для скачивания Tesseract-OCR
import pyzbar.pyzbar as pyzbar  # библиотека для работы с QR-кодами
from autocorrect import Speller

corrector = Speller(lang='ru')

import no_tess  # класс окна с установкой tesseract
import des  # основное окно
import recognition  # окно, в котором идет распознавание
import time_ui  # финальное окно со временем работы

# суммы всех транзакций
# здесь или декодированная сумма, или None, если не сможем считать код (а такое встречается иногда)
totalsQR = []

# суммы с текста, сравним


class Main(QtWidgets.QMainWindow, recognition.Ui_MainWindow):  # Класс окна вывода результатов
    page_index = 0

    # текущий объект класса Main + выбранная директория
    # конструктор
    def __init__(self, my_directory):
        # texts -- результаты OCR
        global i, ocr_recognition, src, ocr_pages, qr_results, start_time


        def create_threads(dir):  # Тут создаем список изображений из выбранной папки
            images = []
            # получим список всех файлов в директории
            files = os.listdir(dir)
            for i in range(len(files)):
                # а здесь считывааем изображения
                images.append(cv2.imread(dir + "/" + files[i]))
                # получим и матрицы изображений, и файлы
            return images, files


        # Объявляем массивы и переменные для пользования со всех функций
        global times, patterns, ocr_results, ocr_pages, text

        patterns = ["СУММА", "ИТОГ", "ИТОГО", "ПОЛУЧЕНО", "ИТОГО К ОПЛАТЕ"]  # ключевые для поиска суммы чека слова

        # формат для вывода
        ocr_pages = []
        # формат для работы
        ocr_results = []
        # по каждому чеку время сохранить отдельно
        times = []
        # самая страшная боль
        error = "QR code is not detected or have not valid info"

        super().__init__()
        self.setupUi(self)

        # сюда распознаем текст с QR-кода
        self.qr_results = []
        images, src = create_threads(my_directory)
        self.code = 1
        for img in images:  # Начинаем перебор изображений из папки
            start_time = datetime.now()  # Сохраняем время начала перебора
            try:

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # рекомендация из документации
                # как правило, остальные вещи (бинаризация, например), портят чек
                # этот метод работает для текста с большими расстояниями между символами (на чеке текст не такой)
                #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # img,_ = cv2.threshold(img,127,255,cv2.THRESH_OTSU)
                #img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                #a_thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                #img = a_thresh
                # текст с фото -- процентов 50 точности
                # текст со скана -- процентов 80 минимум
                # оптическое распознавание здесь для сравнения точности с распознанными из QR-кода данными
                # язык лучше оставить один, т.к. как правило, вавилонское смешение в конечном итоге уменьшает точность

                dec = pytesseract.image_to_string(img, lang='rus', output_type=Output.STRING, config="--psm " + str(6))
                #dec = corrector(dec)

                #decR = dec.split()
                #dec1 = ''
                #print(decR)
                #for d in decR:
                    #try:
                     #   d = corrector(d)
                     #   dec1 = dec1 + d + " "
                   # except:
                    #    dec1 = dec1 + d + " "
                   # dec1 = dec1 + d
                #dec = dec1

                try:
                    # ищем коды, находим не всегда
                    # symbols=[pyzbar.ZBarSymbol.QRCODE] -- на китайском формуле это исправило проблему с
                    # WARNING: .\zbar\decoder\pdf417.c:89: <unknown>: Assertion "g[0] >= 0 && g[1] >= 0 && g[2] >= 0" failed.

                    # факт такой: с фото читает, со скана -- нет
                    decoded_objects = pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.QRCODE])
                    if len(decoded_objects) == 0:
                        error = "QR-code was not detected"
                        # кода нет, сумму в коде не ищем

                        totalsQR.append(None) # это для корректного отображения сумм

                        self.code = 1 #ошибочка вышла
                    else:
                        # print('QR-code was detected')

                        decoded_objects = decoded_objects[
                            -1]  # берем последний объект, на случай, если кодов в чеке несколько
                        obj = decoded_objects

                        # декодируем
                        self.data = obj.data.decode(encoding='utf-8')
                        # пишем в лог
                        logging.info(self.data)

                        if obj.type == "QRCODE":  # Убираем все лишнее и проверяем на возможность использования этого кода для парсинга
                            # все коды с чеков содержат лишние символы в начале и в конце строки
                            test_my_qr = str(obj.data).replace("b'", "").replace("'", "")  # убираем лишнее
                            # вне данного формата декодировать не удается
                            if not re.search(r"\d{8}T\d{4,6}", str(test_my_qr)):  # проверяем формат кода
                                self.code = 1
                                totalsQR.append(None)  # это для корректного отображения сумм
                                error = "Non-standart format of QR-code"
                            else:
                                # print(test_my_qr)
                                # нужна не строка, а список (но из одной строки)
                                my_receipt = test_my_qr.split("?")
                                # print (my_receipt)
                                for elem in my_receipt:
                                    if re.search(r"\d{8}T\d{4,6}", str(elem)):  # Сохраняем данные QR-кода в переменные
                                        qr_code = elem.split("&")  # информация в коде разделяется этим символом
                                        transaction_datetime = qr_code[0].replace("t=",
                                                                                  "")  # дата и время совершения транзакции
                                        # print(transaction_datetime)
                                        usable_datetime = list(
                                            transaction_datetime)  # чтобы собрать отдельно дату и время, сначала разделим строку на куски по одному символу
                                        # print(usable_datetime)
                                        format_datetime = str(usable_datetime[0]) + str(usable_datetime[1]) + str(
                                            usable_datetime[2]) + str(usable_datetime[3]) + "-" + str(
                                            usable_datetime[4]) + str(usable_datetime[5]) + "-" + str(
                                            usable_datetime[6]) + str(usable_datetime[7]) + str(
                                            usable_datetime[8]) + str(
                                            usable_datetime[9]) + str(usable_datetime[10]) + ":" + str(
                                            usable_datetime[0]) + str(usable_datetime[0]) + ":00.000Z"
                                        # print(format_datetime)
                                        s = qr_code[1].replace("s=", "")  # сумма транзакции
                                        # все суммы, если они были распознаны, сохраняем в массив
                                        totalsQR.append(s)
                                        #print(totals)
                                        fn = qr_code[2].replace("fn=", "")  # фискальный накопитель
                                        fd = qr_code[3].replace("i=", "")  # фискальный документ = номер чека
                                        fp = qr_code[4].replace("fp=", "")  # фискальный признак
                                        # print(s)

                                        # Начинаем парсить
                                        headers = {
                                            # Хедеры нужны для того, чтобы сайт понимал, чего мы от него хотим (кодировки, тип данных, язык)
                                            "accept": "application/json, text/plain, */*",
                                            "accept-encoding": "gzip, deflate, br",
                                            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                                            "content-length": "164",
                                            "content-type": "application/json;charset=UTF-8",
                                            "cookie": "_ga=GA1.2.1153270599.1589656882; _gid=GA1.2.1288800306.1589656882; _ym_uid=1589656882268393515; _ym_d=1589656882; _ym_wasSynced=%7B%22time%22%3A1589656882075%2C%22params%22%3A%7B%22eu%22%3A0%7D%2C%22bkParams%22%3A%7B%7D%7D; _ym_isad=1; _ym_visorc_49898752=w; _fbp=fb.1.1589657228481.975483907; _gcl_au=1.1.576637721.1589657229; _ym_visorc_26812653=b; _ym_visorc_39116670=w",
                                            "origin": "https://check.ofd.ru",
                                            "referer": "https://check.ofd.ru/",
                                            "sec-fetch-dest": "empty",
                                            "sec-fetch-mode": "cors",
                                            "sec-fetch-site": "same-origin",
                                            "x-requested-with": "XMLHttpRequest"
                                        }
                                        # В таком формате данные передаются на сайт ОФД
                                        data = {"TotalSum": s.replace(".", ""), "FnNumber": fn,
                                                "ReceiptOperationType": "1", "DocNumber": fd,
                                                "DocFiscalSign": fp, "DocDateTime": format_datetime}
                                        # Запрос для проверки
                                        req = requests.post("https://check.ofd.ru/Document/FetchReceiptFromFns",
                                                            headers=headers,
                                                            data=json.dumps(data),
                                                            timeout=(30, 30))
                                        if req.status_code == 200:  # проверка на валидность сайта
                                            # print('В базе check.ofd.ru')
                                            soup = BeautifulSoup(req.text, "lxml")  # парсим html-теги в строку
                                            # print (soup)
                                            # print(format_datetime)
                                            # между написанными ниже тегами та информация, которая нам нужна
                                            format_datetime = soup.find_all("div", {"class": "ifw-col"})
                                            # print(format_datetime)

                                            # сюда запишем все, что отправил сервер
                                            sent = []
                                            for text in format_datetime:
                                                sent.append(text.text)
                                                # print(sent)
                                            text_qr = " ".join(sent)
                                            self.qr_results.append(text_qr)
                                            self.code = 0
                                            # print(self.qr_text)
                                        elif req.status_code == 406 or req.status_code == 404:  # Ошибки, когда чек просрочен или недействителен
                                            # проверяем на другом сайте
                                            #print('В базе proverkacheka.com')
                                            try:
                                                headers = {
                                                    "Accept": "application/json, text/javascript, */*; q=0.01",
                                                    "Referer": "https://proverkacheka.com/",
                                                    "X-Requested-With": "XMLHttpRequest",
                                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                                                  "Chrome/81.0.4044.122 Safari/537.36 "
                                                }
                                                # для этой базы дату и время перепишем в другом формате
                                                transaction_datetime = transaction_datetime[6] + transaction_datetime[
                                                    7] + "." + transaction_datetime[4] + transaction_datetime[5] + "." + \
                                                                       transaction_datetime[0] + transaction_datetime[
                                                                           1] + transaction_datetime[2] + \
                                                                       transaction_datetime[
                                                                           3] + "+" + transaction_datetime[9] + \
                                                                       transaction_datetime[10] + "%3A" + \
                                                                       transaction_datetime[11] + \
                                                                       transaction_datetime[12]
                                                # print(transaction_datetime)
                                                data = {
                                                    "fn": fn,
                                                    "fd": fd,
                                                    "fp": fp,
                                                    "n": "1",
                                                    "s": s,
                                                    "t": transaction_datetime,
                                                    "qr": "0"
                                                }
                                                # здесь проверим на другой базе, если не удалось найти в первой
                                                req = requests.post("https://proverkacheka.com/check/get",
                                                                    headers=headers,
                                                                    data=data,
                                                                    timeout = (30, 30))
                                                my_receipt = json.loads(str(json.loads(str(json.loads(req.text)["data"])
                                                                                       .replace("\"", "").replace("'",
                                                                                                                  "\""))[
                                                                                "json"]).replace("\"", "").replace("'",
                                                                                                                   "\""))
                                                my_receipts = []
                                                names = json.loads(
                                                    str(my_receipt["items"]).replace("\"", "").replace("'", "\""))
                                                for i in range(len(names)):
                                                    tov = json.loads(str(names[i]).replace("\"", "").replace("'", "\""))
                                                    name = tov["name"]
                                                    #print(name)
                                                    price = tov["price"]

                                                    #print(price) #нет разделителя между рублями и копейками
                                                    pr = str(price)
                                                    ls = len(pr)
                                                    sqq = []
                                                    a = []
                                                    for i in range(ls - 2):
                                                        sqq.append(pr[i])
                                                    kop11 = pr[-1]
                                                    kop22 = pr[-2]
                                                    a.append( "".join(sqq) + "." + str(kop22) + str(kop11))
                                                    #print(a)
                                                    #price = str(a[0])
                                                    #print(price)
                                                    #print(a[0])
                                                    price = a[0]

                                                    quant = tov["quantity"]
                                                    #print(quant)

                                                    sum = tov["sum"]
                                                    #print(sum) #также нет разделителя
                                                    s = str(sum)
                                                    ls = len(s)
                                                    sqq = []
                                                    a = []
                                                    for i in range(ls - 2):
                                                        sqq.append(s[i])
                                                    kop11 = s[-1]
                                                    kop22 = s[-2]
                                                    a.append("".join(sqq) + "." + str(kop22) + str(kop11))
                                                    # print(a)
                                                    sum = a[0]
                                                    #print(sum)

                                                    #realAmount = price*quant

                                                    al = name + "\n" + str(price) + " * " + str(quant) + " = " + str(
                                                        sum) + "\n"
                                                    my_receipts.append(str(al))

                                                summ = str(my_receipt["totalSum"])
                                                ls = len(summ)
                                                sq = []
                                                for i in range(ls - 2):
                                                    sq.append(summ[i])
                                                kop1 = summ[-1]
                                                kop2 = summ[-2]
                                                my_receipts.append("ИТОГ: " + "".join(sq) + "." + str(kop2) + str(kop1))
                                                text_qr = " ".join(my_receipts)
                                                self.qr_results.append(text_qr)
                                                self.code = 0


                                            except:
                                                self.code = 1
                                                error = "Could not find any data, but total amount was decoded"
                except Exception:
                    # traceback.print_exc()
                    logging.error("Could not recognize a QR-code")
                    totalsQR.append(None)
                    self.code = 1
                try:
                    if self.code == 1:  # Если QR-код не распознался, то начинаем оптическое распознавание
                        self.qr_results.append(error)
                        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # рекомендация из документации
                        #ocr_recognition = pytesseract.image_to_string(img, lang='rus', output_type=Output.STRING,
                                                                      #config="--psm " + str(6))
                        ocr_recognition = dec
                        # print ('Распознаем вручную')
                    else:
                        ocr_recognition = ""  # Если ошибок не было, то оставляем это поле пустым
                        # оптическое распознвание все равно нужно!!!
                        ocr_recognition = dec


                except:
                    ocr_recognition = ""
                    error = "error"

            except Exception:
                ocr_recognition = "Text is not valid"


            #print(totals)
            # Работа с массивами для переключения между чеками
            ocr_pages.append(ocr_recognition) # для вывода в окно
            text = ocr_recognition.split(" ")
            ocr_results.append(text) # для поиска суммы, данные там разделены пробелами, лучше поиск
            times.append(datetime.now() - start_time)
            # print(len(texts))
            # print(len(self.qr_text))


        self.label_6.setText("Time: " + str(times[0]))

        self.textBrowser_2.setText(self.qr_results[self.page_index])

        self.textBrowser.setText(ocr_pages[0])

        self.pix = QtGui.QPixmap(my_directory + "/" + src[0])
        #pic = self.pix
        #self.pix = self.label_4.pixmap().scaled(QSize(self.label_4.size()), Qt.KeepAspectRatio, Qt.FastTransformation)
        # почему не работает?
        self.label_4.setPixmap(self.pix)

        #self.label_4.setPixmap(self.pix)

        self.label_4.setScaledContents(1)
        self.label_4.showNormal()


        print(totalsQR)


        self.n.clicked.connect(self.next)  # При нажатии кнопок вызываются функции смены картинки и текстов
        self.b.clicked.connect(self.back)

        #print(totals[-1])
        self.search_total()
        global work_directory
        work_directory = my_directory

        #на этом этапе проверим все суммы
        #print(totals)
        #

    def next(self):
        if self.page_index < len(ocr_pages) - 1:
            self.page_index = self.page_index + 1  # Если была нажата кнопка вперед, то к индексу добавляем единицу и заполняем все поля
            self.label_6.setText("Time: " + str(times[self.page_index]))
            self.textBrowser_2.setText(str(self.qr_results[self.page_index]))
            self.textBrowser.setText(ocr_pages[self.page_index])

            self.pix = QtGui.QPixmap(work_directory + "/" + src[self.page_index])
            #self.label_4.setPixmap(self.pix)
            #self.pix = self.label_4.pixmap().scaled(QSize(self.label_4.size()), Qt.KeepAspectRatio,
             #                                       Qt.FastTransformation)

            # int w = std::min(pixmap.width(),  label->maximumWidth());
       #int h = std::min(pixmap.height(), label->maximumHeight());
       #pixmap = pixmap.scaled(QSize(w, h), Qt::KeepAspectRatio, Qt::SmoothTransformation);
       #label->setPixmap(pixmap);

            self.label_4.setPixmap(self.pix)
            self.search_total()


    def back(self):
        if self.page_index > 0:
            self.page_index = self.page_index - 1
            self.label_6.setText("Time: " + str(times[self.page_index]))
            self.textBrowser_2.setText(str(self.qr_results[self.page_index]))
            self.textBrowser.setText(ocr_pages[self.page_index])
            self.pix = QtGui.QPixmap(work_directory + "/" + src[self.page_index])
            #self.label_4.setPixmap(self.pix)
            #self.pix = self.label_4.pixmap().scaled(QSize(self.label_4.size()), Qt.KeepAspectRatio,
             #                                       Qt.FastTransformation)
            self.label_4.setPixmap(self.pix)
            self.search_total()

    # Функция которая перебирает все слова, пока не найдет слово из списка{ИТОГО, СУММА, ИТОГ}
    def search_total(self):
        find = 0
        for word in ocr_results[self.page_index]:
            for ik in patterns:
                if re.search(ik.lower(), word.lower()):
                    ind = ocr_results[self.page_index].index(word)
                    find = 1
            if find:
                break
            if not find:
                for word in self.qr_results[self.page_index].split(" "):
                    for ik in patterns:
                        if re.search(ik.upper(), word):
                            ind = self.qr_results[self.page_index].split(" ").index(word)
                            find = 1
                    if find:
                        break
        flag = 0
        # Когда индекс слова найден, начинаем искать сумму, это ближайшая цифра справа
        try:
            i = 1
            while flag == 0:
                receipt = ocr_results[self.page_index][int(ind) + int(i)].split("\n")[0].replace("=", "").replace(".", "").replace(",",
                                                                                                                    "").isdigit()
                if receipt:
                    total = ocr_results[self.page_index][int(ind) + int(i)].split("\n")[0].replace("=", "")
                    #print(total)
                    flag = 1
                else:
                    i = i + 1

        except:
            total = " --- "

        try:
            i1 = 0
            while flag == 0:
                receipt = self.qr_results[self.page_index].split(" ")[int(ind) + int(i1)].replace(".", "").isdigit()
                if receipt:
                    total = self.qr_results[self.page_index].split(" ")[int(ind) + int(i1)].split("\n")[0].replace("=", "")
                    flag = 1
                i1 += 1
        except:
            total = " --- "

        # не нашли в коде -- берет ту, что распознали оптически
        # нашли в коде -- берём её
        if (totalsQR[self.page_index] is not None) and (total != totalsQR[self.page_index]):
            self.total_sum.setText(totalsQR[self.page_index])
        else:
            self.total_sum.setText(total)

#print(totalsOCR)

# Класс окна, если на компьютере не установлен tesseract-OCR
class Tess(QtWidgets.QMainWindow, no_tess.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.open)

    def open(self):
        webbrowser.open('https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0.20190623.exe')
        self.close()


# Класс окна конца отчета времени выполнения программы
class Time(QtWidgets.QMainWindow, time_ui.Ui_Form):
    def __init__(self, end):
        super().__init__()
        self.setupUi(self)
        self.label.setText(str(end))


# Класс окна с выбором папки
class Mainn(QtWidgets.QMainWindow, des.Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.folder.clicked.connect(self.browse_folder)
        self.start.clicked.connect(self.starts)

    # суммарное время работы программы
    def starts(self):

        stort_time = datetime.now()
        self.win = Main(directory)
        end = datetime.now() - stort_time
        self.time = Time(end)
        self.close()
        self.win.show()
        self.time.show()


    # Окно выбора папки с чеками
    def browse_folder(self):
        global directory
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder: ")

        logging.info(directory + " is used")

        files = []
        if directory:
            for file_name in os.listdir(directory):
                # выбираем только изображения и выводим их количество
                if file_name.split(".")[-1] in ["jpg", "png", "JPG", "jpeg", "webp"]:
                    files.append(file_name)
        self.len.setText(str(len(files)))

        logging.info(str(len(files)) + ' image(s) was found')

        if len(files) != 0:
            self.start.setEnabled(1)


def main():  # Главная функция программы, где первым делом проверяется наличие tesseract-OCR

    logging.basicConfig(filename="app_log.log", level=logging.INFO, filemode='w')

    app = QtWidgets.QApplication(sys.argv)
    if not os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe") and not os.path.exists(
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):

        logging.info("Tesseract-OCR will be installed")

        tess = Tess()
        tess.show()
    else:
        if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        else:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        windows = Mainn()
        windows.show()

        logging.info("Tesseract-OCR have been already installed")

    app.exec_()


if __name__ == '__main__':
    main()
