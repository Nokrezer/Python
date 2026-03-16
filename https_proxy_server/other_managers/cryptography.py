import hashlib
import uuid
import os
import base64

class CryptographyManager():
    def __init__(self):
        pass
    
    def generate_name_password(self):#Метод для генерации имя пользователя и пароля для доступа
        return uuid.uuid4(), uuid.uuid4()
    
    def base64_user_data(self, user_data):#Метод для генерации строки base64 из данных name:password
        return base64.standard_b64encode(user_data.encode())
    
    def userdata_hash(self, base64_str):#Метод для генерации хэша из данных base64 строки
        return hashlib.sha256(base64_str).hexdigest()