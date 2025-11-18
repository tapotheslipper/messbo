# tgbot-project

## Телеграм Бот MessBo (@messbobot)

Проект студента Бердникова Александра С. группы ДИС-233/21.Б по написанию бота в мессенджере Telegram на языке программирования Python в связи с учебными нуждами.

Выбранная тема - доска объявлений для чатов.

---

Используемые ресурсы в процессе написания бота:

* [Статья на Хабр](https://habr.com/ru/articles/442800/)

* [Документация pyTelegramBotAPI](https://pytba.readthedocs.io/ru/latest/)

---

### Файловая структура

```
/bot/
    /__init__.py           # python пакетирование для /bot
    /board_manager.py      # логика создания и управления досками
    /handlers.py           # обработка сообщений в чате
    /run_bot.py            # запуск бота
    /utils.py              # вспомогательные функции
/config/
    /config.py             # конфигурация
/database/
    /__init__.py           # python пакетирование для /database
    /connection.py         # подключение к базе данных
/logs/
    /bot.log               # общие логи
/models/
    /__init__.py           # python пакетирование для /models
    /Board.py              # модель доски
    /BoardEntry.py         # модель записи на доске
    /User.py               # модель пользователя
/main.py                   # точка входа в бота
```
