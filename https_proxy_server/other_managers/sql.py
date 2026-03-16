import aiomysql

from settings.config import *

class DataBaseManager():
    def __init__(self, host=SQL_HOST, port=SQL_PORT, user=SQL_USER, password=SQL_PASSWORD, now_database=SQL_DATABASE, data_base=None):
        self.data_base = data_base#База данных, к которой отдаём команды

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.now_database = now_database

    async def start(self):
        self.data_base = await aiomysql.create_pool(host=self.host, port=self.port,
                                    user=self.user, password=self.password,
                                    db=self.now_database, autocommit=True)
        
    async def __create(self, command, *args):#Общий метод для создания или добавление данных в БД
        async with self.data_base.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(command, args)
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def __get_data(self, command, *args, fetchall=False):#Общий метод, для получения любых данных с БД
        async with self.data_base.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(command, args)
                
                if fetchall:
                    return await cur.fetchall()

                return await cur.fetchone()
        
    async def get_user_mbits(self, user_data):#Получения максимальной скорости пользователя
        return await self.__get_data("SELECT max_mbits FROM users WHERE user_data_hash=%s", user_data)
    
    async def create_new_user(self, *args):
        await self.__create("INSERT INTO users VALUES (%s, %s, %s)", *args)
    
    async def get_user_display_name(self, user_data_hash):
        return await self.__get_data("SELECT user FROM users WHERE user_data_hash=%s", user_data_hash)
