from Utils.Reader import Reader
from Files.CsvLogic.Regions import Regions
from Server.SetRegionResponseMessage import SetRegionResponseMessage
from database.DataBase import DataBase

class SetRegionMessage(Reader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.id = 12998
        self.player = player
        self.client = client

    def decode(self):
        self.readVInt()
        self.regionName = self.readVInt()
        self.readVInt()

    def process(self, db):
        self.player.regionName = self.regionName
        region = Regions.getIDByRegion(self, self.player.regionName)
        self.player.Region = region
        DataBase.replaceValue(self, 'Region', self.player.Region)
        SetRegionResponseMessage(self.client, self.player).send()
        print("Cменили регион")
