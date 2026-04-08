import os
import json
import requests  # Добавляем импорт
from ipwhois import IPWhois
from Server.Login.LoginOkMessage import LoginOkMessage
from Server.Home.OwnHomeDataMessage import OwnHomeDataMessage
from Server.Login.LoginFailedMessage import LoginFailedMessage
from Utils.Helpers import Helpers
from Utils.Network import is_internal_proxy_ip
from database.DataBase import DataBase
from Server.Club.MyAllianceMessage import MyAllianceMessage
from Server.Club.AllianceStreamMessage import AllianceStreamMessage
from Server.Friend.FriendListMessage import FriendListMessage
from database.DevMessage import DevMessage
from Utils.Reader import BSMessageReader


class LoginMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):  # Убираем аргумент server
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.player.high_id = self.read_int()
        self.player.low_id = self.read_int()
        self.player.token = self.read_string()
        self.major = self.read_int()
        self.minor = self.read_int()
        self.build = self.read_int()

    def create_fresh_account(self):
        plrsinfo = "database/Player/plr.db"
        if os.path.exists(plrsinfo):
            self.player.low_id = Helpers.randomID(self)
        else:
            self.player.low_id = 2

        self.player.token = Helpers().randomStringDigits()
        self.player.high_id = 0
        DataBase.createAccount(self)

    def process(self):
        if self.major != 29 or self.major >= 35:
            self.player.err_code = 8
            self.player.update_url = 't.me/Maxamed18'
            LoginFailedMessage(self.client, self.player, f"Отличные новости! Доступна новая версия MonraxBrawl. Чтобы сыграть в приватный сервер купите Ранний Доступ!").send()
            return

        with open('config.json', 'r') as config:
            settings = json.load(config)
        
        # Проверка на бан
        if self.player.low_id in settings['banID']:
            print("banned")
            self.player.err_code = 11
            LoginFailedMessage(self.client, self.player, "Вы заблокированы. Подать аппеляцию можно написав админу - @zoxdev").send()
            return

        if settings['maintenance']:
            self.player.err_code = 10
            LoginFailedMessage(self.client, self.player, "").send()
            return
        
        client_ip = self.client.getpeername()[0]
        
        # Определение региона по IP
        region = self.get_region_by_ip(client_ip)

        # Добавьте регион в объект игрока, если нужно сохранить его
        self.player.Region = region
        
        
        # Создание нового аккаунта
        if self.player.low_id == 0:
            self.create_fresh_account()

        
        # Проверка существующего аккаунта
        if self.player.low_id >= 2:
            if not DataBase.accountExists(self):
                self.create_fresh_account()

            if not DataBase.loadAccount(self):
                return

            LoginOkMessage(self.client, self.player).send()
            OwnHomeDataMessage(self.client, self.player).send()
            try:
                MyAllianceMessage(self.client, self.player, self.player.club_low_id).send()
                AllianceStreamMessage(self.client, self.player, self.player.club_low_id, 0).send()
                DataBase.GetmsgCount(self, self.player.club_low_id)
            except:
                MyAllianceMessage(self.client, self.player, 0).send()
                AllianceStreamMessage(self.client, self.player, 0, 0).send()
            FriendListMessage(self.client, self.player).send()
            DevMessage(self.client, self.player).send()
        else:
            self.player.err_code = 8
            LoginFailedMessage(self.client, self.player, "Аккаунт не найден, удалите все данные о игре!").send()
            
    def get_region_by_ip(self, ip_address):
        """Метод для определения региона по IP"""
        if not ip_address or is_internal_proxy_ip(ip_address):
            return 'Unknown'

        try:
            url = f'http://ip-api.com/json/{ip_address}'
            response = requests.get(url, timeout=3)
            data = response.json()
            if data.get('status') == 'fail':
                return 'Unknown'
            return data.get('countryCode', 'Unknown')  # Извлекаем регион
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении региона: {e}")
            return 'Unknown'
