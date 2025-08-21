# Telegram Parser

Скрипт для парсинга Telegram-групп и каналов с сохранением результатов в текстовые файлы.  
Подходит для сбора ссылок, сообщений или другой информации из чатов. Реализован механизм исключения дублей через файл `seen_links.json`.

## Возможности
- Парсинг сообщений из заданных групп и каналов.
- Сохранение результатов в `.txt` файлы (`parsed_group_1.txt`, `parsed_group_2.txt` и т.д.).
- Исключение повторов с помощью журнала обработанных элементов (`seen_links.json`).
- Гибкая настройка через `config.json`.

## Установка
```bash
git clone https://github.com/jorabeknazarmatov/telegram_parser.git
cd telegram_parser
pip install -r requirements.txt
```

## Настройка

Перед запуском отредактируйте файл `config.json`:
```json
{
  "groups": [
    "https://t.me/example_group",
    "https://t.me/example_channel"
  ],
  "limit": 100
}
```
- `groups` — список ссылок на чаты/каналы для парсинга.
- `limit` — максимальное количество сообщений для обработки.

## Запуск

```bash
python main.py
```
После запуска скрипт создаст файлы:
- ``parsed_group_1.txt`` … ``parsed_group_N.txt`` — собранные данные.
- ``seen_links.json`` — список уже обработанных сообщений/ссылок.

## Пример использования

- Указать в `config.json` ссылки на нужные Telegram-группы.
- Запустить `python main.py`.
- Получить результаты в текстовых файлах.
- Повторный запуск соберёт только новые сообщения (без дублей).

✍️ Автор: [@jorabeknazarmatov](https://github.com/jorabeknazarmatov)
