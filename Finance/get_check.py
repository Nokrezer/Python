import imaplib, email
from email.header import decode_header

import calendar
from variables import months

class GetCheck:
    def __init__(self):
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")#Создание тела обращения к почте
        self.login = None
        self.password = None
        self.data_class = None
    
    def login_(self):
        self.mail.login(self.login, self.password)#Вход в аккаунт
        self.mail.select('inbox')#Выбираем ящик "входящие"

    def get(self, shop):#в качестве аргумента передаём почту, от которой будем получать письма
        #Получаем письма за заданную дату от 
        now_month = months[self.data_class.now_month_index]
        now_year = self.data_class.now_year

        email_ids = self.mail.uid('search', None, 'ALL', None, 'SINCE', f"01-{now_month}-{now_year}", 'BEFORE', f"{calendar.monthrange(2025, self.data_class.now_month_index+1)[1]}-{now_month}-{now_year}", "FROM", shop)[1][0].split()
        
        msgs = []#список, который будет хранить в себе все чеки
        
        for mail_id in email_ids:#Перебор всех id сообщений от фикс прайса
            response = self.mail.uid('fetch', mail_id, '(RFC822)')[1]#Получаем письмо и его данные(отправка, время и тд)
            
            try:
                html = response[0][1].decode('utf-8')#Декодируем сообщение
                email_message = email.message_from_string(html)#Получаем объект типа email для дальнейшего парсинга сообщения
                
                msg_title = decode_header(email_message["Subject"])[0][0].decode()
                
                if "Бэст Прайс" not in msg_title and "АГРОТОРГ" not in msg_title and "КОРПОРАТИВНЫЙ ЦЕНТР ИКС" not in msg_title:#Если нет в загаловке письма "Бэст Прайс", "АГРОТОРГ" или ""
                    continue
                
                msgs.append(email_message)#Добавляем письмо в список
                
            except: continue

        # self.mail.logout()#завершаем сессию
        return msgs