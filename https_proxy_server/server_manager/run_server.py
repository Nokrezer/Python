import asyncio
import ssl

from settings.config import *

class RunServer():
    def __init__(self, handler, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.handler = handler
    
    async def start(self):
        ssl_certs = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_certs.load_cert_chain('fullchain.pem', 'privkey.pem')

        loop = asyncio.get_running_loop()

        serve = await asyncio.start_server(self.handler, self.host, self.port, ssl=ssl_certs)#Создаём сервер

        async with server:
            await server.serve_forever()#Запускаем сервер в цикле

