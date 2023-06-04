import asyncio
import json
import os
import re
import tkinter as tk
from tkinter import messagebox

from aiofile import LineReader, Writer, AIOFile
from aiologger import Logger
from dotenv import load_dotenv

ENV_FILE = '.env'
ACCOUNT_ENV = 'ACCOUNT'

logger = Logger.with_default_handlers(name='register-script')


async def register_user(user_name: str):
    load_dotenv()
    reader, writer = await asyncio.open_connection(os.getenv('HOST'), os.getenv('SENDING_PORT'))

    await reader.readline()  # пропускаем строку-приглашение ввода хэша аккаунта
    writer.write("\n".encode())  # вводим пустую строку, чтобы получить приглашение для регистрации
    await writer.drain()
    await reader.readline()  # пропускаем строку-приглашение ввода имени пользователя
    user_name = re.sub(r'\\n', ' ', user_name)
    writer.write(f"{user_name}\n".encode())
    await writer.drain()
    response = await reader.readline()  # получаем результат регистрации

    user = json.loads(response)

    if json.loads(response) is None:  # Если результат аутентификации null, то прекращаем выполнение скрипта
        raise ValueError(f'Ошибка регистрации пользователя. Ответ сервера {response}')
    await logger.info(f'Пользователь {user} зарегистрирован')

    # Записываем результат регистрации в env-файл
    lines = []
    async with AIOFile(ENV_FILE) as afp:
        async for line in LineReader(afp):
            lines.append(line)
    async with AIOFile(ENV_FILE, 'w') as afp:
        writer = Writer(afp)
        [await writer(line)
         if not line.startswith(ACCOUNT_ENV)  # TODO заменить условие на re.match
         else await writer(f'{ACCOUNT_ENV}={user["account_hash"]}\n')
         for line in lines]
        await afp.fsync()
    await logger.info(f'Хеш аккаунта сохранен в файле {ENV_FILE}')

    return user['nickname'], user['account_hash']


def draw_message(message: str):
    # hide main window
    root = tk.Tk()
    root.withdraw()

    # message box display
    messagebox.showinfo("Информация", message)


def register(input_field, root):
    text = input_field.get()
    if not text:
        return
    nickname, account_hash = asyncio.run(register_user(text))
    draw_message(f"Вы успешно зарегистрированы.\nВаш никнейм - {nickname}\nВаш токен - {account_hash}")
    root.quit()


def draw():
    root = tk.Tk()
    root.title('Регистрация в чате Майнкрафтера')

    root_frame = tk.Frame()
    root_frame.pack(fill="both", expand=True)

    input_frame = tk.Frame(root_frame)
    input_frame.pack(side="bottom", fill=tk.X)

    input_field = tk.Entry(input_frame)
    input_field.pack(side="left", fill=tk.X, expand=True)

    input_field.bind("<Return>", lambda event: register(input_field, root))

    send_button = tk.Button(input_frame)
    send_button["text"] = "Зарегистрировать"
    send_button["command"] = lambda: register(input_field, root)
    send_button.pack(side="left")

    root.mainloop()


if __name__ == '__main__':
    draw()
