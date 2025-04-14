import json
import os
import asyncio
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from telethon import TelegramClient
from auth.login import login_user
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# 🔎 Функция извлечения и очистки ссылок из текста сообщения
def extract_links_from_message(message):
    if not message:
        return []
    links = set()
    links.update(re.findall(r'(https?://\S+)', message))
    links.update(re.findall(r'(?:https?://)?t\.me/[a-zA-Z0-9_]+', message))
    links.update(re.findall(r'@[\w\d_]+', message))

    clean_links = []
    for link in links:
        link = link.strip()
        if '](' in link:
            link = link.split('](')[-1]  # markdown-стиль: берём реальную ссылку
        if ')' in link:
            link = link.split(')')[0]  # удаляем закрывающую скобку
        link = re.sub(r'[^\w/:.@\-_%#?=&]+$', '', link)  # удаляем лишние символы в конце
        clean_links.append(link)

    return clean_links

# 📂 Загрузка уже сохранённых ссылок
def load_seen_links(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 💾 Сохранение новых ссылок
def save_seen_links(filepath, links_dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(links_dict, f, indent=2)

# 💾 Сохранение ссылок в .txt файл
def save_links_to_txt(filename, links):
    with open(filename, 'w', encoding='utf-8') as f:
        for link in sorted(links):
            f.write(link + '\n')
    return filename

# 📤 Отправка файла в Telegram-канал
async def send_txt_to_channel(client, channel_username_or_id, file_path):
    try:
        print(f"📤 Отправляю файл в канал: {channel_username_or_id}")
        entity = await client.get_entity(channel_username_or_id)

        try:
            # Проверка участия
            await client.get_participants(entity, limit=1)
        except:
            print(f"⚠️ Сессия не является участником канала: {channel_username_or_id}")
            print(f"❌ Пропускаю отправку файла: {file_path}")
            return

        await client.send_file(entity=entity, file=file_path)
        print(f"✅ Файл успешно отправлен: {file_path}")

    except Exception as e:
        print(f"❌ Ошибка при отправке файла в {channel_username_or_id}: {e}")

# 🔄 Основная логика парсера
async def process_all():
    with open("config.json", "r", encoding="utf-8") as file:
        parse_groups = json.load(file)

    seen_links = load_seen_links("seen_links.json")
    client = await login_user()

    async with client:
        for group_name, chats in parse_groups.items():
            print(f"\n📂 Начинаю обработку группы: {group_name}")
            new_links = set()
            group_seen = set(seen_links.get(group_name, []))

            for chat in chats:
                print(f"🔍 Получаю сообщения из чата: {chat}")
                try:
                    async for msg in client.iter_messages(chat, limit=50):
                        links = extract_links_from_message(msg.text or "")
                        for link in links:
                            if link not in group_seen:
                                new_links.add(link)
                                group_seen.add(link)
                except Exception as e:
                    print(f"⚠️  Ошибка при обработке чата {chat}: {e}")

            if new_links:
                file_path = f"parsed_{group_name}.txt"
                print(f"✅ Обработано {len(new_links)} новых ссылок")
                print(f"💾 Сохраняю в файл: {file_path}")
                save_links_to_txt(file_path, new_links)

                output_channel = os.getenv("OUTPUT_CHANNEL")
                await send_txt_to_channel(client, output_channel, file_path)
            else:
                print(f"ℹ️ Нет новых ссылок для группы: {group_name}")

            seen_links[group_name] = list(group_seen)

    save_seen_links("seen_links.json", seen_links)
    print("\n✅ Обработка завершена.")

# 🕒 Планировщик, запускающий парсинг каждый день в 18:00 по Москве
async def scheduler():
    print("⏳ Бот запущен. Ожидает 18:00 по московскому времени...")
    already_ran_today = False
        
    while True:
        now = datetime.now(ZoneInfo("Europe/Moscow"))
        if now.hour == 18 and not already_ran_today:
            print(f"\n🚀 {now.strftime('%Y-%m-%d %H:%M:%S')} - начинаю выполнение задачи...")
            await process_all()
            already_ran_today = True
        elif now.hour != 18:
            already_ran_today = False
        await asyncio.sleep(60)

# ▶️ Запуск
if __name__ == "__main__":
    asyncio.run(scheduler())
