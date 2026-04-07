from Utils.Writer import Writer
from Files.CsvLogic.Regions import Regions
class SetRegionResponseMessage(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24178
        self.player = player

    def encode(self):
        self.writeVint(0)
        self.writeScId(14, self.player.regionName)
        print("Cменили регион2")