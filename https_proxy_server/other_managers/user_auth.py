from settings.exceptions import *

class AuthManager():
    def __init__(self, database_manager, crypt_manager):
        self.database_manager = database_manager
        self.crypt_manager = crypt_manager
    
    async def auth(self, auth_data):#auth_data - строка base64, которая содержить имя пользователя:пароль
        data_hash = self.crypt_manager.userdata_hash(auth_data)#Получаем хэш строки base64(пользовательское имя и пароль)
        speed_mbits = await self.database_manager.get_user_mbits(data_hash)
        
        if not speed_mbits:#Если метод вернул None, то выкидываем ошибку
            raise UserNotFound("Пользователь не найден")
        
        return speed_mbits
