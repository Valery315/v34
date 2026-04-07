import json
import time

from Utils.Writer import Writer
from database.DataBase import DataBase


class Notifications(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.timestamp = int(time.time())

    def GetNotifCount(self):
        return len(json.loads(self.player.notifications))

    def GetNotifByIndex(self, index):
        return json.loads(self.player.notifications).get(str(index))

    def UpdateNotifData(self, index):
        notifications = json.loads(self.player.notifications)
        if str(index) in notifications:
            notifications[str(index)]['Read'] = True
        self.player.notifications = json.dumps(notifications)
        DataBase.replaceValue(self, "notifications", json.dumps(notifications))
