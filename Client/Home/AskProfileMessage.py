from Server.Home.PlayerProfileMessage import PlayerProfileMessage
from Utils.Reader import BSMessageReader
from database.DataBase import DataBase


class AskProfileMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.high_id = self.read_int()
        self.low_id = self.read_int()
        requested_low_id = self.low_id if self.low_id >= 2 else self.player.low_id
        self.players = DataBase.loadbyID(self, requested_low_id)

        # Some clients ask profile/settings with low_id=0. Fall back to the current account.
        if self.players is None and self.player.low_id >= 2:
            self.low_id = self.player.low_id
            self.high_id = self.player.high_id
            self.players = DataBase.loadbyID(self, self.player.low_id)


    def process(self):
        if self.players is None and self.player.low_id < 2:
            return
        PlayerProfileMessage(self.client, self.player, self.high_id, self.low_id, self.players).send()
