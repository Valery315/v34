import sqlite3
import json
from Utils.Writer import Writer
from Server.Friend.FriendOnlineStatusEntryMessage import FriendOnlineStatusEntryMessage
from database.DataBase import DataBase

class FriendListMessage(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 20105
        self.player = player

    def encode(self):
        try:
            # Подключение к базе данных
            conn = sqlite3.connect('database/Player/plr.db')
            cursor = conn.cursor()

            # Получаем данные о пользователе
            cursor.execute('SELECT * FROM plrs WHERE lowID=?', (self.player.low_id,))
            user = cursor.fetchone()

            if user is None:
                return

            # Загружаем данные о друзьях
            friends_json = user[22]
            friends = json.loads(friends_json)

            # Инициализируем список действительных друзей
            valid_friends = []

            self.writeInt(0)
            self.writeBoolean(True)
            self.writeInt(len(friends))

            for data in friends:
                # Получаем данные о игроке по ID
                self.players = DataBase.loadbyID(self, data["id"])

                if self.players is None:
                    continue  # Пропускаем этого друга, если данные о нём не найдены

                # Добавляем в действительный список друзей
                valid_friends.append(data)

                # Записываем данные друга
                self.writeInt(0)  # HighID
                self.writeInt(self.players[1])  # LowID

                self.writeString('')
                self.writeString('')
                self.writeString('')
                self.writeString('')
                self.writeString('')
                self.writeString('')

                self.writeInt(self.players[3])  # Trophies
                self.writeInt(data["state"])
                self.writeInt(0)
                self.writeInt(0)
                self.writeInt(0)

                self.writeBoolean(False)

                self.writeString('')
                self.writeInt(0)

                self.writeBoolean(True)  # Это игрок?

                # Записываем имя игрока
                if self.players[20] == 1:
                    self.writeString(f"{self.players[2]}")
                else:
                    self.writeString(f"{self.players[2]}")
                
                # Записываем дополнительные данные
                self.writeVint(100)
                self.writeVint(28000000 + self.players[9])
                self.writeVint(43000000 + self.players[10])
                if self.players[20] == 1:
                    self.writeVint(43000000 + self.players[10])  # Цвет имени
                else:
                    self.writeVint(0)  # Цвет имени

                # Отправляем сообщение о статусе онлайн
                FriendOnlineStatusEntryMessage(self.client, self.player, data["id"], self.players[19], self.players[16]).send()

            # Сохраняем обновлённый список друзей в базу данных
            if valid_friends != friends:
                updated_friends_json = json.dumps(valid_friends)
                cursor.execute('UPDATE plrs SET friends=? WHERE lowID=?', (updated_friends_json, self.player.low_id))
                conn.commit()

        except Exception as e:
            print(f"Ошибка при кодировании FriendListMessage для игрока с lowID {self.player.low_id}: {e}")
        finally:
            conn.close()