from Utils.Reader import BSMessageReader


class SetDeviceTokenMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client
        self.payload_size = len(initial_bytes)

    def decode(self):
        # The client may send a push/device token when opening settings.
        # The private server does not need it, but the packet must be accepted.
        self.device_token_payload = self.read()

    def process(self):
        print(f"[ИНФО] Handled packet 10113 (len={self.payload_size}) for low_id={self.player.low_id}")
