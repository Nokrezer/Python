import asyncio
from python_socks.async_.asyncio import Proxy

from settings.config import *

from settings.exceptions import *

from other_managers.sql import DataBaseManager
from other_managers.user_auth import AuthManager
from other_managers.cryptography import CryptographyManager
from server_manager.msg_manager import MessageManager
from server_manager.headers_parser import HeadersParser
from other_managers.server_info import InfoManager

class Server():
    def __init__(self, database_manager, msg_manager=None, auth_manager=None, crypt_manager=None, info_manager=None, buffer_size=BUFFER_SIZE, xray_host=XRAY_HOST, xray_port=XRAY_PORT, xray_protocol=XRAY_PROTOCOL):
        #Работа со скоростью сервера, буффером и тд
        self.buffer_size = buffer_size#Сколько данных сервер читает, в байтах
        #Данные xray подключения
        self.xray_host = xray_host
        self.xray_port = xray_port
        self.xray_protocol = xray_protocol
        #Используемые менеджеры
        self.database_manager = database_manager#Менеджер работы с БД
        self.crypt_manager = crypt_manager or CryptographyManager()#Менеджер криптографии
        self.auth_manager = auth_manager or AuthManager(self.database_manager, self.crypt_manager)#Менеджер для авторизации пользователей
        self.msg_manager = msg_manager or MessageManager()#Менеджер для отсылки сообщений и кодов состояний клиенту
        self.info_manager = info_manager or InfoManager(self)
        #Данные пользователей
        self.users = {}#Храним данные об пользователях. {"Данные входа пользоватедя": [кол-во потоков пользователя, максимальная скорость пользователя]}
        #Блокировка потока
        self.lock = asyncio.Lock()

        self.headers_parser = HeadersParser(self.auth_manager, self.lock)#Класс для парсинга заголовков
    
    async def pipe(self, reader, writer, user_data, user_speed, host):#Туннель, для передачи данных
        while True:
            try:
                data = await asyncio.wait_for(reader.read(self.buffer_size), timeout=5)
                print(f"{host} readed")

                if not data:
                    break
                
                writer.write(data)
                await asyncio.wait_for(writer.drain(), timeout=5)
                
                #Минимальная гарантированная скорость, если много потоков, тогда на каждый поток будет стандартная скорость пользователя деленая на 4(1/4)
                #base_speed = max(user_speed, user_speed//4 * self.users[user_data][0])

                #Расчет скорости, выставляем 0.0001 если расчёт скорости получиться меньше этого числа. 
                #Так как asyncio.sleep не может обработать число маньше 0.0001
                #для рассчёта обычной скорости, берем размер пакета и делим на получившуюся скорость, умножаем на количество потоков
                #rate_limit = max(0.0001, (len(data)*8)/(base_speed * 1_000_000)*self.users[user_data][0])
                
                #await asyncio.sleep(rate_limit)
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                break
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass

    async def handler(self, reader, writer):#Главный обработчик запросов
        try:
            host, port, user_speed, user_data = await self.headers_parser.get_connection_info(reader, self.users)#Получаем из заголовков все данные

            if host == "CONSOLE_GET_DATA":#Если заместо хоста строка CONSOLE_GET_DATA, то направляем в менеджер для передачи данных в консоль клиента и завершаем
                await self.info_manager.client_console(reader, writer)
                return

            async with self.lock:
                self.users[user_data][0] = self.users[user_data][0] + 1 if user_data in self.users else 1#если уже были открыты потоки у пользователя, то заносим ещё один, если нет - тогда 1

        except UserNotFound as e:
            await self.msg_manager.send_error(writer, 401, e)
            return
        except NotConnectionError as e:
            await self.msg_manager.send_error(writer, 405, e)
            return
        except Exception as e:
            await self.msg_manager.send_error(writer, 400, e)
            return
        
        try:
            proxy = Proxy.from_url(f'{self.xray_protocol}://{self.xray_host}:{self.xray_port}', rdns=True)#Создаём прокси подключение к xray ядру
            sock = await proxy.connect(dest_host=host, dest_port=port)#Подключаемся через прокси к хосту к которому клиент делает запрос
            remote_reader, remote_writer = await asyncio.open_connection(sock=sock)#Создаём подключение asyncio с использованием прокси

            await self.msg_manager.send_message(writer, 200, "OK")

            await asyncio.gather(
                self.pipe(reader, remote_writer, user_data, user_speed, host),
                self.pipe(remote_reader, writer, user_data, user_speed, host)
            )

            remote_writer.close()
            await asyncio.wait_for(remote_writer.wait_closed(), timeout=2.0)

        except Exception as e:
            print("EXCEPTION", e)
            try:
                await self.msg_manager.send_error(writer, 500, f"Connection error: {e}")
            except: pass
        
        finally:
            try:
                writer.close()#закрываем подключение
                await writer.wait_closed()#Ждём закрытия
            except: pass
            
            async with self.lock:
                self.users[user_data][0] -= 1

                if self.users[user_data][0] <= 0:
                    del self.users[user_data]
            
           