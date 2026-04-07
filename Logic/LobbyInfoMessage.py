from Utils.Writer import Writer
from datetime import datetime
from ping3 import ping
from shared import connected_ips

class LobbyInfoMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 23457
        self.player = player
        self.domain = '107.161.154.201'

    def get_ping(self):
        """Calculate the ping in milliseconds or return 'N/A'."""
        ping_seconds = ping(self.domain)
        if ping_seconds is None:
            return 'N/A'

        ping_ms = int(ping_seconds * 4000)
        return '<1' if ping_ms == 0 and ping_seconds > 0 else ping_ms

    def encode(self):
        now = datetime.now()
        ping_ms = self.get_ping()
        ip_count = len(connected_ips)
        message = (
            f'Monrax Brawl\n'
            f'Version: 29(34)Prod\n'
            f'TG: @MonraxBRAWL\n'
            f'Пинг: {ping_ms}ms\n'
            f'Онлайн: {ip_count}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n:)\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
        )
        self.writeVint(0)
        self.writeString(message)
        self.writeVint(0)