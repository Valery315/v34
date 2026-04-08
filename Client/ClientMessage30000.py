import hashlib

from Utils.Reader import BSMessageReader
from database.DataBase import DataBase
from Server.Login.LoginOkMessage import LoginOkMessage
from Server.Home.OwnHomeDataMessage import OwnHomeDataMessage
from Server.Friend.FriendListMessage import FriendListMessage
from Server.Club.MyAllianceMessage import MyAllianceMessage
from Server.Club.AllianceStreamMessage import AllianceStreamMessage
from database.DevMessage import DevMessage


class ClientMessage30000(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client
        self.payload_size = len(initial_bytes)
        self.identifier = ""

    def decode(self):
        payload = self.read()
        digest = hashlib.sha1(payload).hexdigest()
        self.identifier = f"30000:{digest}"

    def process(self):
        current_token = getattr(self.player, "token", "")
        current_low_id = getattr(self.player, "low_id", 0)

        if not self.identifier:
            print(f"[ИНФО] Handled packet 30000 (len={self.payload_size}) for low_id={current_low_id}")
            return

        existing = DataBase.getAccountRow(self, account_identifiers=self.identifier)

        if existing is None:
            self.player.account_identifiers = self.identifier
            DataBase.bindAccountIdentifiers(self, self.identifier)
            print(
                f"[ИНФО] Handled packet 30000 (len={self.payload_size}) "
                f"bound={self.identifier[-12:]} low_id={current_low_id}"
            )
            return

        existing_token = existing[0]
        existing_low_id = existing[1]

        if existing_token == current_token:
            self.player.account_identifiers = self.identifier
            DataBase.bindAccountIdentifiers(self, self.identifier)
            print(
                f"[ИНФО] Handled packet 30000 (len={self.payload_size}) "
                f"same_account={existing_low_id} id={self.identifier[-12:]}"
            )
            return

        restored = DataBase.loadAccount(self, account_identifiers=self.identifier)
        if not restored:
            print(
                f"[ИНФО] Handled packet 30000 (len={self.payload_size}) "
                f"restore_failed id={self.identifier[-12:]}"
            )
            return

        DataBase.rebindTokenToLowID(
            self,
            existing_low_id,
            current_token,
            self.identifier,
            getattr(self.player, "login_identifier", ""),
        )
        restored = DataBase.loadAccount(self, token=current_token)
        if not restored:
            print(
                f"[ИНФО] Handled packet 30000 (len={self.payload_size}) "
                f"rebind_failed low_id={existing_low_id} id={self.identifier[-12:]}"
            )
            return

        # The client has already received a temporary LoginOk for a throwaway low_id.
        # Send LoginOk again with the rebound low_id so the client updates its active account.
        LoginOkMessage(self.client, self.player).send()
        OwnHomeDataMessage(self.client, self.player).send()
        try:
            MyAllianceMessage(self.client, self.player, self.player.club_low_id).send()
            AllianceStreamMessage(self.client, self.player, self.player.club_low_id, 0).send()
        except Exception:
            MyAllianceMessage(self.client, self.player, 0).send()
            AllianceStreamMessage(self.client, self.player, 0, 0).send()
        FriendListMessage(self.client, self.player).send()
        DevMessage(self.client, self.player).send()
        print(
            f"[ИНФО] Handled packet 30000 (len={self.payload_size}) "
            f"restored_low_id={self.player.low_id} rebound_token=yes from_temp={current_low_id} "
            f"id={self.identifier[-12:]}"
        )
