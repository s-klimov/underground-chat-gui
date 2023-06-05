import json
import re

import asyncio
import socket

import anyio
from aiologger import Logger
from uuid import UUID

from common import options, drawing
from common.etc import InvalidToken

logger = Logger.with_default_handlers()

VERIFICATION_INTERVAL = 90 * 60


def authorize(account: UUID):
    """
    Декоратор авторизации в чате для отправки сообщений.
            Параметры:
                    account: хэш аккаунта для отправки сообщений в чат
    """

    def wrap(func):
        async def wrapped(*args):
            _, watchdog_queue, status_queue, reader, writer = args
            await connect_to_chat(account, watchdog_queue, status_queue, reader, writer)

            await func(*args)

            writer.close()
            status_queue.put_nowait(drawing.SendingConnectionStateChanged.CLOSED)

            await writer.wait_closed()

        return wrapped

    return wrap


@authorize(options.account)
async def send_messages(queue, watchdog_queue, status_queue, reader, writer, /):
    """
    Посылает сообщения пользователя в чат.
        Позиционные аргументы:
                queue: очередь, из которой считываются набранные пользователем сообщения
                watchdog_queue: очередь в которой отмечается каждое поступление сообщений в чат
                status_queue: очередь для отображения статуса соединений в графическом интерфейсе
                reader: поток чтения сообщения из чата
                writer: поток записи сообщений в чат
    """

    while message := await queue.get():
        message_line = "".join([re.sub(r"\\n", " ", message), "\n"]).encode()
        line_feed = "\n".encode()

        writer.writelines([message_line, line_feed])
        await writer.drain()
        watchdog_queue.put_nowait("Connection is alive. Message sent")


async def send_empty_message(
    watchdog_queue: asyncio.Queue,
    status_queue: asyncio.Queue,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    /,
):
    """
    Каждые VERIFICATION_INTERVAL секунд посылает на порт отправки сообщений пустое сообщение, чтобы
    поддерживать соединение с сервером активным.
        Позиционные аргументы:
                watchdog_queue: очередь в которой отмечается каждое поступление сообщений в чат
                status_queue: очередь для отображения статуса соединений в графическом интерфейсе
                reader: поток чтения сообщения из чата
                writer: поток записи сообщений в чат
    """
    while True:
        await asyncio.sleep(VERIFICATION_INTERVAL)
        line_feed = "\n".encode()
        try:
            writer.write(line_feed)
            await writer.drain()
        except (
            socket.gaierror,
            anyio.ExceptionGroup,
        ):  # если произошел обрыв соединения, пытаемся восстановить его
            await logger.info("Reconnecting to chat ...")
            await connect_to_chat(
                options.account, watchdog_queue, status_queue, reader, writer
            )
        else:
            await logger.info("Empty message sent to maintain the connection")


async def connect_to_chat(
    account: UUID,
    watchdog_queue: asyncio.Queue,
    status_queue: asyncio.Queue,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    /,
):
    status_queue.put_nowait(drawing.SendingConnectionStateChanged.INITIATED)

    await reader.readline()  # пропускаем строку-приглашение
    writer.write(f"{account}\n".encode())
    await writer.drain()
    response = await reader.readline()  # получаем результат аутентификации

    auth = json.loads(response)

    if (
        auth is None
    ):  # Если результат аутентификации null, то прекращаем выполнение скрипта
        raise InvalidToken(account)

    await logger.debug(
        f"Выполнена авторизация по токену {account}. Пользователь {auth['nickname']}"
    )

    status_queue.put_nowait(drawing.SendingConnectionStateChanged.ESTABLISHED)
    status_queue.put_nowait(drawing.NicknameReceived(auth["nickname"]))

    watchdog_queue.put_nowait("Connection is alive. Prompt before auth")
