from Utils.Reader import BSMessageReader
from database.DataBase import DataBase


class AccountIdentifiersMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        # Keep the opaque payload as-is. It is stable enough to be used as a
        # fallback identity when the client does not resend the saved token.
        self.player.account_identifiers = self.read().hex()

    def process(self):
        if getattr(self.player, "low_id", 0) >= 2 and getattr(self.player, "token", ""):
            DataBase.bindAccountIdentifiers(self, self.player.account_identifiers)
