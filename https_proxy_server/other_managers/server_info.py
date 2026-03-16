import asyncio
import time
import os

class InfoManager():
    def __init__(self, server):
        self.server = server
    
    async def client_console(self, reader, writer):
        while True:
            writer.write(f"{self.server.users}\r\n\r\n".encode())#Инфо об подключенных пользователях
            await writer.drain()
            
            await asyncio.sleep(1)

    async def __output(self):
        while True:
            os.system("clear")#Очищаем консоль от прошлого вывода
            #Выводим всю нужную информацию об сервере
            print(f"Информация об подключенных пользователях:\n{self.server.users}\n")

            await asyncio.sleep(1)

    def start(self):
        asyncio.create_task(self.__output())#В потоке запускаем задачу