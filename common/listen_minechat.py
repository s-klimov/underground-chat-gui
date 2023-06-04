import asyncio

from aiofile import async_open

from common import logger, options, drawing

logger.name = "LISTENER"


async def listen_messages(
        queue: asyncio.Queue,
        watchdog_queue: asyncio.Queue,
        status_queue: asyncio.Queue,
        reader: asyncio.StreamReader,
        /,
) -> None:
    """Считывает сообщения из сайта в консоль"""

    status_queue.put_nowait(drawing.ReadConnectionStateChanged.ESTABLISHED)

    while data := await reader.readline():

        logger.debug(data.decode().rstrip())  # логируем полученное сообщение

        await save_messages(filepath=options.history, message=data.decode())

        if queue is not None:
            queue.put_nowait(data.decode().rstrip())

        if watchdog_queue is not None:
            watchdog_queue.put_nowait('Connection is alive. New message in chat')


async def save_messages(filepath: str, message: str):
    """Сохраняет сообщение в файл"""

    async with async_open(filepath, 'a') as afp:
        await afp.write(message)
