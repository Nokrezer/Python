from settings.exceptions import *

import asyncio

class HeadersParser():
    def __init__(self, auth_manager, lock):
        self.auth_manager = auth_manager
        self.lock = lock
    
    async def get_connection_info(self, reader, server_users):
        headers = (await reader.readuntil(b"\r\n\r\n")).decode().split("\r\n")#Получаем заголовки, декодируем в строку и создаём массив заголовков

        if "CONSOLE_GET_DATA" in headers[0]:#Если запрос с заголовком консоли
            return "CONSOLE_GET_DATA", None, None, None#возвращаем в качестве хоста "CONSOLE_GET_DATA"
        # if "CONNECT" not in headers[0]:#Если запрос идёт из браузера, а не из прокси клиента отправляем ошибку
            # raise NotConnectionError("Method Not Allowed")
            
        for header in headers:#Перебираем заголовки, и парсим нужные
            if "Host" in header:
                host, port = header.replace("Host: ", "").split(':')
                port = int(port)

            elif "Proxy-Authorization" in header: #ИСПОЛЬЗУЕТСЯ BASE64
                auth_type, user_data = header.replace("Proxy-Authorization: ", "").split(" ")
                
                if user_data not in server_users:
                    server_users[user_data] = [0, 0]

                    async with self.lock:
                        user_speed = (await self.auth_manager.auth(user_data.encode()))["max_mbits"]
                        
                    server_users[user_data][1] = user_speed#Заносим скорость пользователя в массив, чтобы лишний раз не делать запросов к БД
                    continue
                    
                user_speed = server_users[user_data][1]
                
        return host, port, user_speed, user_data