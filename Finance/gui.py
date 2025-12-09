import gi

import re

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk

from variables import *
import get_check, parsing_check

class MainGui:
    def __init__(self, data_class):
        global ru_months

        self.data_class = data_class

        self.builder = Gtk.Builder()#Создаём объект self.builder для загрузки интерфейса из файла
        self.builder.add_from_file("gui.ui")#загружаем интерфейс из файла

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()#Добавление стилей
        provider.load_from_path("style.css")
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        self.entry_work = EntryTable(self)#для работы с таблицей и вводом данных

        self.window = self.builder.get_object("window")#получаем главное окно программы
        self.window.connect("destroy", lambda e: [data_class.save(), Gtk.main_quit(e)])#уничтожаем и завершаем главный поток, при закрытии окна
        
        self.createMenuBar()#создание меню
        self.create()#Создаём все виджеты интерфейса
        self.signals()#Создаём сигналы/отклики
        
        self.monthLbl.set_text(ru_months[data_class.now_month_index])#Устанавливаем переданный месяц

        self.load()#загружаем все данные с предыдущих сессий, если такие есть
        self.window.show_all()

        Gtk.main()

    def create(self):#Объявления всех виджетов интерфейса
        #Кнопки
        self.delBtn = self.builder.get_object("delBtn")#кнопка удаления статьей расхода
        self.tableGrid = self.builder.get_object("tableGrid")#таблица, где статьи расхода и их значения
        self.addBtn = self.builder.get_object("addBtn")#кнопка добавления статьей расхода
        # self.nextBtn = self.builder.get_object("nextMonthBtn")#кнопка переключения месяца на следующий
        # self.pastBtn = self.builder.get_object("pastMonthBtn")#кнопка переключения месяца на следующий

        #Поля ввода
        self.resultEntry = self.builder.get_object("resultEntry")#Entry для вывода ИТОГО
        self.budgetEntry = self.builder.get_object("budgetEntry")#Entry для бюджета
        self.leftEntry = self.builder.get_object("leftEntry")#Entry для рассчёта сколько денег осталось ИТОГО-БЮДЖЕТ

        #Текст
        self.monthLbl = self.builder.get_object("monthLbl")#Лейбл, где указан выбранный месяц

    def signals(self):
        #Entry
        self.budgetEntry.connect("changed", self.budgetEntry_signal)#При изменении entry итого, изменяем поле ввода ОСТАЛОСЬ по формуле БЮДЖЕТ-ИТОГО
        self.resultEntry.connect("changed", lambda e: self.calculateEndResult)#entry_work.entry_calculation)
        
        #Buttons
        self.addBtn.connect("clicked", lambda e: self.entry_work.append_entry())#при нажатии на кнопку добавляем статью расхода
        self.delBtn.connect("clicked", lambda e: [self.entry_work.delete_entry(), self.calculateEndResult()])#при нажатии на кнопку удаляем статью расхода
    #     self.nextBtn.connect("clicked", lambda e: self.set_now_month_signal(1))
    #     self.pastBtn.connect("clicked", lambda e: self.set_now_month_signal(-1))

    # def set_now_month_signal(self, arg):
    #     self.data_class.now_month_index += arg

    def budgetEntry_signal(self, e):#изменение поля "осталось"
        try:
            tmp = float(self.budgetEntry.get_text())-float(self.resultEntry.get_text())#БЮДЖЕТ-ИТОГО
            self.data_class.budget = self.budgetEntry.get_text()#сохраняем данные в классе Data

            self.leftEntry.set_text(str(tmp))
        except: pass

    def load(self):#загрузка интерфейса и остальных данных их прошлых сессий
        if self.data_class.loaded_tableEntrys == None:#если таблица не существует, то завершаем метод
            return

        for i in range(0, len(list(self.data_class.loaded_tableEntrys.keys())[:-1])):
            self.entry_work.append_entry(list(self.data_class.loaded_tableEntrys.keys())[i], list(self.data_class.loaded_tableEntrys.values())[i])

        if self.data_class.encoded_password != None and self.data_class.autoLoadChecks == True and list(self.data_class.loaded_tableEntrys.keys())[0] == "Супермаркеты" and list(self.data_class.loaded_tableEntrys.values())[0] == None:
            checks = get_check.GetCheck()
            checks.login = self.data_class.user_mail
            checks.password = self.data_class.encoded_password.to_bytes((self.data_class.encoded_password.bit_length() + 7) // 8, "little").decode()
            checks.data_class = self.data_class

            checks.login_()

            end_result = 0
            for msg in checks.get(PYATOROCHKA):#перебираем массив из полученных сообщений
                end_result += parsing_check.pyatorochka_check(msg)#получаем значения из каждого сообщения и складываем

            for msg in checks.get(FIXPRICE):#перебираем массив из полученных сообщений
                end_result += parsing_check.fixPrice_check(msg)#получаем значения из каждого сообщения и складываем

            list(self.entry_work.valuesEntry.values())[0].set_text(str(round(end_result, 3)))
        
        self.calculateEndResult()

        try:
            self.budgetEntry.set_text(str(self.data_class.budget))
            self.budgetEntry_signal(None)
        except: pass
    
    def choose_directory(self, title=None, type_=Gtk.FileChooserAction.SAVE, method=None):#Выбор директорий
        dialog = Gtk.FileChooserDialog(
            title=title,
            parent=self.window,
            action=type_,
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
        )

        self.data_class.excel_directory = dialog.run()

        if self.data_class.excel_directory == Gtk.ResponseType.OK:
            self.data_class.excel_directory = dialog.get_filename()
            
            if type_ == Gtk.FileChooserAction.SAVE and ".xlsm" not in self.data_class.excel_directory and ".xls" not in self.data_class.excel_directory and ".xlsx" not in self.data_class.excel_directory and ".xlsx" not in self.data_class.excel_directory:#Если в имени файла нету не одного из форматов,
                self.data_class.excel_directory += ".xlsx"#тогда добавляем стандартное расширение эксель
            
            method()

            if method == self.data_class.import_excel:#Если импорируем эксель, то
                for i in range(0, len(self.entry_work.valuesEntry)):#перебираем список существуещих полей ввода
                    self.entry_work.delete_entry()#и уничтожаем их
                    
                self.load()
            
        dialog.destroy()#Уничтожаем диалоговое окно

    def createMenuBar(self):
        mb = Gtk.MenuBar()

        fileMenu = Gtk.Menu()
        file = Gtk.MenuItem(label="Файл")
        file.set_submenu(fileMenu)

        save_as_excel = Gtk.MenuItem(label="Экспортировать excel")
        save_as_excel.connect("activate", lambda e: self.choose_directory("Экспорт excel", method=self.data_class.save_as_excel))
        fileMenu.append(save_as_excel)

        save_as_excel = Gtk.MenuItem(label="Импортировать excel")
        save_as_excel.connect("activate", lambda e: self.choose_directory("Импорт excel", Gtk.FileChooserAction.OPEN, self.data_class.import_excel))
        fileMenu.append(save_as_excel)

        #========
        loadMenu = Gtk.Menu()
        loadLbl = Gtk.MenuItem(label="Автозагрузка данных с почты")
        loadLbl.set_submenu(loadMenu)

        check_item = Gtk.CheckMenuItem(label="Включено")
        check_item.set_active(self.data_class.autoLoadChecks)#Задаём параметр по умолчанию вкл/выкл
        check_item.connect("toggled", lambda e: [self.data_class.set_autoLoadChecks(e.get_active())])#При изменении checkitem изменяем значение переменной autoLoadChecks из класса Data

        settings_item = Gtk.MenuItem(label="Настройки")
        settings_item.connect("activate", lambda e: [passwordWindow(self.data_class)])

        loadMenu.append(check_item)
        loadMenu.append(settings_item)
        #========
        
        mb.append(file)
        mb.append(loadLbl)

        self.builder.get_object("mainBox").pack_start(mb, False, False, 0)#выводим на экран

        self.builder.get_object("mainBox").reorder_child(mb, 0)#делаем так, чтобы menubar был сверху остальных виджетов

    def calculateEndResult(self):#считаем ИТОГО
        end_result = 0

        for entry in list(self.entry_work.valuesEntry.values()):
            try:
                end_result += float(entry.get_text())
            except: pass

        self.resultEntry.set_text(str(end_result))

class passwordWindow:
    def __init__(self, data_class):
        self.data_class = data_class

        self.builder = Gtk.Builder()#Создаём объект self.builder для загрузки интерфейса из файла
        self.builder.add_from_file("passwordWindow.ui")#загружаем интерфейс из файла

        window = self.builder.get_object("passwordWindow")
        saveBtn = self.builder.get_object("saveButton")
        saveBtn.connect("clicked", self.saveButton_clicked)

        window.show_all()

    def saveButton_clicked(self, e):
        self.data_class.user_mail = self.builder.get_object("mailEntry").get_text()
        self.data_class.encode_password(self.builder.get_object("passwordEntry").get_text())

class EntryTable():#Класс для работы с entry
    def __init__(self, parent):
        self.now_row = 1
        self.valuesEntry = {}

        self.parent = parent#для обращения к родительскому главному классу

    def show_real_string(self, e, _):
        try:
            e.set_text(e.get_tooltip_text())
        except: pass

    def entry_calculation(self, obj, event=None):#считаем в заданном entry все арифметические операции
        text = obj.get_text().replace(" ", "")#Получаем текст из entry, убираем пробелы

        end_result = 0
        
        for letter in text:#перебираем все введённые символы
            if letter in "1234567890-=+*/." and text[-1] not in "-=+*/.":#если символ находиться в разрешённых, то перебираем следующие
                continue
            else:
                return#Если какой-то из символов не прошёл проверку, то ничего не происходит
        
        if len(text) == 0:
            obj.set_tooltip_text(None)

        if event == None or obj.get_tooltip_text() == None:
            obj.set_tooltip_text(text)

        try:
            end_result = str(eval(text))#расчёт
            obj.set_text(str(end_result))#изменяем entry
        except: pass

        self.parent.budgetEntry_signal(None)
        self.parent.calculateEndResult()#вызываем метод для рассчитывания ИТОГО

    def append_entry(self, text_1=None, text_2=None):#добавление несколько entry при нажатии на кнопку
        tmpEntry_1 = Gtk.Entry()
        tmpEntry_1.set_margin_end(3)

        if text_1 != None:
            tmpEntry_1.set_text(str(text_1).replace("=", ""))
            self.entry_calculation(tmpEntry_1)

        tmpEntry_2 = Gtk.Entry()

        tmpEntry_2.connect("activate", self.entry_calculation)
        tmpEntry_2.connect("focus-out-event", self.entry_calculation)
        tmpEntry_2.connect("button-press-event", self.show_real_string)

        if text_2 != None:
            tmpEntry_2.set_text(str(text_2).replace("=", ""))
            self.entry_calculation(tmpEntry_2)

        self.now_row += 1

        self.valuesEntry[tmpEntry_1] = tmpEntry_2

        self.parent.tableGrid.attach(tmpEntry_1, 0, self.now_row, 1, 1)
        self.parent.tableGrid.attach(tmpEntry_2, 1, self.now_row, 3, 1)

        self.parent.tableGrid.show_all()

        self.parent.data_class.tableEntrys = self.valuesEntry#обновляем список всех созданных статей расхода в класс Data для будущего сохранения

    def delete_entry(self):#удаление несколько entry при нажатии на кнопку
        if self.now_row > 1:
            self.now_row -= 1
        else:
            return

        self.parent.tableGrid.remove(list(self.valuesEntry.keys())[self.now_row-1])#Удаляем из интерфейса entry's
        self.parent.tableGrid.remove(list(self.valuesEntry.values())[self.now_row-1])
        
        self.valuesEntry.pop(list(self.valuesEntry.keys())[self.now_row-1], None)#удаляем из словаря entry:entry
        
        self.parent.window.queue_draw()#обновляем графический интерфейс


# MainGui()