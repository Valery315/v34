from Utils.Reader import BSMessageReader


class ClientMessage30000(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client
        self.payload_size = len(initial_bytes)

    def decode(self):
        # Newer clients send an extra post-login initialization packet.
        # The current private server does not use its payload yet.
        pass

    def process(self):
        print(f"[ИНФО] Handled packet 30000 (len={self.payload_size}) for low_id={self.player.low_id}")
