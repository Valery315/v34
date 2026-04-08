import json
import time

from Utils.Writer import Writer
from database.DataBase import DataBase


class Notifications(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.timestamp = int(time.time())

    def _get_notifications(self):
        if isinstance(self.player.notifications, dict):
            return self.player.notifications
        if not self.player.notifications:
            return {}
        return json.loads(self.player.notifications)

    def GetNotifCount(self):
        return len(self._get_notifications())

    def GetNotifByIndex(self, index):
        return self._get_notifications().get(str(index))

    def UpdateNotifData(self, index):
        notifications = self._get_notifications()
        if str(index) in notifications:
            notifications[str(index)]['Read'] = True
        self.player.notifications = json.dumps(notifications)
        DataBase.replaceValue(self, "notifications", json.dumps(notifications))
