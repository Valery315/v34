from Utils.Writer import Writer
from database.DataBase import DataBase
import json

class PlayerProfileMessage(Writer):

    def __init__(self, client, player, high_id, low_id, players):
        super().__init__(client)
        self.id = 24113
        self.player = player
        self.high_id = high_id
        self.low_id = low_id
        self.players = players
        
        # Initialize attributes for club data
        self.clubName = ""
        self.clubbadgeID = 0
        self.clubtype = 0
        self.clubmembercount = 0
        self.clubtrophies = 0
        self.clubtrophiesneeded = 0
        self.clubregion = ""

    @staticmethod
    def _normalize_brawler_data(data):
        return {
            "highest_trophies": int(data.get("highest_trophies", 0)),
            "brawlersTrophies": data.get("brawlersTrophies", {}) or {},
            "UnlockedBrawlers": data.get("UnlockedBrawlers", {}) or {},
            "UnlockedSkins": data.get("UnlockedSkins", {}) or {},
            "brawlerPowerLevel": data.get("brawlerPowerLevel", {}) or {},
            "brawlerPoints": data.get("brawlerPoints", {}) or {},
            "StarPowerUnlocked": data.get("StarPowerUnlocked", {}) or {},
            "UnlockedPins": data.get("UnlockedPins", {}) or {},
        }

    @staticmethod
    def _normalize_player_data(data):
        return {
            "Test": int(data.get("Test", 0)),
            "Debacle": int(data.get("Debacle", 0)),
            "Boss_Fight": int(data.get("Boss_Fight", 0)),
            "Robo_Cabin": int(data.get("Robo_Cabin", 0)),
            "Power_Race": int(data.get("Power_Race", 0)),
            "Duo_Wins": int(data.get("Duo_Wins", 0)),
        }

    def encode(self):
        player = self.players

        if player is not None:
            name = player[2]
            trophies = int(player[3] or 0)
            profile_icon = int(player[9] or 0)
            name_color = int(player[10] or 0)
            club_id = int(player[11] or 0)
            club_role = int(player[12] or 0)
            player_exp = int(player[21] or 0)
            trio_wins = int(player[24] or 0)
            solo_wins = int(player[25] or 0)
            brawlerData = self._normalize_brawler_data(json.loads(player[13]))
            playerData = self._normalize_player_data(json.loads(player[38]))
        else:
            name = self.player.name
            trophies = int(getattr(self.player, "trophies", 0) or 0)
            profile_icon = int(getattr(self.player, "profile_icon", 0) or 0)
            name_color = int(getattr(self.player, "name_color", 0) or 0)
            club_id = int(getattr(self.player, "club_low_id", 0) or 0)
            club_role = int(getattr(self.player, "club_role", 0) or 0)
            player_exp = int(getattr(self.player, "player_experience", 0) or 0)
            trio_wins = int(getattr(self.player, "trioWINS", 0) or 0)
            solo_wins = int(getattr(self.player, "sdWINS", 0) or 0)
            brawlerData = self._normalize_brawler_data({
                "highest_trophies": getattr(self.player, "highest_trophies", 0),
                "brawlersTrophies": getattr(self.player, "brawlers_trophies", {}),
                "UnlockedBrawlers": getattr(self.player, "UnlockedBrawlers", {}),
                "UnlockedSkins": getattr(self.player, "UnlockedSkins", {}),
                "brawlerPowerLevel": getattr(self.player, "brawlerPowerLevel", {}),
                "brawlerPoints": getattr(self.player, "brawlerPoints", {}),
                "StarPowerUnlocked": getattr(self.player, "StarPowerUnlocked", {}),
                "UnlockedPins": getattr(self.player, "UnlockedPins", {}),
            })
            playerData = self._normalize_player_data({
                "Test": getattr(self.player, "test", 0),
                "Debacle": getattr(self.player, "debacle", 0),
                "Boss_Fight": getattr(self.player, "boss_fight", 0),
                "Robo_Cabin": getattr(self.player, "robo_cabin", 0),
                "Power_Race": getattr(self.player, "power_race", 0),
                "Duo_Wins": getattr(self.player, "duo_wins", 0),
            })

        self.writeVint(0)  # High Id
        self.writeVint(self.low_id)  # Low Id
        self.writeVint(0)  # Unknown
        brawlersToCheck = [LkPrtctrd for LkPrtctrd, LkPrtctnd in brawlerData["UnlockedBrawlers"].items() if LkPrtctnd and int(LkPrtctrd) < 46]
        self.writeVint(len(brawlersToCheck))  # Brawlers array
        for brawler in brawlersToCheck:
            if True:
                self.writeScId(16, int(brawler))
                self.writeVint(0)
                self.writeVint(int(brawlerData["brawlersTrophies"][str(brawler)]))  # Trophies for rank
                self.writeVint(int(brawlerData["brawlersTrophies"][str(brawler)]))  # Trophies
                self.writeVint(0)  # Power level

        self.writeVint(15)
        self.writeVint(1)
        self.writeVint(trio_wins)  # 3v3 victories
        self.writeVint(2)
        self.writeVint(player_exp)  # Player experience
        self.writeVint(3)
        self.writeVint(trophies)  # Trophies
        self.writeVint(4)
        self.writeVint(brawlerData['highest_trophies'])  # Highest trophies
        self.writeVint(5)
        self.writeVint(len(brawlersToCheck))  # Brawlers list
        self.writeVint(7)
        self.writeVint(28000000 + profile_icon)  # Profile icon
        self.writeVint(8)
        self.writeVint(solo_wins)  # Solo victories
        self.writeVint(9)
        self.writeVint(playerData['Robo_Cabin'])  # 794 Роборубка
        self.writeVint(10)
        self.writeVint(0)  # 794 Большой бравлер (not user)
        self.writeVint(11)
        self.writeVint(playerData['Duo_Wins'])  # Duo victories
        self.writeVint(12)
        self.writeVint(playerData['Boss_Fight'])  # Бой с боссом
        self.writeVint(13)
        self.writeVint(playerData['Power_Race'])  # Highest power player points
        self.writeVint(14)
        self.writeVint(0)  # Highest power play rank
        self.writeVint(15)
        self.writeVint(playerData['Test'])  # Испытания
        self.writeVint(16)
        self.writeVint(playerData['Debacle']) #Разгром Суперсити

        with open('config.json', 'r') as file:
            config = json.load(file)
        if self.low_id in config['vips']:
            self.writeString(f"{name}")
        else:
            self.writeString(f"{name}")
        self.writeVint(100)
        self.writeVint(28000000 + profile_icon)  # Profile icon
        self.writeVint(43000000 + name_color)  # Name color
        if self.low_id in config['vips']:
            self.writeVint(43000000 + name_color)  # Name color
        else:
            self.writeVint(0)  # Name color

        if club_id != 0:
            DataBase.loadClub(self, club_id)
            self.writeBoolean(True)  # Is in club
            self.writeInt(0)
            self.writeInt(club_id)
            self.writeString(self.clubName)  # Club name
            self.writeVint(8)
            self.writeVint(self.clubbadgeID)  # Club badgeID
            self.writeVint(self.clubtype)  # Club type | 1 = Open, 2 = invite only, 3 = closed
            self.writeVint(self.clubmembercount)  # Current members count
            self.writeVint(self.clubtrophies)
            self.writeVint(self.clubtrophiesneeded)  # Trophy required
            self.writeVint(0)  # (Unknown)
            self.writeString(self.clubregion)  # Region
            self.writeVint(0)  # (Unknown)
            self.writeVint(0)  # (Unknown)
            self.writeVint(25)
            self.writeVint(club_role)
        else:
            self.writeVint(0)
            self.writeVint(0)
