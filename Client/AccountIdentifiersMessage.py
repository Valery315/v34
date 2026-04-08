from Utils.Reader import BSMessageReader


class AccountIdentifiersMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        # Newer clients send account/device identifiers during the login flow.
        # The private server does not need them yet, but the packet must be recognized.
        pass

    def process(self):
        pass
