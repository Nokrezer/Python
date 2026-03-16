import asyncio

from server_manager.run_server import RunServer
from server_manager.server import Server
from other_managers.sql import DataBaseManager

from other_managers.server_info import InfoManager

async def main():
    database_manager = DataBaseManager()#Менеджер работы с БД
    await database_manager.start()#Запуск менеджера
    server = Server(database_manager)#Основная логика сервера

    info_manager = InfoManager(server)#Менеджер для вывода информации в консоль об сервере
    info_manager.start()#Запускаем менеджер
    
    server_runner = RunServer(server.handler)#Запускатор сервера, передаём главную функцию-обработчик
    await server_runner.start()#Запуск сервера

if __name__ == "__main__":
    asyncio.run(main())