import asyncio
import logging
from pathlib import Path
from tkinter import TclError

from aiofile import async_open
from anyio import run, create_task_group

from common import drawing, options
from common.etc import InvalidToken, watch_for_connection, catching_exception
from common.sending import send_messages, send_empty_message
from common.listen_minechat import listen_messages


async def load_history(messages_queue: asyncio.Queue):

    if not Path(options.history).is_file():
        return

    async with async_open(options.history) as f:
        while message := await f.readline():
            messages_queue.put_nowait(message.rstrip())


@catching_exception(asyncio.exceptions.CancelledError, message="CancelledError", raise_on_giveup=True)
@catching_exception(TclError, message="окно программы закрыто", raise_on_giveup=False)
async def main():
    """Основная функция генерирующая очереди и потоки чтения и записи сообщений в чат майнкрафта """

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    reader, _ = await asyncio.open_connection(options.host, options.listen_port)
    reader_w, writer = await asyncio.open_connection(options.host, options.sending_port)

    async with create_task_group() as tg:

        tg.start_soon(drawing.draw, messages_queue, sending_queue, status_queue)
        tg.start_soon(load_history, messages_queue)
        tg.start_soon(listen_messages, messages_queue, watchdog_queue, status_queue, reader)
        tg.start_soon(send_messages, sending_queue, watchdog_queue, status_queue, reader_w, writer)
        tg.start_soon(watch_for_connection, watchdog_queue, status_queue)
        tg.start_soon(send_empty_message, writer)


if __name__ == '__main__':

    try:
        run(main)
    except InvalidToken as e:
        logging.error(str(e))
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        # NOTE CancelledError перехватываем повторно для корректного завершения работы корутин
        pass
    finally:
        logging.info('Работа сервера остановлена')
