import email
from bs4 import BeautifulSoup

def get_full_msg(msg):
    full_msg = ""

    for msg_part in msg.walk():#Перебираем массив байтов сообщения
        try:
            full_msg += msg_part.get_payload(decode=True).decode('utf-8')#Декодируем части сообщения и записываем в переменную
        except: pass

    return full_msg

def fixPrice_check(msg):
    parser = BeautifulSoup(get_full_msg(msg), 'html.parser')#Создаём объект для парсинга 
    
    for i in parser.find_all("tr"):
        try:
            if "ИТОГО" in i.find("span").get_text():#Ищем среди каждого объекта слово ИТОГО
                return float(i.find_all("td")[1].get_text())
        except: pass

def pyatorochka_check(msg):
    parser = BeautifulSoup(get_full_msg(msg), 'html.parser')#Создаём объект для парсинга
    
    for i in parser.find_all("tr"):
        if "Итог" in i.find("td"):
            return float(i.find_all("td")[1].get_text())