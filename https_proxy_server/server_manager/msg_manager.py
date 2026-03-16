class MessageManager():
    async def send_message(self, writer, status_code, message=""):#Отправка обычный сообщений
        try:
            writer.write(f"HTTP/1.1 {status_code} {message}\r\n\r\n".encode())#Сообщений, статус код
            await asyncio.wait_for(writer.drain(), timeout=5.0)#Ждём завершения отправки сообщений
        except:
            pass

    async def send_error(self, writer, status_code, message=""):#Отправка ошибок
        await self.send_message(writer, status_code, message)

        try:
            writer.close()#закрываем подключение
            await writer.wait_closed()#Ждём закрытия
        except: pass