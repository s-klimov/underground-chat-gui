# Подключаемся к подпольному чату Майнкрафт

Сервис для подключения к чату обмена кодами Майнкрафт

## Приступая к работе

Следуя этим инструкциям, вы получите копию проекта, которая будет запущена на вашем локальном компьютере для целей разработки и тестирования. Примечания о том, как развернуть проект в действующей системе, см. в разделе Развертывание.

### Предпосылки

Клонируйте проект на локальный компьютер

```commandline
git clone https://github.com/s-klimov/underground-chat-gui.git
```

Для работы сервиса у вас должны быть установлены:
* python версии 3.10 и выше
* poetry версии 1.4.x

### Развертывание

1. Установите в операционную систему пакет Tkinter. Пример для Debian-based Linux 
```commandline
sudo apt-get update
sudo apt-get install python-tk
```
2. Установите зависимости проекта
```commandline
poetry install
```
3. Активируйте локальное окружение
```commandline
poetry shell
```
4. Скопируйте файл .env.dist в .env и заполните его параметрами подключения.  

Назначение параметров:
* HOST -- хост сервера с чатом
* LISTEN_PORT -- порт для чтения сообщений сервера с чатом
* SENDING_PORT -- порт для отправки сообщений на сервер с чатом
* HISTORY -- путь к файлу для хранения истории чата
* ACCOUNT -- хэш аккаунта для написания сообщений в чат
* DISPLAY -- адрес виртуального дисплея для X-сервера (используется при запуске скрипта gui.py из контейнера)

Пример:  
* HOST=minechat.dvmn.org
* LISTEN_PORT=5000
* SENDING_PORT=5050
* HISTORY=chat.txt
* ACCOUNT=f007e00c-cd77-11ed-ad76-0242ac110002
* DISPLAY=172.26.32.1:0.0

5. Настройте запуск скрипта gui.py (если запускаете из контейнера)
[Видеоинструкция](https://youtu.be/W82jvmiaDtk?list=PLQMlgM71Ag24wooZwLXguA_Cx7rRXaVwa)
Пример запуска экранного сервера из ОС Windows:
```commandline
PS C:\Program Files (x86)\Xming> .\xming -ac
```

## Запуск проекта

### Графический интерфейс регистрации в чате
```commandline
python register.py
```
> порт для написания сообщения в чат должен отличаться от порта, указываемого для пролсушивания чата  
В качестве альтернативы вы можете указать свои параметры подключения при запуске:

После успешной регистрации пользователя хэш его аккаунта сохраняется в файле .env:
```commandline
cat .env
```
Чтобы получить справку по параметрам:
```commandline
python register.py --help
```

### Графический интерфейс прослушивания чата и отправки сообщений в чат
```commandline
python gui.py
```
В качестве альтернативы вы можете указать свои параметры подключения при запуске:
```commandline
python gui.py --host minechat.dvmn.org --listen_port 5000 --sending_port 5050 --history ~/minechat.history
```
Чтобы получить справку по параметрам:
```commandline
python gui.py --help
```

## Используемый стек

* [asyncio](https://docs.python.org/3/library/asyncio.html) - The library to write concurrent code using the async/await syntax used.  
* [anyio](https://anyio.readthedocs.io/en/3.x/) - AnyIO is an asynchronous networking and concurrency library that works on top of either asyncio or trio.    
* [poetry](https://python-poetry.org/docs/) - Dependency Management.  

## Авторы

* **Sergei Klimov** - [repos](https://github.com/s-klimov/)

## Лицензия

Проект разработан под лицензией MIT - см. [LICENSE](LICENSE) файл для подробного изучения.

## Благодарности

* [dvmn.org](https://dvmn.org/modules/)
