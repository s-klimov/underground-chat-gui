import asyncio

from aiologger import Logger
from aiofile import async_open

from common import options, drawing

logger = Logger.with_default_handlers()


async def listen_messages(
    queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue,
    status_queue: asyncio.Queue,
    reader: asyncio.StreamReader,
    /,
) -> None:
    """
    Считывает сообщения из чата в консоль и в графический интерфейс.
        Позиционные аргументы:
                queue: очередь сообщений в чате
                watchdog_queue: очередь в которой отмечается каждое поступление сообщений в чат
                status_queue: очередь для отображения статуса соединений в графическом интерфейсе
                reader: поток чтения
    """

    status_queue.put_nowait(drawing.ReadConnectionStateChanged.ESTABLISHED)

    while data := await reader.readline():
        logger.debug(data.decode().rstrip())  # логируем полученное сообщение

        await save_messages(filepath=options.history, message=data.decode())

        if queue is not None:
            queue.put_nowait(data.decode().rstrip())

        if watchdog_queue is not None:
            watchdog_queue.put_nowait("Connection is alive. New message in chat")


async def save_messages(filepath: str, message: str):
    """
    Сохраняет сообщение в файл.
        Параметры:
                filepath: путь к файлу в котором сохраняются сообщения
                message: сообщение для сохранения в файле
    """

    async with async_open(filepath, "a") as afp:
        await afp.write(message)
