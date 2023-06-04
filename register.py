import asyncio
import json
import logging
import os
import re
import tkinter as tk
from tkinter import messagebox

from anyio import run, create_task_group
from dotenv import load_dotenv


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
    logging.debug(f'Пользователь {user} зарегистрирован')

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

    nickname, account_hash = await register_user(text)  # FIXME Как запустить асинхронную функцию из синхронной с использованием пакета anyio
    draw_message(f"Вы успешно зарегистрированы.\nВаш никнейм - {nickname}\nВаш токен - {account_hash}")
    root.quit()


async def draw():

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


async def main():

    async with create_task_group() as tg:
        tg.start_soon(draw)


if __name__ == '__main__':
    run(main)
