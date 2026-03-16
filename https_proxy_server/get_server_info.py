import asyncio
import json
import os
import ssl

from other_managers.cryptography import CryptographyManager
from other_managers.sql import DataBaseManager

HOST = ""
PORT = 47000
BUFFER_SIZE = 1024

class ServerRemoteConsole():#Класс, для получения информации об сервере на консоли
    def __init__(self, host=HOST, port=PORT, buffer_size=BUFFER_SIZE, crypt_manager=None, database_manager=None):
        self.reader = None
        self.writer = None

        self.host = host
        self.port = port

        self.buffer_size = buffer_size
        self.crypt_manager = crypt_manager or CryptographyManager()
        self.database_manager = database_manager

    async def init(self):
        ssl_certs = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_certs.check_hostname = False
        ssl_certs.load_cert_chain('fullchain.pem', 'privkey.pem')

        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=ssl_certs)

        self.database_manager = self.database_manager or DataBaseManager()
        await self.database_manager.start()

    async def start(self):
        while True:
            try:
                self.writer.write(b"CONSOLE_GET_DATA\r\n\r\n")
                await self.writer.drain()#Ждём закрытия записи

                data = await self.reader.read(self.buffer_size)
                print(data)
                users_connected = json.loads(data.decode().replace("'", '"'))
                
                os.system("clear")
                print(f"Пользователей подключено: {len(users_connected)}")#выводим данные об подключенниях
                for user in users_connected:
                    user_data_hash = self.crypt_manager.userdata_hash(user.encode())#Получаем хэш из данных подключения
                    user_name = await self.database_manager.get_user_display_name(user_data_hash)#Получаем из БД имя пользоватедя

                    print(f"Пользователь: {user_name}; Подключений(потоков): {users_connected[user][0]}; Максимальная скорость потоков: {users_connected[user][1]}")
            except:
                pass

async def main():
    controller = ServerRemoteConsole()
    await controller.init()
    await controller.start()

if __name__ == "__main__":
    asyncio.run(main())