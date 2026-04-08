import json
import time

from Utils.Writer import Writer
from database.DataBase import DataBase


class Notifications(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.timestamp = int(time.time())

    @staticmethod
    def _get_notifications(owner):
        player = getattr(owner, "player", owner)
        notifications = getattr(player, "notifications", {})

        if isinstance(notifications, dict):
            return notifications
        if not notifications:
            return {}
        return json.loads(notifications)

    @staticmethod
    def GetNotifCount(owner):
        return len(Notifications._get_notifications(owner))

    @staticmethod
    def GetNotifByIndex(owner, index):
        return Notifications._get_notifications(owner).get(str(index))

    @staticmethod
    def UpdateNotifData(owner, index):
        notifications = Notifications._get_notifications(owner)
        if str(index) in notifications:
            notifications[str(index)]['Read'] = True
        owner.player.notifications = json.dumps(notifications)
        DataBase.replaceValue(owner, "notifications", json.dumps(notifications))
