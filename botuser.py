import sys
import telebot
import sqlite3
import time
import pytz
from datetime import datetime as dt, timedelta
from telebot import TeleBot
from telebot import types
from telebot.types import Message
from difflib import SequenceMatcher
import logging
import json
import re
import os
import random 
import psutil
from ping3 import ping
from core import Server
import datetime
import days
import threading
from termcolor import colored
import pyfiglet
from database.DataBase import DataBase
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ascii_banner = pyfiglet.figlet_format("ZoxDev")
colored_banner = colored(ascii_banner, color='red')
print(colored_banner)
print(colored(f"Bot created by @ZoxDev", 'red'))
print(colored(f"Version 3.2.2", 'red'))
print(colored(f"started!", 'green'))

# Хуета
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Дебаг хуйня
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.WARNING)

# Хуйня
for handler in urllib3_logger.handlers[:]:
    urllib3_logger.removeHandler(handler)

# Хуйня
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOTUSER_TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "Missing env var BOTUSER_TELEGRAM_TOKEN. "
        "Set it before running, e.g. BOTUSER_TELEGRAM_TOKEN='123:ABC...' python3 botuser.py"
    )

bot = telebot.TeleBot(BOT_TOKEN)

# Telegram owner/admin IDs
OWNER_TELEGRAM_ID = int(os.getenv("BOTUSER_OWNER_ID", "6721976368"))
admins = {OWNER_TELEGRAM_ID, 7014105936, 7745508536}
tehs = set()
managers = set()  # 1755600329
creator1 = set()
creator2 = set()
creator3 = set()
 
def init_db():
    os.makedirs("database/Player", exist_ok=True)
    conn = sqlite3.connect('users.db')  # Название созданной бд
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accountconnect
        (lowID INTEGER PRIMARY KEY, trophies INTEGER, name TEXT, id_user INTEGER, token TEXT, username TEXT)
    ''')
    conn.commit()
    conn.close()
    
init_db()

# Стартуй сука
@bot.message_handler(commands=['start'])
def start(message):
    response = (
        'Добро пожаловать в бота!\n\n'
        '⛔Команды:\n\n'
        '/name [name] - Узнать об аккаунте\n'
        '/info [id] - Узнать об аккаунте.\n'
        '/connect [id] [token] - Привязать аккаунт.\n'
        '/profile - Просмотр профиля.\n'
        '/unlink - Отвязать аккаунт.\n'
        '/top - Посмотреть топы.\n'
        '/recovery [old id] [new token] - Востановить аккаунт.\n\n'
        '/admin - Админ команды\n'
        '/tehadmin - Тех.Админ команды\n'
        '/manager - Менеджер команды\n\n'
        '/creator - Контент мейкеры\n'
    )
    try:
        bot.reply_to(message, response)
    except Exception as e:
        logger.error(f"Failed to reply to /start command: {e}")

# Админ команды
@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    try:
        bot.reply_to(message, (
            'Admin Commands!\n\n⛔ Команды:\n\n'
            '/toggle_trophies [false/true] - Двойные трофеи.\n'
            '/toggle_tokens [false/true] - Двойные токены.\n'
            '/vip [id] - Дать ВИП.\n'
            '/unvip [id] - Забрать ВИП.\n'
            '/settokens [id] [amount] - Установить токены.\n'
            '/addtokens [id] [amount] - Добавить токены.\n'
            '/untokens [id] [amount] - Забрать токены.\n'
            '/setgems [id] [amount] - Установить гемы.\n'
            '/addgems [id] [amount] - Добавить гемы.\n'
            '/ungems [id] [amount] - Забрать гемы.\n'
            '/setgold [id] [amount] - Установить золото.\n'
            '/addgold [id] [amount] - Добавить золото.\n'
            '/ungold [id] [amount] - Забрать золото.\n'
            '/unroom - Очистить румы.\n'
            '/teh - Тех. Перерыв.\n'
            '/unteh - Убрать Тех. Перерыв.\n'
            '/ban [id] - Забанить.\n'
            '/unban [id] - Разбанить.\n'
            '/code [code] - Создать код.\n'
            '/code_list - Список кодов.\n'
            '/uncode [code] - Удалить код.\n'
            '/autoshop - Автомагазин.\n'
            '/upshop - Обновить магазин.\n'
            '/rename [id] [new_name] - Изменить имя.\n'
            '/theme [theme] - Тема.\n'
            '/status [status] - Статус.\n'
            '/resetclubs - Удалить клубы.\n'
            '/bd - Сохранить базу данных сервера.\n'
            '/delete - [id] Удалить аккаунт.\n'
            '/addadmin [telegramid] - Добавить админа.\n'
            '/addteh [telegramid] - Добавить Тех.Админа.\n'
            '/addmanager [telegramid] - Добавить Менеджера.\n'
            '/token [id] - Просмотреть токены.\n'
            '/account [id] [token] - Востановить аккаунт.\n'
            '/resetbp [id] - Сброс BrawlPass.\n'
            '/addpass [id] - Дать BrawlPass.\n'
            '/removepass [id] - Забрать BrawlPass.\n'
            '/antiddos - Очистка.\n'
            '/new_offer - Новая акция от 11 до беск.\n'
            '/remove_offer - Удалить акцию с 11.\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /admin command: {e}")
       
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Если файл не найден, возвращаем пустой словарь
    except json.JSONDecodeError:
        return {}

# Функция для сохранения конфигурации в файл config.json
def save_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

# Включение и выключение удвоения трофеев
@bot.message_handler(commands=['toggle_trophies'])
def toggle_trophies(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    # Загружаем текущую конфигурацию
    config = load_config()

    # Проверяем текущее состояние удвоения трофеев
    if config.get("DoubleTrophiesEvent", False):
        config["DoubleTrophiesEvent"] = False
        bot.send_message(message.chat.id, "✅ Удвоение трофеев отключено.")
    else:
        config["DoubleTrophiesEvent"] = True
        bot.send_message(message.chat.id, "✅ Удвоение трофеев включено.")
    
    # Сохраняем обновленную конфигурацию
    save_config(config)

# Включение и выключение удвоения токенов
@bot.message_handler(commands=['toggle_tokens'])
def toggle_tokens(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    # Загружаем текущую конфигурацию
    config = load_config()

    # Проверяем текущее состояние удвоения токенов
    if config.get("DoubleTokensEvent", False):
        config["DoubleTokensEvent"] = False
        bot.send_message(message.chat.id, "✅ Удвоение токенов отключено.")
    else:
        config["DoubleTokensEvent"] = True
        bot.send_message(message.chat.id, "✅ Удвоение токенов включено.")
    
    # Сохраняем обновленную конфигурацию
    save_config(config)
    
    
@bot.message_handler(func=lambda message: message.text.startswith("/allquest"))
def allquest(message):
    chat_id = message.chat.id
    if chat_id in admins:
        # Устанавливаем соединение с базой данных
        conn = sqlite3.connect("database/Player/plr.db")
        cursor = conn.cursor()

        # Обрабатываем каждую запись в таблице plrs
        cursor.execute("SELECT lowID, brawlerData, trophies FROM plrs")
        player_data = cursor.fetchall()

        for player in player_data:
            lowID = player[0]
            data = json.loads(player[1])
            unlocked = [int(key) for key, value in data['UnlockedBrawlers'].items() if value == 1]
            unlocked_brawlers = random.choice([unlocked])
            quests = []

            trophies = player[2]

            if trophies < 300:
                continue  # Пропускаем генерацию квестов, если трофеев меньше 300

            # Проверяем количество квестов у игрока
            cursor.execute("SELECT quests FROM plrs WHERE lowID = ?", (lowID,))
            current_quests = json.loads(cursor.fetchone()[0])
            if len(current_quests) >= 18:
                # Удаляем все текущие квесты
                current_quests = []
                cursor.execute("UPDATE plrs SET quests = ? WHERE lowID = ?", (json.dumps(current_quests), lowID))
                conn.commit()

            for i in range(2):  # 2 ежедневных квеста
                brawler_id = random.choice(unlocked_brawlers) #0, 6, 3
                win_count = 3
                if win_count == 3:
                    prize = 100
                    mt = 1
                    qt = 1
                    gm = 0
                    bpex = False
                quest = {"id": brawler_id, "state": 0, "win_count": win_count, "counts": 0, "prize": prize, "QT": qt, "GM": gm, "MT": mt, "BPEX": bpex}
                quests.append(quest)

            # Обновляем поле quests для текущего игрока
            current_quests.extend(quests)
            cursor.execute("UPDATE plrs SET quests = ? WHERE lowID = ?", (json.dumps(current_quests), lowID))
            conn.commit()

        conn.close()
        bot.send_message(chat_id, "Квесты успешно сгенерированы для всех игроков!")

@bot.message_handler(func=lambda message: message.text.startswith("/clearquests"))
def clearquests(message):
    chat_id = message.chat.id
    if chat_id in admins:
        # Устанавливаем соединение с базой данных
        conn = sqlite3.connect("database/Player/plr.db")
        cursor = conn.cursor()

        # Обрабатываем каждую запись в таблице plrs
        cursor.execute("SELECT lowID FROM plrs")
        player_data = cursor.fetchall()

        for player in player_data:
            lowID = player[0]

            # Очищаем квесты у игрока
            cursor.execute("UPDATE plrs SET quests = ? WHERE lowID = ?", (json.dumps([]), lowID))
            conn.commit()

        conn.close()
        bot.send_message(chat_id, "Все квесты успешно очищены у всех игроков!")
    
@bot.message_handler(func=lambda message: message.text.startswith("/notif"))
def addNotif(message):
    chat_id = message.chat.id
    if chat_id in admins:  # Проверка, является ли пользователь администратором
        # Проверяем, хочет ли администратор выдать нотификацию всем
        if message.text.startswith("/notifall"):
            match = re.match(r'/notifall\s+(\d+)\s+"(.+?)"\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', message.text)

            if match:
                param2 = int(match.group(1))  # ID уведомления
                param3 = match.group(2)  # Описание
                param4 = int(match.group(3))  # ID бравлера
                param5 = int(match.group(4))  # ID скина
                param6 = int(match.group(5))  # Количество гемов

                # Вызываем метод для добавления уведомления всем игрокам
                result = DataBase().addNotificationToAll(param2, param3, param4, param5, param6)

                bot.send_message(chat_id, result)
            else:
                bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /notifall <айди нотифа> \"описание\" <айди бравлера> <айди скина> <кол-во гемов>")

        else:
            match = re.match(r'\/notif\s+(\d+)\s+(\d+)\s+"(.+?)"\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', message.text)

            if match:
                param1 = int(match.group(1))  # ID игрока
                param2 = int(match.group(2))  # ID уведомления
                param3 = match.group(3)  # Описание
                param4 = int(match.group(4))  # ID бравлера
                param5 = int(match.group(5))  # ID скина
                param6 = int(match.group(6))  # Количество гемов

                result = DataBase().addNotification(param1, param2, param3, param4, param5, param6)
                
                bot.send_message(chat_id, result)
            else:
                bot.send_message(chat_id, "Айди: \n\n 1 - Скины\n 2 - Боец\n 3 - Гемы\n 4 - Сбросс сезона\n 5 - Старпоинты(скоро)\n 6 - Пины(скоро)\n 7 - Ящики(скоро)")
                bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /notif <айди игрока> <айди нотифа> \"описание\" <айди бравлера> <айди скина> <кол-во гемов>")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав!")

        
@bot.message_handler(func=lambda message: message.text.startswith("/notif"))
def addNotif(message):
    chat_id = message.chat.id
    if chat_id in admins:  # Проверка, является ли пользователь администратором
        match = re.match(r'\/notif\s+(\d+)\s+(\d+)\s+"(.+?)"\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', message.text)
        
        if match:
            param1 = int(match.group(1))  # ID игрока
            param2 = int(match.group(2))  # ID уведомления
            param3 = match.group(3)  # Описание
            param4 = int(match.group(4))  # ID бравлера
            param5 = int(match.group(5))  # ID скина
            param6 = int(match.group(6))  # Количество гемов

            result = DataBase().addNotification(param1, param2, param3, param4, param5, param6)
            
            bot.send_message(chat_id, result)
        else:
            bot.send_message(chat_id, "Айди: \n\n 1 - Скины\n 2 - Боец\n 3 - Гемы\n 4 - Золото(скоро)\n 5 - Старпоинты(скоро)\n 6 - Пины(скоро)\n 7 - Ящики(скоро)")
            bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /notif <айди игрока> <айди нотифа> \"описание\" <айди бравлера> <айди скина> <кол-во гемов>")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав!")

@bot.message_handler(func=lambda message: message.text.startswith("/unnotif"))
def removeNotif(message):
    chat_id = message.chat.id
    if chat_id in admins:  # Проверка прав администратора
        match = re.match(r'/unnotif\s+(\d+)\s+(\d+)', message.text)

        if match:
            player_id = int(match.group(1))
            notif_index = int(match.group(2))

            db = DataBase()  # Создаём объект базы данных
            result = db.removeNotification(player_id, notif_index)  # Удаляем уведомление

            bot.send_message(chat_id, result)  # Отправляем результат удаления
        else:
            bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /unnotif <айди игрока> <номер уведомления>")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав!")
        
@bot.message_handler(commands=['tehadmin'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь Тех.Админом!")
        return

    try:
        bot.reply_to(message, (
            'Teh.Admin Commands!\n\n⛔ Команды:\n\n'
            '/toggle_trophies [false/true] - Двойные трофеи.\n'
            '/toggle_tokens [false/true] - Двойные токены.\n'
            '/vip [id] - Дать ВИП.\n'
            '/unvip [id] - Забрать ВИП.\n'
            '/settokens [id] [amount] - Установить токены.\n'
            '/addtokens [id] [amount] - Добавить токены.\n'
            '/untokens [id] [amount] - Забрать токены.\n'
            '/setgems [id] [amount] - Установить гемы.\n'
            '/addgems [id] [amount] - Добавить гемы.\n'
            '/ungems [id] [amount] - Забрать гемы.\n'
            '/setgold [id] [amount] - Установить золото.\n'
            '/addgold [id] [amount] - Добавить золото.\n'
            '/ungold [id] [amount] - Забрать золото.\n'
            '/unroom - Очистить румы.\n'
            '/teh - Тех. Перерыв.\n'
            '/unteh - Убрать Тех. Перерыв.\n'
            '/ban [id] - Забанить.\n'
            '/unban [id] - Разбанить.\n'
            '/code [code] - Создать код.\n'
            '/code_list - Список кодов.\n'
            '/uncode [code] - Удалить код.\n'
            '/autoshop - Автомагазин.\n'
            '/upshop - Обновить магазин.\n'
            '/rename [id] [new_name] - Изменить имя.\n'
            '/theme [theme] - Тема.\n'
            '/status [status] - Статус.\n'
            '/resetclubs - Удалить клубы.\n'
            '/delete - [id] Удалить аккаунт.\n'
            '/addmanager [telegramid] - Добавить Менеджера.\n'
            '/token [id] - Просмотреть токены.\n'
            '/account [id] [token] - Востановить аккаунт.\n'
            '/resetbp [id] - Сброс BrawlPass.\n'
            '/addpass [id] - Дать BrawlPass.\n'
            '/removepass [id] - Забрать BrawlPass.\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /tehadmin command: {e}")

@bot.message_handler(commands=['manager'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in managers and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь Менеджером!")
        return

    try:
        bot.reply_to(message, (
            'Manager Commands!\n\n⛔ Команды:\n\n'
            '/vip [id] - Дать ВИП.\n'
            '/unvip [id] - Забрать ВИП.\n'
            '/settokens [id] [amount] - Установить токены.\n'
            '/addtokens [id] [amount] - Добавить токены.\n'
            '/untokens [id] [amount] - Забрать токены.\n'
            '/addgems [id] [amount] - Добавить гемы.\n'
            '/ungems [id] [amount] - Забрать гемы.\n'
            '/addgold [id] [amount] - Добавить золото.\n'
            '/ungold [id] [amount] - Забрать золото.\n'
            '/resetbp [id] - Сброс BrawlPass.\n'
            '/addpass [id] - Дать BrawlPass.\n'
            '/removepass [id] - Забрать BrawlPass.\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /manager command: {e}")

@bot.message_handler(commands=['creator'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in managers and user_id not in tehs and user_id not in creator1 and user_id not in creator2 and user_id not in creator3:
        bot.send_message(message.chat.id, "❌ Вы не являетесь Контент мейкером!")
        return

    try:
        bot.reply_to(message, (
            'Какой ваш уровень?!\n\n⛔ Команды:\n\n'
            '/creator1 - 1 Уровень\n'
            '/creator2 - 2 Уровень\n'
            '/creator3 - 3 Уровень\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /creator command: {e}")
        
REWARD_INTERVAL = 604800  # 1 неделя в секундах епта

rewards_running = False
last_distribution_time = 0

ENABLE_REWARD_DISTRIBUTION = os.getenv("ENABLE_REWARD_DISTRIBUTION", "0") == "1"

def _get_tg_user_id_by_lowid(lowID: int):
    """Map game lowID -> Telegram user id (id_user) via users.db."""
    try:
        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_user FROM accountconnect WHERE lowID = ?", (lowID,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.error(f"Error reading users.db mapping: {e}")
        return None

def distribute_rewards():
    global last_distribution_time
    while True:
        if not ENABLE_REWARD_DISTRIBUTION:
            time.sleep(5)
            continue

        current_time = time.time()
        
        if current_time - last_distribution_time >= REWARD_INTERVAL:  # ну тут интервал
            try:
                with sqlite3.connect('database/Player/plr.db') as plr_conn:
                    plr_cursor = plr_conn.cursor()
                    plr_cursor.execute("SELECT lowID FROM plrs")
                    creators = plr_cursor.fetchall()

                    for (lowID,) in creators:
                        gems, gold, BPTOKEN = get_rewards(lowID)
                        
                        if gems > 0 or gold > 0 or BPTOKEN > 0:
                            plr_cursor.execute(
                                "UPDATE plrs SET gems = gems + ?, gold = gold + ?, BPTOKEN = BPTOKEN + ? WHERE lowID = ?",
                                (gems, gold, BPTOKEN, lowID)
                            )
                            plr_conn.commit()

                            message = f"🎉 Вы получили награду: {gems} Гемов, {gold} Золота, {BPTOKEN} Токенов!"
                            tg_user_id = _get_tg_user_id_by_lowid(int(lowID))
                            if tg_user_id:
                                bot.send_message(tg_user_id, message)
                admin_message = "Сервер был перезапущен/награда выдана!"
                for admin_id in admins:
                    bot.send_message(admin_id, admin_message)

                last_distribution_time = current_time
            
            except Exception as e:
                logger.error(f"Error in distributing rewards: {e}")

        time.sleep(1)

def get_rewards(lowID): #награды контенткрейтерам
    if lowID in creator1:
        return 10, 50, 100
    elif lowID in creator2:
        return 20, 150, 300
    elif lowID in creator3:
        return 50, 300, 750
    return 0, 0, 0

@bot.message_handler(commands=['content'])
def content_command(message):
    user_id = message.from_user.id
    if user_id in (admins | tehs | managers):
        threading.Thread(target=immediate_distribution, daemon=True).start()
        bot.reply_to(message, "✅ Награды контентмейкерам были выданы немедленно.")
    else:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды!")

def immediate_distribution():
    try:
        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()
            plr_cursor.execute("SELECT lowID FROM plrs")
            creators = plr_cursor.fetchall()

            for (lowID,) in creators:
                gems, gold, BPTOKEN = get_rewards(lowID)
                
                if gems > 0 or gold > 0 or BPTOKEN > 0:
                    plr_cursor.execute(
                        "UPDATE plrs SET gems = gems + ?, gold = gold + ?, BPTOKEN = BPTOKEN + ? WHERE lowID = ?",
                        (gems, gold, BPTOKEN, lowID)
                    )
                    plr_conn.commit()

                    message = f"🎉 Вы получили награду: {gems} Гемов, {gold} Золота, {BPTOKEN} Токенов!"
                    tg_user_id = _get_tg_user_id_by_lowid(int(lowID))
                    if tg_user_id:
                        bot.send_message(tg_user_id, message)

    except Exception as e:
        logger.error(f"Error in immediate distribution: {e}")

def create_creator_handler(level, gems, gold, BPTOKEN):
    level = set(level)  # Уровень контенмейкерсва

    def creator_command(message):
        user_id = message.from_user.id
        
        if user_id not in (admins | managers | tehs | level):
            bot.send_message(message.chat.id, "❌ Вы не являетесь Контент мейкером!")
            return

        try:
            with sqlite3.connect('users.db') as users_conn:
                users_cursor = users_conn.cursor()
                users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
                row = users_cursor.fetchone()

                if row:
                    lowID = row[0]
                    with sqlite3.connect('database/Player/plr.db') as plr_conn:
                        plr_cursor = plr_conn.cursor()
                        plr_cursor.execute("SELECT SCC FROM plrs WHERE lowID = ?", (lowID,))
                        code_row = plr_cursor.fetchone()

                        author_code = code_row[0] if code_row and code_row[0] else "нет кода"

                        plr_cursor.execute("SELECT COUNT(*) FROM plrs WHERE SCC = ?", (author_code,))
                        count = plr_cursor.fetchone()[0] if author_code != "нет кода" else 0

                        plr_cursor.execute(
                            "UPDATE plrs SET gems = gems + ?, gold = gold + ?, BPTOKEN = BPTOKEN + ? WHERE lowID = ?",
                            (gems, gold, BPTOKEN, lowID)
                        )
                        plr_conn.commit()

                        response_message = (
                            f'⛔ Ваш успех!\n\n'
                            f'1. Каждую неделю вы будете получать:\n'
                            f'{gems} Гемов, {gold} золота, {BPTOKEN} Токенов\n\n'
                            f"🔍 Кодом автора пользуются {count} аккаунта(ов).\n"
                            f"🔍 Ваш код: {author_code}"
                        )
                else:
                    response_message = "❌ Ошибка: Вы не привязали аккаунт."

            bot.reply_to(message, response_message)

        except Exception as e:
            logger.error(f"Failed to reply to creator command: {e}")
            bot.send_message(message.chat.id, "❌ Произошла ошибка при выполнении команды.")

    return creator_command

# Уровни креатерства
bot.message_handler(commands=['creator1'])(create_creator_handler(creator1, 10, 50, 100))
bot.message_handler(commands=['creator2'])(create_creator_handler(creator2, 20, 150, 300))
bot.message_handler(commands=['creator3'])(create_creator_handler(creator3, 50, 300, 750))

threading.Thread(target=distribute_rewards, daemon=True).start()

        
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = message.from_user.id

    try:
        with sqlite3.connect('users.db') as users_conn:
            users_cursor = users_conn.cursor()
            users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            row = users_cursor.fetchone()

            if row:
                lowID = row[0]

                with sqlite3.connect('database/Player/plr.db') as plr_conn:
                    plr_cursor = plr_conn.cursor()
                    plr_cursor.execute("SELECT token, name, trophies, gems, gold, starpoints, tickets, vip, SCC FROM plrs WHERE lowID = ?", (lowID,))
                    plr_row = plr_cursor.fetchone()

                    if plr_row:
                        token, name, trophies, gems, gold, starpoints, tickets, vip, SCC = plr_row
                        vip_status = "Есть" if vip in [1, 2, 3] else "Отсутствует"

                        with open("config.json", "r", encoding='utf-8') as f:
                            config = json.load(f)
                        bp_status = "Куплен" if lowID in config["buybp"] else "Отсутствует"

                        name = escape_markdown(name.strip())
                        author_code_status = SCC if SCC else "Отсутствует"

                        roles = []
                        rewards = ""
                        if user_id in creator1:
                            roles.append("Creator - 1 Уровень")
                            rewards = "10 Гемов, 50 золота, 100 Токенов каждую неделю."
                        elif user_id in creator2:
                            roles.append("Creator - 2 Уровень")
                            rewards = "20 Гемов, 150 золота, 300 Токенов каждую неделю.\n5 Гемов, 75 золота, 150 Токенов за каждое использование кода."
                        elif user_id in creator3:
                            roles.append("Creator - 3 Уровень")
                            rewards = "50 Гемов, 300 золота, 750 Токенов каждую неделю.\n15 Гемов, 150 золота, 300 Токенов за каждое использование кода.\nVIP статус."
                        if user_id in admins:
                            roles.append("Администратор")
                        if user_id in tehs:
                            roles.append("Тех.Админ")
                        if user_id in managers:
                            roles.append("Менеджер")

                        role_str = ", ".join(roles) if roles else "Игрок"

                        profile_info = (f"🤠 Статистика аккаунта: {name}:\n\n🆔 ID: {lowID}\n📱 Токен: {token}\n\n"
                                        f"🏆 Трофеи: {trophies}\n💎 Гемы: {gems}\n💸 Монеты: {gold}\n"
                                        f"🎟️ Билеты: {tickets}\n⭐ Старпоинты: {starpoints}\n\n"
                                        f"💳 VIP: {vip_status}\n🎫 BrawlPass: {bp_status}\n"
                                        f"🔑 Код автора: {author_code_status}\n"
                                        f"🌟 Роль: {role_str}\n")

                        if rewards:
                            profile_info += f"🎁 Награды: {rewards}"

                        bot.send_message(user_id, profile_info)
                    else:
                        bot.send_message(user_id, "❌ Ошибка! Аккаунт не найден.")
            else:
                bot.send_message(user_id, "❌ Вы не привязали аккаунт. Используйте команду /connect.")
    except Exception as e:
        logger.error(f"Error in /profile command: {e}")
        bot.send_message(user_id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['antiddos'])
def handle_antiddos(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in tehs:
        bot.send_message(message.chat.id, "❌ У вас нет прав для выполнения этой команды.")
        return

    bot.send_message(message.chat.id, "Выберите метод:\n"
                                       "1. Очистить аккаунт по имени\n"
                                       "2. Очистить аккаунт по трофеям\n"
                                       "3. Очистить клуб\n"
                                       "4. Очистить список друзей\n"
                                       "5. Очистить бот-клуб\n"
                                       "6. Очистить аккаунт по имени++")

    bot.register_next_step_handler(message, process_antiddos_selection)

def process_antiddos_selection(message: types.Message):
    choice = message.text

    try:
        if choice == '1':
            clear_accounts_by_name(message.from_user.id)
        elif choice == '2':
            clear_accounts_by_trophies(message.from_user.id)
        elif choice == '3':
            clear_club(message.from_user.id)
        elif choice == '4':
            clear_friends_list(message.from_user.id)
        elif choice == '5':
            clear_bot_club(message.from_user.id)
        elif choice == '6':
            clear_accounts_by_name_plus(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, "❌ Неверный выбор. Пожалуйста, попробуйте снова.")
    except Exception as e:
        bot.send_message(message.from_user.id, f"❌ Произошла ошибка: {str(e)}")

def clear_accounts_by_name(user_id):
    try:
        with open('config.json', 'r') as config:
            settings = json.load(config)

        with sqlite3.connect('database/Player/plr.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT lowID FROM plrs WHERE name IN ({})".format(','.join(['?'] * len(settings['DelName']))), settings['DelName'])
            rows = cursor.fetchall()

            for row in rows:
                cursor.execute("DELETE FROM plrs WHERE lowID=?", (row[0],))
            conn.commit()

        bot.send_message(user_id, "✅ Аккаунты по имени очищены.")
    except Exception as e:
        logging.error(f"Failed to clear accounts by name: {e}")

def clear_accounts_by_trophies(user_id):
    try:
        with sqlite3.connect('database/Player/plr.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plrs WHERE trophies = 0")
            conn.commit()

        bot.send_message(user_id, "✅ Аккаунты по трофеям очищены.")
    except Exception as e:
        logging.error(f"Failed to clear accounts by trophies: {e}")

def clear_club(user_id):
    try:
        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET quests = ?", ('[]',))
            conn.commit()

        bot.send_message(user_id, "✅ Клубы очищены.")
    except Exception as e:
        logging.error(f"Failed to clear clubs: {e}")

def clear_friends_list(user_id):
    try:
        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET friends = ? WHERE friends IS NOT NULL", (json.dumps([]),))
            conn.commit()

        bot.send_message(user_id, "✅ Списки друзей очищены.")
    except Exception as e:
        logging.error(f"Failed to clear friends list: {e}")

def clear_bot_club(user_id):
    try:
        with open('config.json', 'r') as config:
            settings = json.load(config)

        with sqlite3.connect('database/Club/clubs.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clubs WHERE LENGTH(clubID) = 28")
            conn.commit()

        bot.send_message(user_id, "✅ Бот-клубы очищены.")
    except Exception as e:
        logging.error(f"Failed to clear bot clubs: {e}")

def clear_accounts_by_name_plus(user_id):
    try:
        with sqlite3.connect('database/Player/plr.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plrs WHERE name LIKE 'player%'")
            conn.commit()

        bot.send_message(user_id, "✅ Аккаунты по имени++ очищены.")
    except Exception as e:
        logging.error(f"Failed to clear accounts by name++: {e}")
        
@bot.message_handler(commands=['delete'])
def handle_delete(message: types.Message):
    user_id = message.from_user.id
    command_parts = message.text.split()
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(user_id, "❌ У вас нет прав для выполнения этой команды.")
        return

    if len(command_parts) != 2:
        bot.send_message(user_id, "Неверный формат команды. Используйте: /delete [id]")
        return

    try:
        lowID_to_delete = command_parts[1]

        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()
            plr_cursor.execute("DELETE FROM plrs WHERE lowID = ?", (lowID_to_delete,))
            plr_conn.commit()

            if plr_cursor.rowcount > 0:
                bot.send_message(user_id, f"✅ Аккаунт с lowID {lowID_to_delete} был успешно удален.")
            else:
                bot.send_message(user_id, "❌ Аккаунт не найден.")
    except Exception as e:
        logging.error(f"Error in /delete command: {e}")
        bot.send_message(user_id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['addadmin'])
def add_admin(message: Message):
    if message.from_user.id in admins:
        try:
            new_admin_id = int(message.text.split()[1])
            if new_admin_id in admins:
                bot.reply_to(message, "❌ Этот пользователь уже является администратором.")
            else:
                admins.add(new_admin_id)
                bot.reply_to(message, f"✅ Пользователь {new_admin_id} был добавлен в администраторы.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Использование: /addadmin [telegramid]")
    else:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этого действия.")

@bot.message_handler(commands=['addteh'])
def add_tech(message: Message):
    if message.from_user.id in admins:
        try:
            new_tech_id = int(message.text.split()[1])
            if new_tech_id in tehs:
                bot.reply_to(message, "❌ Этот пользователь уже является техническим администратором.")
            else:
                teh.add(new_tech_id)
                bot.reply_to(message, f"✅ Пользователь {new_tech_id} был добавлен в технические администраторы.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Использование: /addteh [telegramid]")
    else:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этого действия.")

@bot.message_handler(commands=['addmanager'])
def add_manager(message: Message):
    if message.from_user.id in admins and user_id in tehs:
        try:
            new_manager_id = int(message.text.split()[1])
            if new_manager_id in managers:
                bot.reply_to(message, "❌ Этот пользователь уже является менеджером.")
            else:
                autoshop.append(new_manager_id)
                bot.reply_to(message, f"✅ Пользователь {new_manager_id} был добавлен в менеджеры.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Использование: /addmanager [telegramid]")
    else:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этого действия.")

@bot.message_handler(commands=['unlink'])
def unlink_account(message):
    user_id = message.from_user.id

    try:
        with sqlite3.connect('users.db') as bot_db_connection:
            bot_db_cursor = bot_db_connection.cursor()

            bot_db_cursor.execute("SELECT lowID, name FROM accountconnect WHERE id_user = ?", (user_id,))
            result = bot_db_cursor.fetchone()

            if result:
                lowID, name = result

                bot_db_cursor.execute("DELETE FROM accountconnect WHERE id_user = ?", (user_id,))
                bot_db_connection.commit()

                bot.send_message(message.chat.id, f"✅ Ваш аккаунт успешно отвязан: {name}.\n\n🆔 ID: {lowID}")
            else:
                bot.send_message(message.chat.id, "❌ Вы не привязали аккаунт. Используйте команду /connect.")
    except Exception as e:
        logger.error(f"Error in /unlink command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

def send_top(message, top_type='trophies', page=1):
    try:
        with sqlite3.connect('database/Player/plr.db') as server_db_connection:
            server_db_cursor = server_db_connection.cursor()

            limit = 10
            offset = (page - 1) * limit
            
            if top_type == 'trophies':
                server_db_cursor.execute("SELECT name, trophies FROM plrs ORDER BY trophies DESC LIMIT ? OFFSET ?", (limit, offset))
                top_accounts = server_db_cursor.fetchall()
                header = "🏆 Топ аккаунты по кубкам:\n\n"
            else:
                server_db_cursor.execute("SELECT name, gems, gold, starpoints FROM plrs ORDER BY (gems + gold + starpoints) DESC LIMIT ? OFFSET ?", (limit, offset))
                top_accounts = server_db_cursor.fetchall()
                header = "💎 Топ аккаунты по ресурсам:\n\n"

            if top_accounts:
                top_info = header
                for idx, account in enumerate(top_accounts, start=offset + 1):
                    if top_type == 'trophies':
                        name, trophies = account
                        top_info += f"{idx}. {name}:\n🏆 Кубки: {trophies}\n\n"
                    else:
                        name, gems, gold, starpoints = account
                        top_info += f"{idx}. {name}:\n💎 Гемы: {gems}\n💰 Монеты: {gold}\n⭐ Старпоинты: {starpoints}\n\n"
                
                keyboard = types.InlineKeyboardMarkup()
                if page > 1:
                    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data=f'top_{top_type}_{page-1}'))
                keyboard.add(types.InlineKeyboardButton('➡️ Далее', callback_data=f'top_{top_type}_{page+1}'))
                
                bot.send_message(message.chat.id, top_info, reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, "❌ Топ аккаунтов не найден!")
    except Exception as e:
        logger.error(f"Error in send_top function: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['top'])
def top_command(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Топ по кубкам', callback_data='top_trophies_1'))
    keyboard.add(types.InlineKeyboardButton('Топ по ресурсам', callback_data='top_resources_1'))
    
    bot.send_message(message.chat.id, "Выберите тип топа:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('top_'))
def handle_top_callback(call):
    top_type, page = call.data.split('_')[1:3]
    page = int(page)
    
    if page < 1:
        page = 1
    
    send_top(call.message, top_type, page)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['token'])
def token_command(message):
    user_id = message.from_user.id

    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(message.chat.id, "❌ Используйте команду в формате: /token [lowID]")
            return
        
        lowID = int(args[1])

        with sqlite3.connect('database/Player/plr.db') as server_db_connection:
            server_db_cursor = server_db_connection.cursor()
            
            server_db_cursor.execute("SELECT token, name, trophies, gems, gold, starpoints, tickets, vip FROM plrs WHERE lowID = ?", (lowID,))
            result = server_db_cursor.fetchone()
            
            if result:
                token, name, trophies, gems, gold, starpoints, tickets, vip = result
                vip_status = "Есть" if vip in [1, 2, 3] else "Отсутствует"
                
                token_info = (f"🆔 ID: {lowID}\n\n"
                              f"📱 Токен: `{token}`\n")
                bot.send_message(message.chat.id, token_info, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, "❌ Аккаунт с указанным lowID не найден!")
    
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат lowID. Убедитесь, что вы вводите число.")
    except Exception as e:
        logger.error(f"Error in /token command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['account'])
def update_token(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь техадминистратором!")
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Правильное использование: /account ID NEW_TOKEN")
        return
    
    player_id = parts[1]
    new_token = parts[2]
    
    try:
        with sqlite3.connect('database/Player/plr.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM plrs WHERE lowID=?", (player_id,))
            if cursor.fetchone() is None:
                bot.reply_to(message, f"Игрок с ID {player_id} не найден.")
                return
            
            cursor.execute("UPDATE plrs SET token = ? WHERE lowID = ?", (new_token, player_id))
            conn.commit()
            
            bot.send_message(chat_id=message.chat.id, text=f"Токен для игрока с ID {player_id} успешно обновлён.")
    except Exception as e:
        logger.error(f"Error in /account command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

def escape_markdown(text):
    text = re.sub(r'([_\*`\[\]()~|>#+-=|{}.!])', r'\\\1', text)
    return text

def escape_markdown_v2(text):
    characters_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in characters_to_escape:
        text = text.replace(char, f'\\{char}')
    return text

def format_value(value):
    if value < 0:
        return f"{abs(value)} Отрицательное"
    return str(value)

@bot.message_handler(commands=['connect'])
def connect_command(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат команды. Введите \n/connect [ваш айди] [ваш токен]\n\nВаш айди и токен в игре! Например 1 AxH24bHs4Ijf84RsuN7gnzx")

        player_id = int(parts[1])
        token = parts[2]
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Введите \n/connect [ваш айди] [ваш токен]\n\nВаш айди и токен в игре! Например 1 ABC123")
        return

    try:
        user_id = message.from_user.id
        username = message.from_user.username

        with sqlite3.connect('users.db') as bot_db_connection:
            bot_db_cursor = bot_db_connection.cursor()

            bot_db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS accountconnect
                (lowID INTEGER PRIMARY KEY, trophies INTEGER, name TEXT, id_user INTEGER, token TEXT, username TEXT)
            ''')
            bot_db_connection.commit()

            bot_db_cursor.execute("SELECT lowID, token FROM accountconnect WHERE id_user = ?", (user_id,))
            existing_account = bot_db_cursor.fetchone()

            if existing_account:
                existing_lowID, existing_token = existing_account
                if existing_token != token:
                    bot.send_message(message.chat.id, "❌ Этот аккаунт уже привязан к другому пользователю или токен неверен!")
                    return
                bot.send_message(message.chat.id, "❌ Аккаунт уже привязан!")
                return

            with sqlite3.connect('database/Player/plr.db') as server_db_connection:
                server_db_cursor = server_db_connection.cursor()

                server_db_cursor.execute("SELECT lowID, trophies, name, token FROM plrs WHERE lowID = ?", (player_id,))
                player_data = server_db_cursor.fetchone()

                if player_data:
                    player_lowID, player_trophies, player_name, player_token = player_data

                    # Проверяем, совпадает ли хотя бы половина символов токена
                    similarity_ratio = SequenceMatcher(None, token, player_token).ratio()
                    if similarity_ratio >= 0.5:
                        bot_db_cursor.execute("INSERT INTO accountconnect (lowID, trophies, name, id_user, token, username) VALUES (?, ?, ?, ?, ?, ?)", (player_lowID, player_trophies, player_name, user_id, token, username))
                        bot_db_connection.commit()

                        bot.send_message(message.chat.id, f"🏴 Ваш аккаунт привязан! {player_name}:\n\n🆔 ID: {player_lowID}\n🏆 Кубки: {player_trophies}")
                    else:
                        bot.send_message(message.chat.id, "❌ Токен неверен!")
                else:
                    bot.send_message(message.chat.id, "❌ Аккаунт с указанным айди не найден!")
    except Exception as e:
        logger.error(f"Error in /connect command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_value(value):
    return f"{value}" if value >= 0 else f"-{abs(value)}"

def escape_html(text):
    import html
    return html.escape(text)

@bot.message_handler(commands=['info'])
def info_command(message):
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /info [lowID]")
        return

    try:
        lowID = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат lowID. Убедитесь, что вы вводите число.")
        return

    try:
        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()
            plr_cursor.execute("SELECT token, name, trophies, gems, gold, starpoints, tickets, vip, SCC FROM plrs WHERE lowID = ?", (lowID,))
            plr_row = plr_cursor.fetchone()

            if plr_row:
                token, name, trophies, gems, gold, starpoints, tickets, vip, SCC = plr_row
                vip_status = "Есть" if vip in [1, 2, 3] else "Отсутствует"

                with open("config.json", "r", encoding='utf-8') as f:
                    config = json.load(f)

                # Проверка статуса VIP в config.json
                if lowID not in config["vips"]:
                    vip_status = "Отсутствует"

                bp_status = "Куплен" if lowID in config.get("buybp", []) else "Отсутствует"
                author_code_status = SCC if SCC else "Отсутствует"
                name = escape_html(name.strip())

                trophies = format_value(trophies)
                gems = format_value(gems)
                gold = format_value(gold)
                starpoints = format_value(starpoints)
                tickets = format_value(tickets)

                with sqlite3.connect('users.db') as bot_db_connection:
                    bot_db_cursor = bot_db_connection.cursor()
                    bot_db_cursor.execute("SELECT username FROM accountconnect WHERE lowID = ?", (lowID,))
                    user_row = bot_db_cursor.fetchone()

                registration_info = f"Подтвержден: @{user_row[0]}" if user_row else "Аккаунт: Не подтвержден"

                roles = []
                if lowID in creator1:
                    roles.append("Creator - 1 Уровень")
                if lowID in creator2:
                    roles.append("Creator - 2 Уровень")
                if lowID in creator3:
                    roles.append("Creator - 3 Уровень")
                if lowID in admins:
                    roles.append("Администратор")
                if lowID in tehs:
                    roles.append("Тех.Админ")
                if lowID in managers:
                    roles.append("Менеджер")

                role_str = ", ".join(roles) if roles else "Игрок"

                profile_info = (f"🤠 Статистика аккаунта: {name}:\n\n"
                                f"🆔 ID: {lowID}\n📱 Токен: `ONLYADMIN`\n\n"
                                f"🏆 Трофеи: {trophies}\n💎 Гемы: {gems}\n💸 Монеты: {gold}\n"
                                f"🎟️ Билеты: {tickets}\n⭐ Старпоинты: {starpoints}\n\n"
                                f"💳 VIP: {vip_status}\n🎫 BrawlPass: {bp_status}\n"
                                f"🔑 Код автора: {author_code_status}\n\n"
                                f"{registration_info}\n")

                try:
                    bot.send_message(message.chat.id, profile_info, parse_mode='HTML')
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    bot.send_message(message.chat.id, "❌ Произошла ошибка при отправке сообщения.")
            else:
                bot.send_message(message.chat.id, "❌ Аккаунт с указанным lowID не найден.")
    except Exception as e:
        logger.error(f"Error in /info command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")


@bot.message_handler(commands=['resetbp'])
def reset_brawl_pass(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /resetbp [lowID]")
        return

    try:
        lowID = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат lowID. Убедитесь, что вы вводите число.")
        return

    try:
        freepass_data = json.dumps([])
        buypass_data = json.dumps([])
        
        with sqlite3.connect('database/Player/plr.db') as server_db_connection:
            server_db_cursor = server_db_connection.cursor()

            server_db_cursor.execute("UPDATE plrs SET freepass = ?, buypass = ?, BPTOKEN = ? WHERE lowID = ?", 
                                    (freepass_data, buypass_data, 0, lowID))
            server_db_connection.commit()

            bot.send_message(message.chat.id, f"✅ Brawl Pass для аккаунта с ID {lowID} успешно сброшен.")
    except Exception as e:
        logger.error(f"Error in /resetbp command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['addpass'])
def add_brawl_pass(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /addpass [lowID]")
        return

    try:
        lowID = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат lowID. Убедитесь, что вы вводите число.")
        return

    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if lowID not in config["buybp"]:
            config["buybp"].append(lowID)
            bot.send_message(message.chat.id, f"✅ Brawl Pass добавлен для игрока с ID {lowID}.")
        else:
            bot.send_message(message.chat.id, f"❌ Brawl Pass уже добавлен для игрока с ID {lowID}.")

        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

    except Exception as e:
        logger.error(f"Error in /addpass command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['removepass'])
def remove_brawl_pass(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /removepass [lowID]")
        return

    try:
        lowID = int(args[1])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат lowID. Убедитесь, что вы вводите число.")
        return

    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if lowID in config["buybp"]:
            config["buybp"].remove(lowID)
            bot.send_message(message.chat.id, f"✅ Brawl Pass удален для игрока с ID {lowID}.")
        else:
            bot.send_message(message.chat.id, f"❌ Brawl Pass не найден для игрока с ID {lowID}.")

        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
    except Exception as e:
        logger.error(f"Error in /removepass command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
def escape_markdown(text):
    """ Escape MarkdownV2 special characters """
    return re.sub(r'([_*\[\]()~`>#+-=|{}.!])', r'\\\1', text)

@bot.message_handler(commands=['name'])
def name_command(message):
    args = message.text.split(maxsplit=1)
    
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /name [имя]")
        return

    name = args[1].strip()

    try:
        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()

            plr_cursor.execute("SELECT lowID, name FROM plrs WHERE name = ?", (name,))
            plr_rows = plr_cursor.fetchall()

            if plr_rows:
                account_list = "\n".join([f"{idx + 1}. ID: {row[0]}, Имя: {row[1]}" for idx, row in enumerate(plr_rows)])
                
                keyboard = types.InlineKeyboardMarkup()
                for idx, row in enumerate(plr_rows):
                    button_text = f"ID: {row[0]}, Имя: {row[1]}"
                    keyboard.add(types.InlineKeyboardButton(button_text, callback_data=f'name_{row[0]}'))

                bot.send_message(message.chat.id, f"Найдено несколько аккаунтов с именем `{name}`:\n\n{account_list}", reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, "❌ Аккаунт с указанным именем не найден.")
    except Exception as e:
        logger.error(f"Error in /name command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('name_'))
def handle_name_selection(call):
    lowID = int(call.data.split('_')[1])
    
    try:
        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()

            plr_cursor.execute("SELECT token, name, trophies, gems, gold, starpoints, tickets, vip, SCC FROM plrs WHERE lowID = ?", (lowID,))
            plr_row = plr_cursor.fetchone()

            if plr_row:
                token, name, trophies, gems, gold, starpoints, tickets, vip, SCC = plr_row
                vip_status = "Есть" if vip in [1, 2, 3] else "Отсутствует"

                with open("config.json", "r", encoding='utf-8') as f:
                    config = json.load(f)
                bp_status = "Куплен" if lowID in config["buybp"] else "Отсутствует"

                author_code_status = SCC if SCC else "Отсутствует"
                name = escape_markdown(name.strip())
                
                with sqlite3.connect('users.db') as bot_db_connection:
                    bot_db_cursor = bot_db_connection.cursor()
                    bot_db_cursor.execute("SELECT username FROM accountconnect WHERE lowID = ?", (lowID,))
                    user_row = bot_db_cursor.fetchone()

                if user_row:
                    username = user_row[0]
                    registration_info = f"Подтвержден: @{username}"
                else:
                    registration_info = "Аккаунт: Не подтвержден"
                
                if user_row:
                    username = user_row[0]
                    registration_info = f"Подтвержден: @{username}"
                else:
                    registration_info = "Аккаунт: Не подтвержден"
                
                profile_info = (f"🤠 Статистика аккаунта: {escape_markdown(name)}:\n\n🆔 ID: {lowID}\n📱 Токен: `ONLYADMIN`\n\n"
                                f"🏆 Трофеи: {trophies}\n💎 Гемы: {gems}\n💸 Монеты: {gold}\n"
                                f"🎟️ Билеты: {tickets}\n⭐ Старпоинты: {starpoints}\n\n"
                                f"💳 VIP: {vip_status}\n🎫 BrawlPass: {bp_status}\n"
                                f"🔑 Код автора: {author_code_status}\n\n"
                                f"{registration_info}")
                bot.send_message(call.message.chat.id, profile_info, parse_mode='HTML')
            else:
                bot.send_message(call.message.chat.id, "❌ Ошибка: выбранный аккаунт не найден.")
    except Exception as e:
        logger.error(f"Error in handle_name_selection callback: {e}")
        bot.send_message(call.message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['recovery'])
def recovery_command(message):
    user_id = message.from_user.id

    try:
        with sqlite3.connect('users.db') as bot_db_connection:
            bot_db_cursor = bot_db_connection.cursor()
            
            bot_db_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            profile_info = bot_db_cursor.fetchone()

            if not profile_info:
                bot.send_message(message.chat.id, "❌ Ваш профиль не активен. Сначала используйте команду /profile для активации профиля.")
                return
            
            user_lowID = profile_info[0]

        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❌ Используйте команду в формате: /recovery [lowID] [новый токен]")
            return
        
        lowID = int(parts[1])
        new_token = parts[2]

        if lowID != user_lowID:
            bot.send_message(message.chat.id, "❌ Вы не можете изменять токен для данного lowID, так как это не ваш профиль.")
            return

        with sqlite3.connect('database/Player/plr.db') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM plrs WHERE lowID = ?", (lowID,))
            player = cursor.fetchone()

            if player is None:
                bot.send_message(message.chat.id, f"❌ Игрок с ID {lowID} не найден.")
                return

            old_token = player[1]  # Предполагается, что токен находится во втором столбце

            # Удаляем аккаунт с новым токеном
            cursor.execute("DELETE FROM plrs WHERE token = ?", (new_token,))
            
            # Обновляем токен для текущего игрока
            cursor.execute("UPDATE plrs SET token = ? WHERE lowID = ?", (new_token, lowID))
            conn.commit()

            bot.send_message(chat_id=message.chat.id, text=f"✅ Токен для игрока с ID {lowID} успешно обновлён. Аккаунт с новым токеном был удалён.")

    except Exception as e:
        logger.error(f"Error in /recovery command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

def dball():
    conn = sqlite3.connect("database/Player/plr.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM plrs")
    return cur.fetchall()

config_file_path = 'config.json'

def load_config():
    try:
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_config(config):
    try:
        with open(config_file_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False

def update_maintenance_status(new_status):
    config = load_config()
    if config:
        config['maintenance'] = new_status
        return save_config(config)
    return False

def is_admin(user_id):
    return user_id in admins or user_id in tehs


# Структура для скинов
skins = {
    'common': [29, 15, 2, 109, 27, 139, 111, 137, 152, 75],
    'rare': [25, 58, 98, 28, 92, 158, 130, 88, 93, 104, 132, 108, 45, 125, 117, 11, 126, 131, 20, 110],
    'epic': [52, 159, 79, 44, 163, 91, 160, 99, 30, 128, 71, 59, 26, 68, 147, 50, 96, 118],
    'legendary': [94, 49, 95]
}

# Привязка цен к редкостям
skin_prices = {
    "common": (29, 29),
    "rare": (79, 79),
    "epic": (149, 149),
    "legendary": (299, 299)
}

def get_offers():
    with open("JSON/offers.json", "r",encoding='utf-8') as f:
        data = json.load(f)

    offer_list = "Список акций:\n"
    for offer_id, offer_data in data.items():
        vault=offer_data['ShopType']
        daily=offer_data['ShopDisplay']
        current=""
        types=""
        if vault==1:current="Золото"
        elif vault==0:current="Кристаллы"
        if daily==1:types="Ежедневная"
        elif daily==0:types="Обычная"
        offer_list += f"\nАкция #{offer_id}\n"
        offer_list += f"Название: {offer_data['OfferTitle']}\n"
        offer_list += f"Тип: {types}\n"
        offer_list += f"Боец: {offer_data['BrawlerID'][0]}\n"
        offer_list += f"Скин: {offer_data['SkinID'][0]}\n"
        offer_list += f"Валюта: {current}\n"
        offer_list += f"Стоимость: {offer_data['Cost']}\n"
        offer_list += f"Множитель: {offer_data['Multiplier'][0]}\n"

    return offer_list
@bot.message_handler(commands=['list'])
def handle_list_offers(message):
    offer_list = get_offers()

    bot.send_message(chat_id=message.chat.id, text=offer_list)
    
    
@bot.message_handler(commands=['new_offer'])
def add_offer(message):
    user_id = message.from_user.id
    if user_id in admins:
        offer_data = message.text.split()
        
        if len(offer_data) != 12:  # Expecting exactly 10 parts
            bot.reply_to(message, "Список ID предложений в магазине:\n"
        "0 = Бесплатный ящик Brawl Box\n"
        "1 = Золото\n"
        "2 = Случайный боец\n"
        "3 = Боец\n"
        "4 = Скин\n"
        "5 = Звёздная сила / Гаджет\n"
        "6 = Ящик Brawl Box\n"
        "7 = Билеты (больше не работают)\n"
        "8 = Очки силы (для конкретного бойца)\n"
        "9 = Удвоитель жетонов\n"
        "10 = Мегаящик\n"
        "11 = Ключи (???)\n"
        "12 = Очки силы\n"
        "13 = Слот события (???)\n"
        "14 = Большой ящик\n"
        "15 = Рекламный ящик (больше не работают)\n"
        "16 = Гемы\n"
        "19 = Пин для бойца\n"
        "20 = Коллекция пинов\n"
        "21 = Набор пинов\n"
        "22 = Набор пинов для бойца\n"
        "23 = Обычный пин (???)\n"
        "24 = Предложение скина в магазине (может не работать)\n"
        "94 = Скин (???)\n\n"
        
        "Список BGR предложений в магазине:\n"
        "Предложение жетонов = offer_generic\n"
        "Специальное предложение = offer_special\n"
        "Предложение за звёздные очки = offer_legendary\n"
        "Предложение монет = offer_coins (в версии 29 как offer_moon_festival)\n"
        "Предложение гемов = offer_gems\n"
        "Предложение ящиков = offer_boxes\n"
        "Предложение бойца = offer_finals\n"
        "Предложение Лунного Нового года = offer_lny\n"
        "Архивное предложение = offer_archive\n"
        "Хроматическое предложение = offer_chromatic\n"
        "Предложение Лунного фестиваля = offer_moon_festival\n"
        "Рождественское предложение = offer_xmas\n\n"
        
        "ET означает дополнительный текст.")
            bot.reply_to(message, 'Используйте команду /new_offer с аргументами в формате: /new_offer <ID> <Multiplier> <BrawlerID> <SkinID> <ShopType> <Cost> <OfferView> <ShopDisplay> <Oldcost> <OfferTitle> <OfferRGB>')
            bot.reply_to(message, 'ID - Айди акций, можно посмотреть в Logic/Shop.py или сообщением выше.\nMultiplier - Кол-во (с ящиками не работает).\nBrawlerID - Айди бойца.\nSkinID - айди скина.\nShopType - за какую валюту покупают предмет, пример: 0 - гемы, 1 - золото, 3 - старпоинты.\nCost - стоимость.\nOfferView - просмотренна ли акция или нет, пример: 0 - абсолютно новая, 1 - новая, 2 - просмотренна.\nShopDisplay - вид акции, пример: 0 - обыкновенная, 1 - дневная (квадратик).\nOldcost - старая цена.\nOfferTitle - название акции.\nOfferRGB - внешний вид (сообщение выше).')
            return
        
        print("Received offer data:", offer_data)  # Debugging output
        
        try:
            new_offer = {
                'ID': [int(offer_data[1]), 0, 0],
                'Multiplier': [int(offer_data[2]), 0, 0],
                'BrawlerID': [int(offer_data[3]), 0, 0],
                'SkinID': [int(offer_data[4]), 0, 0],
                'ShopType': int(offer_data[5]),  # Expecting integer
                'Cost': int(offer_data[6]),
                'Timer': 86400,
                "OfferView": int(offer_data[7]),
                'WhoBuyed': [],
                'ShopDisplay': int(offer_data[8]),
                'OldCost': int(offer_data[9]),
                'OfferTitle': offer_data[10],
                'OfferBGR': offer_data[11],
                "ETType": 0,
                "ETMultiplier": 0
            }
        except ValueError as e:
            bot.reply_to(message, f'Ошибка при вводе данных: {e}')
            return

        # Attempt to read and write the offers file
        try:
            with open('JSON/offers.json', 'r', encoding='utf-8') as f:
                offers = json.load(f)
            offers[str(len(offers))] = new_offer
            
            with open('JSON/offers.json', 'w', encoding='utf-8') as f:
                json.dump(offers, f, indent=4)

            bot.reply_to(message, '✅ Новая акция успешно добавлена!')
        
        except PermissionError:
            bot.reply_to(message, "❌ У меня нет прав для записи в файл offers.json. Пожалуйста, проверьте права доступа.")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['rename'])
def change_name(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "❌ Правильное использование /rename [id] [new name]")
        else:
            user_id = message.from_user.id
            id = message.text.split()[1]
            ammount = message.text.split()[2]
            conn = sqlite3.connect("database/Player/plr.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET name = ? WHERE lowID = ?", (ammount, id))
            conn.commit()
            conn.close()
            bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку c айди {id} изменили имя на {ammount}.")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['remove_offer'])
def remove_offer(message):
    user_id = message.from_user.id
    if user_id in admins:
        if len(message.text.split()) != 2:
            bot.reply_to(message, 'Используйте команду /remove_offer с аргументом в формате: /remove_offer <ID>')
            return
        offer_id = message.text.split()[1]
        
        # Проверка, что ID меньше 13 или равно 13
        if int(offer_id) <= 13:
            bot.reply_to(message, f"❌ Акция с ID {offer_id} не может быть удалена!")
            return
        
        with open('JSON/offers.json', 'r', encoding='utf-8') as f:
            offers = json.load(f)
        
        if offer_id not in offers:
            bot.reply_to(message, f'❌ Акция с ID {offer_id} не найдена')
            return
        
        offers.pop(offer_id)
        
        with open('JSON/offers.json', 'w', encoding='utf-8') as f:
            json.dump(offers, f)
        
        bot.reply_to(message, f'✅ Акция с ID {offer_id} удалена')
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        
@bot.message_handler(commands=['theme'])
def theme(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Выбери ID темы\n0 - Обычная\n1 - Новый год (Снег)\n2 - Красный новый год\n3 - От клеш рояля\n4 - Обычный фон с дефолт музыкой\n5 - Желтые панды\n7 - Роботы Зелёный фон\n8 - Хэллуин 2019\n9 - Пиратский фон (Новый год 2020)\n10 - Фон с обновы с мистером п.\n11 - Футбольный фон\n12 - Годовщина Supercell\n13 - Базар Тары\n14 - Лето с монстрами\n15 - Гавс\n16 - Зайчики\nИспользовать команду /theme ID")
        else:
            user_id = message.from_user.id
            theme_id = message.text.split()[1]
            conn = sqlite3.connect("database/Player/plr.db")
            c = conn.cursor()
            c.execute(f"UPDATE plrs SET theme={theme_id}")
            conn.commit()
            c.execute("SELECT * FROM plrs")
            conn.close()
            bot.send_message(chat_id=message.chat.id, text=f"✅ Айди всех записей был изменён на {theme_id}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        
@bot.message_handler(commands=['code'])
def new_code(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Правильное использование /code [new code](На англ)")
        else:
            code = message.text.split()[1]
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            if code not in config["CCC"]:
                config["CCC"].append(code)
                with open("config.json", "w", encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                bot.send_message(chat_id=message.chat.id, text=f"✅ Новый код {code}, Был добавлен!")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"❌ Код {code} уже существует!")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['code_list'])
def code_list(message):
    with open('config.json', 'r') as f:
        data = json.load(f)
    code_list = '\n'.join(data["CCC"])
    bot.send_message(chat_id=message.chat.id, text=f"Список кодов: \n{code_list}")
    	
    	
@bot.message_handler(commands=['uncode'])
def del_code(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "❌ Правильное использование /uncode [code]")
        else:
            code = message.text.split()[1]
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            if code in config["CCC"]:
                config["CCC"].remove(code)
                with open("config.json", "w", encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                bot.send_message(chat_id=message.chat.id, text=f"✅ Код {code}, Был удалён!")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"❌ Код {code} не найден!")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['code_info'])
def code_info(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in creator1 and user_id not in creator2 and user_id not in creator3:
        bot.reply_to(message, "❌ Вы не имеете доступ к данной команде!")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /code_info [code]")
        return

    code = args[1]
    
    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if code not in config["CCC"]:
            bot.send_message(message.chat.id, f"❌ Код {code} не найден.")
            return
        
        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()
            plr_cursor.execute("SELECT COUNT(*) FROM plrs WHERE SCC = ?", (code,))
            count = plr_cursor.fetchone()[0]

        if count > 0:
            bot.send_message(chat_id=message.chat.id, text=f"🔍 Код {code} используется {count} аккаунтами.")
        else:
            bot.send_message(chat_id=message.chat.id, text=f"❌ Код {code} не используется ни одним аккаунтом.")
    
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Файл конфигурации не найден.")
    except json.JSONDecodeError:
        bot.send_message(message.chat.id, "❌ Ошибка чтения конфигурации. Проверьте файл config.json.")
    except Exception as e:
        logger.error(f"Error in /code_info command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")

@bot.message_handler(commands=['vip'])
def add_vip(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in managers:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Правильное использование /vip [id]")
        else:
            vip_id = int(message.text.split()[1])
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            if vip_id not in config["vips"]:
                config["vips"].append(vip_id)
                with open("config.json", "w", encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                bot.send_message(chat_id=message.chat.id, text=f"✅ Вип статус был выдан игроку с ID {vip_id}")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"❌ Вип статус уже есть у ID {vip_id}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

		
@bot.message_handler(commands=['unvip'])
def del_vip(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in managers:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Правильное использование /unvip [id]")
        else:
            code = int(message.text.split()[1])
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            if code in config["vips"]:
                config["vips"].remove(code)
                with open("config.json", "w", encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                bot.send_message(chat_id=message.chat.id, text=f"✅ Вип статус был удален у игрока с ID {code}")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"❌ Вип статус не найден у игрока с ID {code}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

        
        
STAR_SKINS = {
    103: 500,
    102: 2500,
    100: 10000,
    101: 50000,
    120: 500,
    165: 10000,
    167: 500,
    123: 10000,
    118: 500,
    108: 500
}

def save_last_update():
    now = dt.now(pytz.timezone("Europe/Moscow"))
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("JSON/last_update.json", "w", encoding="utf-8") as f:
        json.dump({"last_update": update_time}, f, indent=4, ensure_ascii=False)
    
    for admin in admins:
        try:
            bot.send_message(admin, f"✅ Магазин обновлён в {update_time} по МСК")
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору {admin}: {e}")

def auto_shop():
    try:
        shop_items = [
            {"StarPowerCard": [76, 135], "GadgetCard": [255, 288], "Brawler": 0},
            {"StarPowerCard": [77, 138], "GadgetCard": [273], "Brawler": 1},
            {"StarPowerCard": [78, 137], "GadgetCard": [272], "Brawler": 2},
            {"StarPowerCard": [79, 150], "GadgetCard": [245], "Brawler": 3},
            {"StarPowerCard": [80, 156], "GadgetCard": [246], "Brawler": 4},
            {"StarPowerCard": [81, 151], "GadgetCard": [247], "Brawler": 5},
            {"StarPowerCard": [82, 158], "GadgetCard": [250], "Brawler": 6},
            {"StarPowerCard": [83, 149], "GadgetCard": [251], "Brawler": 7},
            {"StarPowerCard": [84, 136], "GadgetCard": [249], "Brawler": 8},
            {"StarPowerCard": [85, 155], "GadgetCard": [258], "Brawler": 9},
            {"StarPowerCard": [86, 140], "GadgetCard": [264], "Brawler": 10},
            {"StarPowerCard": [87, 154], "GadgetCard": [265], "Brawler": 11},
            {"StarPowerCard": [88, 143], "GadgetCard": [243], "Brawler": 12},
            {"StarPowerCard": [89, 144], "GadgetCard": [267], "Brawler": 13},
            {"StarPowerCard": [90, 148], "GadgetCard": [263], "Brawler": 14},
            {"StarPowerCard": [91, 152], "GadgetCard": [268], "Brawler": 15},
            {"StarPowerCard": [92, 139], "GadgetCard": [257], "Brawler": 16},
            {"StarPowerCard": [93, 160], "GadgetCard": [266], "Brawler": 17},
            {"StarPowerCard": [94, 157], "GadgetCard": [260], "Brawler": 18},
            {"StarPowerCard": [99, 142], "GadgetCard": [248], "Brawler": 19},
            {"StarPowerCard": [104, 153], "GadgetCard": [261], "Brawler": 20},
            {"StarPowerCard": [109, 159], "GadgetCard": [252], "Brawler": 21},
            {"StarPowerCard": [114, 161], "GadgetCard": [253], "Brawler": 22},
            {"StarPowerCard": [119, 141], "GadgetCard": [276], "Brawler": 23},
            {"StarPowerCard": [124, 147], "GadgetCard": [242], "Brawler": 24},
            {"StarPowerCard": [129, 145], "GadgetCard": [262], "Brawler": 25},
            {"StarPowerCard": [134, 146], "GadgetCard": [275], "Brawler": 26},
            {"StarPowerCard": [168, 181], "GadgetCard": [259], "Brawler": 27},
            {"StarPowerCard": [186, 187], "GadgetCard": [270], "Brawler": 28},
            {"StarPowerCard": [192, 193], "GadgetCard": [271], "Brawler": 29},
            {"StarPowerCard": [198, 199], "GadgetCard": [274], "Brawler": 30},
            {"StarPowerCard": [204, 205], "GadgetCard": [269], "Brawler": 31},
            {"StarPowerCard": [210, 211], "GadgetCard": [254], "Brawler": 32},
            {"StarPowerCard": [222, 223], "GadgetCard": [256], "Brawler": 34},
            {"StarPowerCard": [228, 229], "GadgetCard": [277], "Brawler": 35},
            {"StarPowerCard": [234, 235], "GadgetCard": [278], "Brawler": 36},
            {"StarPowerCard": [240, 241], "GadgetCard": [244], "Brawler": 37},
            {"StarPowerCard": [283, 284], "GadgetCard": [285], "Brawler": 38},
            {"StarPowerCard": [300, 301], "GadgetCard": [302], "Brawler": 39},
            {"StarPowerCard": [307, 308], "GadgetCard": [309], "Brawler": 40},
            {"StarPowerCard": [324, 325], "GadgetCard": [326], "Brawler": 41},
            {"StarPowerCard": [331, 332], "GadgetCard": [333], "Brawler": 42},
            {"StarPowerCard": [338, 339], "GadgetCard": [340], "Brawler": 43},
            {"StarPowerCard": [345, 346], "GadgetCard": [347], "Brawler": 44},
            {"StarPowerCard": [362, 363], "GadgetCard": [364], "Brawler": 45}
        ]
        with open('JSON/offers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        used_skins = set()
        valid_brawler_ids = [i for i in range(0, 40) if i != 33]

        with open('config.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        available_skins = set(settings['Skinse'])
        
        # --- Первая акция: подарок ---
        choice = random.choice([1, 2, 3])

        if choice == 1:  
            gift_id = 1  # Золото  
            gold_amount = random.choice([25, 50, 75, 150, 300])  
            cost = random.randint(1, 15)  
            oldcost = cost + random.randint(1, 15)
        elif choice == 2:  
            gift_id = 16  # Гемы  
            gold_amount = random.randint(1, 10)  
            cost = random.randint(1, 15)  
            oldcost = cost + random.randint(1, 15)
        elif choice == 3:  
            gift_id = 6  # Например, новый предмет  
            gold_amount = 1  # Другое количество  
            cost = random.randint(1, 15)  # Другая стоимость
            oldcost = cost + random.randint(1, 15)

        data["0"] = {
            "ID": [gift_id, 0, 0],
            "Multiplier": [gold_amount, 0, 0],
            "BrawlerID": [0, 0, 0],
            "SkinID": [0, 0, 0],
            "ShopType": 1,
            "Cost": cost,
            "Timer": 86400,
            "OfferView": 0,
            "WhoBuyed": [],
            "ShopDisplay": 1,
            "OldCost": oldcost,
            "OfferTitle": "ПОДАРОК!",
            "OfferBGR": "0",
            "ETType": 0,
            "ETMultiplier": 0
        }
        
        selected_item = random.choice(shop_items)
        all_powerups = selected_item["GadgetCard"] + selected_item["StarPowerCard"]
        powerup_id = random.choice(all_powerups)
        powerup_cost = 1000 if powerup_id in selected_item["GadgetCard"] else 2000

        data["1"] = {
            "ID": [5, 0, 0],
            "Multiplier": [0, 0, 0],
            "BrawlerID": [selected_item["Brawler"], 0, 0],
            "SkinID": [powerup_id, 0, 0],
            "ShopType": 1,
            "Cost": powerup_cost,
            "Timer": 86400,
            "OfferView": 0,
            "WhoBuyed": [],
            "ShopDisplay": 1,
            "OldCost": 0,
            "OfferTitle": "УЛУЧШЕНИЕ",
            "OfferBGR": "0",
            "ETType": 0,
            "ETMultiplier": 0
        }
        
        for i in range(2, 6):
            if not valid_brawler_ids:
                bot.reply_to(message, "❌ Недостаточно бойцов для создания акций!")
                return

            multiplier = random.randint(10, 456)
            brawler_id = random.choice(valid_brawler_ids)
            valid_brawler_ids.remove(brawler_id)  # Удаляем выбранного бойца, чтобы не повторялся

            new_offer = {
                "ID": [8, 0, 0],
                "Multiplier": [multiplier, 0, 0],
                "BrawlerID": [brawler_id, 0, 0],
                "SkinID": [0, 0, 0],
                "ShopType": 1,
                "Cost": multiplier * 2,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 1,
                "OldCost": 0,
                "OfferTitle": "ЕЖЕДНЕВНАЯ АКЦИЯ",
                "OfferBGR": "0",
                "ETType": 0,
                "ETMultiplier": 0
            }

            data[str(i)] = new_offer

        for i in range(6, 12):
            if not available_skins:
                bot.reply_to(message, "❌ Недостаточно скинов для создания акций!")
                return

            random_skin = random.choice(list(available_skins))
            available_skins.remove(random_skin)
            used_skins.add(random_skin)

            # Определение редкости
            all_skins_by_rarity = get_skin_ids_by_rarity(None)
            rarity = next((r for r, skins in all_skins_by_rarity.items() if random_skin in skins), 'common')
            cost = random.randint(*get_price_range_by_rarity(rarity))

            # Сохраняем старую стоимость
            old_cost = cost  

            # Определяем скидку с шансом 30%
            discount = 0
            if random.random() < 0.3:  # 30% шанс на скидку
                if rarity == 'common':
                    discount = 10
                elif rarity == 'rare':
                    discount = 30
                elif rarity == 'epic':
                    discount = 50
                elif rarity == 'legendary':
                    discount = 100

            # Применяем скидку, если она выпала
            cost = max(0, cost - discount)  # Цена не может быть меньше 0

            # Устанавливаем ShopType в 1, если это золотой скин
            shop_type = 1 if rarity in ['gold', 'silver'] else 0

            new_offer = {
                "ID": [4, 0, 0],
                "Multiplier": [0, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [random_skin, 0, 0],
                "ShopType": shop_type,
                "Cost": cost,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": old_cost,  # Сохраняем старую стоимость
                "OfferTitle": "ЕЖЕДНЕВНЫЙ СКИН",
                "OfferBGR": "0",
                "ETType": 0,
                "ETMultiplier": 0
            }

            data[str(i)] = new_offer

        # Генерация 2 звездных скинов
        selected_star_skins = random.sample(list(STAR_SKINS.keys()), 2)

        for idx, skin_id in enumerate(selected_star_skins, start=12):
            new_star_offer = {
                "ID": [4, 0, 0],
                "Multiplier": [0, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [skin_id, 0, 0],
                "ShopType": 3,
                "Cost": STAR_SKINS[skin_id],
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": 0,
                "OfferTitle": "ЗВЁЗДНЫЙ СКИН",
                "OfferBGR": "0",
                "ETType": 0,
                "ETMultiplier": 0
            }

            data[str(idx)] = new_star_offer
            
        if random.random() < 0.1:
            next_index = str(len(data))
            data[next_index] = {
                "ID": [10, 0, 0],
                "Multiplier": [1, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [0, 0, 0],
                "ShopType": 3,
                "Cost": 1500,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": 0,
                "OfferTitle": "ОСОБАЯ АКЦИЯ",
                "OfferBGR": "offer_legendary",
                "ETType": 0,
                "ETMultiplier": 0
            }
            
            next_index = str(len(data))
            data[next_index] = {
                "ID": [14, 0, 0],
                "Multiplier": [1, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [0, 0, 0],
                "ShopType": 3,
                "Cost": 500,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": 0,
                "OfferTitle": "ОСОБАЯ АКЦИЯ",
                "OfferBGR": "offer_legendary",
                "ETType": 0,
                "ETMultiplier": 0
            }

        with open('JSON/offers.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        save_last_update()
    except Exception as e:
        print(f"Ошибка при обновлении магазина: {e}")

        
def schedule_auto_shop():
    now = dt.now(pytz.timezone("Europe/Moscow"))
    next_run = now.replace(hour=11, minute=0, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    initial_delay = (next_run - now).total_seconds()
    
    def run_periodically():
        delay = initial_delay  # Устанавливаем начальную задержку
        while True:
            time.sleep(delay)
            auto_shop()
            delay = 24 * 60 * 60  # После первой итерации устанавливаем задержку в 24 часа

    thread = threading.Thread(target=run_periodically, daemon=True)
    thread.start()

schedule_auto_shop()

@bot.message_handler(commands=['upshop'])
def manual_update(message):
    if message.from_user.id in admins:
        auto_shop()
        bot.reply_to(message, '✅ Акции успешно обновлены!')
    else:
        bot.reply_to(message, "❌ У вас недостаточно прав!")
        
        
def get_skin_ids_by_rarity(rarity=None):
    skin_ids = {
        'common': [29, 15, 2, 109, 27, 139, 111, 137, 152],
        'rare': [25, 28, 92, 158, 88, 93, 104, 132, 125, 117, 11, 126, 131, 20, 110, 135, 159, 75],
        'epic': [79, 44, 163, 91, 160, 99, 30, 128, 71, 26, 68, 147, 96, 118, 98, 254],
        'legendary': [94, 49, 95, 143],
        'gold': [185, 195, 197, 199, 221, 219, 229],
        'silver': [224, 226, 186, 187, 196, 198, 200]
    }
    return skin_ids if rarity is None else skin_ids.get(rarity, [])  

def get_price_range_by_rarity(rarity):
    price_ranges = {
        'common': (29, 29),
        'rare': (79, 79),
        'epic': (149, 149),
        'legendary': (299, 299),
        'gold': (10000, 10000),
        'silver': (2500, 2500)
    }
    return price_ranges.get(rarity, (10, 20))
		
def is_numeric(value):
    return value.isdigit()

def validate_integer(value):
    try:
        int_value = int(value)
        if int_value <= 0:
            return False
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['setgems'])
def set_gems(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in managers:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /setgems [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество гемов должно быть положительным числом!")
            return

        conn = sqlite3.connect("database/Player/plr.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE plrs SET gems = ? WHERE lowID = ?", (amount, id))
        conn.commit()
        conn.close()
        bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} установили {amount} гемов")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['addgems'])
def add_gems(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in managers:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /addgems [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество гемов должно быть положительным числом!")
            return

        conn = sqlite3.connect("database/Player/plr.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE plrs SET gems = gems + ? WHERE lowID = ?", (amount, id))
        conn.commit()
        conn.close()
        bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} добавлено {amount} гемов")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['ungems'])
def ungems(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in managers:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /ungems [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество гемов должно быть положительным числом!")
            return

        conn = sqlite3.connect("database/Player/plr.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE plrs SET gems = gems - ? WHERE lowID = ?", (amount, id))
        conn.commit()
        conn.close()
        bot.send_message(chat_id=message.chat.id, text=f"✅ У игрока с айди {id} убрано {amount} гемов")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        
def is_numeric(value):
    return value.isdigit()

def validate_integer(value, non_negative=False):
    try:
        int_value = int(value)
        if non_negative:
            return int_value >= 0
        return int_value > 0
    except ValueError:
        return False

@bot.message_handler(commands=['setgold'])
def set_gold(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /setgold [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount, non_negative=True):
            bot.reply_to(message, "❌ Количество золота должно быть числом >= 0!")
            return

        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET gold = ? WHERE lowID = ?", (amount, id))
            conn.commit()
        
        bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} установлено {amount} золота")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['addgold'])
def add_gold(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /addgold [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество золота должно быть числом > 0!")
            return

        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET gold = gold + ? WHERE lowID = ?", (amount, id))
            conn.commit()
        
        bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} добавлено {amount} золота")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['ungold'])
def un_gold(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /ungold [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество золота должно быть числом > 0!")
            return

        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET gold = gold - ? WHERE lowID = ?", (amount, id))
            conn.commit()
        
        bot.send_message(chat_id=message.chat.id, text=f"✅ У игрока с айди {id} убрано {amount} золота")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
		
@bot.message_handler(commands=['settokens'])
def set_tokens(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in tehs: 
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /settokens [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount, non_negative=True):
            bot.reply_to(message, "❌ Количество токенов должно быть числом >= 0!")
            return

        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET BPTOKEN = ? WHERE lowID = ?", (amount, id))
            conn.commit()
        
        bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} установлены {amount} токенов")
    else:
        bot.reply_to(message, "❌ У вас нет прав на эту команду!")

@bot.message_handler(commands=['addtokens'])
def add_tokens(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in tehs: 
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /addtokens [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество токенов должно быть числом > 0!")
            return

        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET BPTOKEN = BPTOKEN + ? WHERE lowID = ?", (amount, id))
            conn.commit()
        
        bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} добавлено {amount} токенов")
    else:
        bot.reply_to(message, "❌ У вас нет прав на эту команду!")

@bot.message_handler(commands=['untokens'])
def un_tokens(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in tehs: 
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /untokens [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество токенов должно быть числом > 0!")
            return

        with sqlite3.connect("database/Player/plr.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET BPTOKEN = BPTOKEN - ? WHERE lowID = ?", (amount, id))
            conn.commit()
        
        bot.send_message(chat_id=message.chat.id, text=f"✅ У игрока с айди {id} убрано {amount} токенов")
    else:
        bot.reply_to(message, "❌ У вас нет прав на эту команду!")
        
@bot.message_handler(commands=['ban'])
def ban(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Правильное использование /ban [id]")
        else:
            vip_id = int(message.text.split()[1])
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            if vip_id not in config["banID"]:
                config["banID"].append(vip_id)
                with open("config.json", "w", encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                bot.send_message(chat_id=message.chat.id, text=f"✅ Бан был выдан игроку {vip_id}")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"❌ Бан уже есть у игрока {vip_id}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['unban'])
def ban(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Правильное использование /unban [id]")
        else:
            vip_id = int(message.text.split()[1])
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            if vip_id in config["banID"]:
                config["banID"].remove(vip_id)
                with open("config.json", "w", encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                bot.send_message(chat_id=message.chat.id, text=f"✅ Разбан был выдан игроку {vip_id}")
            else:
                bot.send_message(chat_id=message.chat.id, text=f"❌ У игрока {vip_id} отсутствует бан")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['unroom'])
def clear_room(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        if len(message.text.split()) < 2:
            user_id = message.from_user.id
            plrsinfo = "database/Player/plr.db"
            if os.path.exists(plrsinfo):
                conn = sqlite3.connect("database/Player/plr.db")
                c = conn.cursor()
                c.execute("UPDATE plrs SET roomID=0")
                c.execute("SELECT * FROM plrs")
                conn.commit()
                conn.close()
                bot.reply_to(message, '✅ Команды были очищены!')
            else:
                bot.reply_to(message, "❌ Вы не являетесь администратором!")

def is_numeric(value):
    return value.isdigit()

def validate_integer(value, non_negative=False):
    try:
        int_value = int(value)
        if non_negative:
            return int_value >= 0
        return int_value > 0
    except ValueError:
        return False

def is_numeric(value):
    return value.isdigit()

def validate_integer(value, non_negative=False):
    try:
        value = int(value)
        if non_negative and value < 0:
            return False
        return True
    except ValueError:
        return False

@bot.message_handler(commands=['settrophies'])
def set_trophies(message):
    user_id = message.from_user.id
    if user_id in admins:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /settrophies [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount, non_negative=True):
            bot.reply_to(message, "❌ Количество трофеев должно быть числом >= 0!")
            return

        amount = int(amount)

        try:
            with sqlite3.connect("database/Player/plr.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE plrs SET trophies = ? WHERE lowID = ?", (amount, id))
                conn.commit()
            bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} установлено {amount} трофеев")
        except Exception as e:
            logger.error(f"Error in /settrophies command: {e}")
            bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['addtrophies'])
def add_trophies(message):
    user_id = message.from_user.id
    if user_id in admins:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /addtrophies [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество трофеев должно быть числом > 0!")
            return

        amount = int(amount)

        try:
            with sqlite3.connect("database/Player/plr.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE plrs SET trophies = trophies + ? WHERE lowID = ?", (amount, id))
                conn.commit()
            bot.send_message(chat_id=message.chat.id, text=f"✅ Игроку с айди {id} добавлено {amount} трофеев")
        except Exception as e:
            logger.error(f"Error in /addtrophies command: {e}")
            bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

@bot.message_handler(commands=['untrophies'])
def remove_trophies(message):
    user_id = message.from_user.id
    if user_id in admins:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Правильное использование /untrophies [id] [amount]")
            return
        
        id, amount = parts[1], parts[2]

        if not is_numeric(id):
            bot.reply_to(message, "❌ ID должно быть числом!")
            return

        if not validate_integer(amount):
            bot.reply_to(message, "❌ Количество трофеев должно быть числом > 0!")
            return

        amount = int(amount)

        try:
            with sqlite3.connect("database/Player/plr.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE plrs SET trophies = trophies - ? WHERE lowID = ?", (amount, id))
                conn.commit()
            bot.send_message(chat_id=message.chat.id, text=f"✅ У игрока с айди {id} убрано {amount} трофеев")
        except Exception as e:
            logger.error(f"Error in /untrophies command: {e}")
            bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")


@bot.message_handler(commands=['teh'])
def enable_maintenance(message):
    if is_admin(message.from_user.id):
        if update_maintenance_status(True):
            bot.reply_to(message, "✅ Технический перерыв был включен!")
        else:
            bot.reply_to(message, "❌ Произошла ошибка при включении технического перерыва.")
    else:
        bot.reply_to(message, "❌Вы не являетесь администратором!")

@bot.message_handler(commands=['unteh'])
def disable_maintenance(message):
    if is_admin(message.from_user.id):
        if update_maintenance_status(False):
            bot.reply_to(message, "✅ Технический перерыв был выключен!")
        else:
            bot.reply_to(message, "❌ Произошла ошибка при выключении технического перерыва.")
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")

def get_disk_usage():
    try:
        usage = psutil.disk_usage('/')
        return usage.percent // 100
    except Exception as e:
        return f"Error: {e}"

def get_ping(host='asuranodes.fun'):
    try:
        response_time = ping(host)
        if response_time is not None:
            inflated_ping = response_time * 1000
            return f"{inflated_ping:.2f}"
        else:
            return "Не удалось измерить"
    except Exception as e:
        return f"Error: {e}"

@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs:
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
                ban_list = len(data.get("banID", []))
                vip_list = len(data.get("vips", []))
        except FileNotFoundError:
            bot.reply_to(message, "❌ Файл конфигурации не найден.")
            return
        except json.JSONDecodeError:
            bot.reply_to(message, "❌ Ошибка чтения файла конфигурации.")
            return
        except Exception as e:
            bot.reply_to(message, f"❌ Произошла неожиданная ошибка: {e}")
            return

        try:
            player_list = len(dball())
        except Exception as e:
            player_list = f"Ошибка: {e}"

        ram_usage = psutil.virtual_memory().percent // 10
        cpu_usage = psutil.cpu_percent()
        disk_usage = get_disk_usage()
        ping_time = get_ping()

        status_message = (
            f'Всего создано аккаунтов: {player_list}\n'
            f'Игроков в бане: {ban_list}\n'
            f'Игроков с VIP: {vip_list}\n\n'
            f'RAM: {ram_usage}%\n'
            f'CPU: {cpu_usage}%\n'
            f'Диск: {disk_usage}%\n'
            f'Пинг: {ping_time} ms'
        )
        bot.reply_to(message, status_message)
    else:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        
@bot.message_handler(commands=['resetclubs'])
def reset_clubs_command(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У вас нет прав для выполнения этой команды.")
        return

    try:
        with sqlite3.connect('database/Player/plr.db') as plr_conn:
            plr_cursor = plr_conn.cursor()

            plr_cursor.execute("UPDATE plrs SET ClubID = 0, ClubRole = 0")
            plr_conn.commit()

        club_files = ['database/Club/clubs.db', 'database/Club/chats.db']
        for file in club_files:
            if os.path.exists(file):
                os.remove(file)

        bot.send_message(message.chat.id, "✅ Данные клубов были успешно сброшены и файлы удалены.")
    except Exception as e:
        logger.error(f"Error in /resetclubs command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
dbplayers = 'database/Player/plr.db'
dbclubs = 'database/Club/clubs.db'
dbchat = 'database/Club/chats.db'
        
@bot.message_handler(commands=['bd'])
def handle_bd_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Вы не имеете прав для выполнения этой команды.")
        return

    files = [dbplayers, dbclubs, dbchat]

    for file_path in files:
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                bot.send_document(chat_id=message.chat.id, document=file, caption=f'Файл: {os.path.basename(file_path)}')
        else:
            bot.reply_to(message, f"❌ Файл {os.path.basename(file_path)} не найден")

    bot.reply_to(message, "✅ Все доступные файлы отправлены в Telegram.")
    
@bot.message_handler(commands=['addcode'])
def new_code(message):
    user_id = message.from_user.id
    if user_id in creator2 or user_id in creator3:
        with sqlite3.connect('users.db') as users_conn:
            users_cursor = users_conn.cursor()
            users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            row = users_cursor.fetchone()

            if row:
                lowID = row[0]
                with sqlite3.connect('database/Player/plr.db') as plr_conn:
                    plr_cursor = plr_conn.cursor()
                    plr_cursor.execute("SELECT SCC FROM plrs WHERE lowID = ?", (lowID,))
                    code_row = plr_cursor.fetchone()

                    if code_row and code_row[0]:
                        bot.reply_to(message, "❌ Вы уже имеете код. Удалите его, прежде чем создать новый.")
                        return

                if len(message.text.split()) < 2:
                    bot.reply_to(message, "Правильное использование /code [new code](На англ)")
                else:
                    code = message.text.split()[1]
                    with open("config.json", "r", encoding='utf-8') as f:
                        config = json.load(f)
                    if code not in config["CCC"]:
                        config["CCC"].append(code)
                        with open("config.json", "w", encoding='utf-8') as f:
                            json.dump(config, f, indent=4)

                        plr_cursor.execute("UPDATE plrs SET SCC = ? WHERE lowID = ?", (code, lowID))
                        plr_conn.commit()

                        bot.send_message(chat_id=message.chat.id, text=f"✅ Новый код {code} был добавлен!")
                    else:
                        bot.send_message(chat_id=message.chat.id, text=f"❌ Код {code} уже существует!")
            else:
                bot.reply_to(message, "❌ Вы не привязали аккаунт. Используйте команду /connect.")
    else:
        bot.reply_to(message, "❌ Вы не являетесь контентмейкером!")


@bot.message_handler(commands=['event1'])
def event1(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите 'true' или 'false'.")
        return

    value = message.text.split()[1].lower()

    if value == "true":
        EventSettings.set_double_trophies(True)
        bot.send_message(message.chat.id, "DOUBLE_TROPHIES установлено на True.")
    elif value == "false":
        EventSettings.set_double_trophies(False)
        bot.send_message(message.chat.id, "DOUBLE_TROPHIES установлено на False.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, укажите 'true' или 'false'.")

    # Для отладки
    print("DOUBLE_TROPHIES:", EventSettings.get_double_trophies())

@bot.message_handler(commands=['event2'])
def event2(message: types.Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    if len(message.text.split()) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите 'true' или 'false'.")
        return

    value = message.text.split()[1].lower()

    if value == "true":
        EventSettings.set_double_tokens(True)
        bot.send_message(message.chat.id, "DOUBLE_TOKENS установлено на True.")
    elif value == "false":
        EventSettings.set_double_tokens(False)
        bot.send_message(message.chat.id, "DOUBLE_TOKENS установлено на False.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, укажите 'true' или 'false'.")

    # Проверка установленных значений
    print("DOUBLE_TOKENS:", EventSettings.get_double_tokens())
        
@bot.message_handler(commands=['delcode'])
def del_code(message):
    user_id = message.from_user.id
    if user_id in creator2 or user_id in creator3:
        with sqlite3.connect('users.db') as users_conn:
            users_cursor = users_conn.cursor()
            users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            row = users_cursor.fetchone()

            if row:
                lowID = row[0]
                with sqlite3.connect('database/Player/plr.db') as plr_conn:
                    plr_cursor = plr_conn.cursor()
                    plr_cursor.execute("SELECT SCC FROM plrs WHERE lowID = ?", (lowID,))
                    code_row = plr_cursor.fetchone()

                    if code_row and code_row[0]:
                        code = code_row[0]
                        with open("config.json", "r", encoding='utf-8') as f:
                            config = json.load(f)

                        if code in config["CCC"]:
                            config["CCC"].remove(code)
                            with open("config.json", "w", encoding='utf-8') as f:
                                json.dump(config, f, indent=4)

                            plr_cursor.execute("UPDATE plrs SET SCC = NULL WHERE lowID = ?", (lowID,))
                            plr_conn.commit()

                            bot.send_message(chat_id=message.chat.id, text=f"✅ Код {code} был удалён!")
                        else:
                            bot.send_message(chat_id=message.chat.id, text="❌ Код не найден!")
                    else:
                        bot.send_message(chat_id=message.chat.id, text="❌ У вас нет кода для удаления.")
            else:
                bot.reply_to(message, "❌ Вы не привязали аккаунт. Используйте команду /connect.")
    else:
        bot.reply_to(message, "❌ Вы не являетесь контентмейкером!")
    
bot.polling(none_stop=True)
