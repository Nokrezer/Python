import os

HOST = "0.0.0.0"
PORT = 47000

#XRAY настройки
XRAY_HOST = "127.0.0.1"
XRAY_PORT = 10808
XRAY_PROTOCOL = "socks5"

#Работа с данными
BUFFER_SIZE = 1024 * 32#Буффер, сколько получаем за раз данных

#Настройки базы данных
SQL_HOST = ""
SQL_PORT = 3306
SQL_USER = ""
SQL_PASSWORD = os.environ.get("DB_PASSWORD")
SQL_DATABASE = ""