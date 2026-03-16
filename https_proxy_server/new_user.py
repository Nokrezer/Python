from other_managers.sql import DataBaseManager
from other_managers.cryptography import CryptographyManager

import uuid
import base64
import asyncio

class UserManager():#Менеджер, для создания нового пользователя в БД
    def __init__(self, database_manager=None, cryptography_manager=None):
        self.database_manager = database_manager or DataBaseManager()
        self.cryptography_manager = cryptography_manager or CryptographyManager()
    
    async def create(self):
        user_name = input("Введите имя пользователя(Можно пропустить): ")

        access_name, password = self.cryptography_manager.generate_name_password()#Генерируем имя пользователя(для доступа) и пароль
        user_full_data = f"{access_name}:{password}"
        base64_user_data = self.cryptography_manager.base64_user_data(user_full_data)#Возвращаем строку base64 из данных пользователя
        data_hash = self.cryptography_manager.userdata_hash(base64_user_data)#Создаём хэш из строки base64

        try:
            max_mbits = int(input("Максимальная скорость интернета(Мбит/с) пользователя(Базовое значение 75): "))
        except:
            max_mbits = 75

        await self.database_manager.create_new_user(user_name, data_hash, max_mbits)

        print("="*10, "Сылка пользователя", "="*10)
        print(f"https://{user_full_data}@HOST:47000/#{user_name}")


async def main():
    database_manager = DataBaseManager()
    await database_manager.start()

    users_manager = UserManager(database_manager)
    await users_manager.create()

if __name__ == "__main__":
    asyncio.run(main())