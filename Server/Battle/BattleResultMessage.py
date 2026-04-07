from Utils.Writer import Writer
from database.DataBase import DataBase
import sys
import os
import random
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class BattleResultMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 23456
        self.player = player
        self.double_tokens = self.load_config()
        self.double_trophies = self.load_config2()
        
    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                return config.get("DoubleTokensEvent", False)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return False
        
    def load_config2(self):
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                return config.get("DoubleTrophiesEvent", False)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return False

    def encode(self):
        brawler_trophies = self.player.brawlers_trophies[str(self.player.brawler_id)]
        tropGained = 0
        tokenGained = 0

        # Устанавливаем значения трофеев в зависимости от диапазона трофеев игрока
        rank_values = {
            (0, 49): (10, 8, 5, 4, 3, 2, 0, 0, 0, 0),
            (50, 99): (10, 8, 6, 5, 4, 2, 0, 0, 0, 0),
            (100, 249): (10, 8, 6, 4, 3, 0, 0, -1, -2, -2),
            (250, 399): (10, 8, 5, 3, 0, -2, -2, -2, -2, -3),
            (400, 499): (10, 8, 4, 3, 0, -1, -2, -2, -3, -3),
            (500, 649): (10, 8, 3, 2, -1, -2, -3, -3, -3, -3),
            (650, 799): (10, 7, 2, 0, -2, -3, -3, -3, -3, -4),
            (800, 899): (9, 6, 1, 0, -2, -3, -3, -4, -4, -4),
            (900, 1099): (7, 5, 0, -2, -2, -3, -3, -4, -4, -4),
            (1100, 1249): (5, 4, -1, -2, -3, -3, -4, -4, -4, -5),
            (1250, 9999999): (6, 2, -3, -5, -6, -7, -8, -9, -10, -11)
        }


        # Определяем значения трофеев для текущего диапазона
        for (min_trophies, max_trophies), ranks in rank_values.items():
            if min_trophies <= brawler_trophies <= max_trophies:
                rank_1_val, rank_2_val, rank_3_val, rank_4_val, rank_5_val, rank_6_val, rank_7_val, rank_8_val, rank_9_val, rank_10_val = ranks
                break

        # Определяем трофеи и токены, основываясь на ранге игрока
        if self.player.rank == 1:
            tropGained = rank_1_val
            tokenGained = 20
        elif self.player.rank == 2:
            tropGained = rank_2_val
            tokenGained = 20
        elif self.player.rank == 3:
            tropGained = rank_3_val
            tokenGained = 20
        elif self.player.rank == 4:
            tropGained = rank_4_val
            tokenGained = 15
        elif self.player.rank == 5:
            tropGained = rank_5_val
            tokenGained = 15
        elif self.player.rank == 6:
            tropGained = rank_6_val
            tokenGained = 15
        elif self.player.rank == 7:
            tropGained = rank_7_val
            tokenGained = random.randint(10, 15)
        elif self.player.rank == 8:
            tropGained = rank_8_val
            tokenGained = random.randint(10, 15)
        elif self.player.rank == 9:
            tropGained = rank_9_val
            tokenGained = random.randint(1, 10)
        elif self.player.rank == 10:
            tropGained = rank_10_val
            tokenGained = random.randint(1, 10)
            

        # Запись результатов
        self.writeVint(2)  # Battle End Game Mode
        self.writeVint(self.player.rank)  # Result
        self.writeVint(tokenGained)  # Tokens Gained
        if tropGained >= 0:
            if self.player.vip == 1:
                tropGained += 15
                self.writeVint(tropGained * 2 if self.double_trophies else tropGained)  # Trophies Result
            else:
                self.writeVint(tropGained * 2 if self.double_trophies else tropGained)  # Trophies Result
        else:
            self.writeVint(-65 - (tropGained))  # Trophies Result

        self.writeVint(0)  # Unknown (Power Play Related)
        if self.player.vip == 1:
            self.writeVint(125)  # Doubled Tokens
            tokenGained += 125
        else:
            self.writeVint(0)  # Doubled Tokens
        self.writeVint(tokenGained if self.double_tokens else 0) # Double Token Event
        self.writeVint(0) # Token Doubler Remaining
        self.writeVint(0) # Big Game/Robo Rumble Time
        self.writeVint(0) # Unknown (Championship Related)
        self.writeVint(0) # Championship Level Passed
        self.writeVint(0) # Challenge Reward Type (0 = Star Points, 1 = Star Tokens)
        self.writeVint(0) # Challenge Reward Ammount
        self.writeVint(0) # Championship Losses Left
        self.writeVint(0) # Championship Maximun Losses
        self.writeVint(0) # Coin Shower Event
        if tropGained > 0:
            if self.player.vip == 1:
                self.writeVint(15) # Underdog Trophies
            else:
                self.writeVint(0) # Underdog Trophies
        else:
            self.writeVint(0) # Underdog Trophies
        self.writeVint(16)# 48-спектатор 32-дружеская 16-обычная победа (-16) - повер плей
        self.writeVint(-64) # Championship Challenge Type
        self.writeVint(0) # Championship Cleared and Beta Quests
            
        # Players Array
        self.writeVint(6) # Battle End Screen Players
        
        self.writeVint(1) # Team and Star Player Type
        self.writeScId(16, self.player.brawler_id) # Player Brawler
        self.writeScId(29, self.player.skin_id) # Player Skin
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)]) # Your Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(self.player.brawlerPowerLevel.get(str(self.player.brawler_id), 0) + 1)
        self.writeBoolean(True) # HighID and LowID Array
        self.writeInt(0) # HighID
        self.writeInt(self.player.low_id) # LowID
        self.writeString(self.player.name) # Your Name
        self.writeVint(self.player.player_experience) # Player Experience Level
        self.writeVint(28000000 + self.player.profile_icon) # Player Profile Icon
        self.writeVint(43000000 + self.player.name_color) # Player Name Color
        if self.player.vip == 1:
            self.writeVint(43000000 + self.player.name_color) # Player Name Color
        else:
            self.writeVint(0) # Player Name Color

        self.writeVint(0) # Team and Star Player Type
        self.writeScId(16, self.player.bot1) # Bot 1 Brawler
        self.writeVint(0) # Bot 1 Skin
        self.writeVint(0) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(1) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.player.bot1_n) # Bot 1 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color
            
        self.writeVint(0) # Team and Star Player Type
        self.writeScId(16, self.player.bot2) # Bot 2 Brawler
        self.writeVint(0) # Bot 2 Skin
        self.writeVint(0) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(1) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.player.bot2_n) # Bot 2 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color

        self.writeVint(2) # Team and Star Player Type
        self.writeScId(16, self.player.bot3) # Bot 3 Brawler
        self.writeVint(0) # Bot 3 Skin
        self.writeVint(0) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(1) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.player.bot3_n) # Bot 3 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color

        self.writeVint(2) # Team and Star Player Type
        self.writeScId(16, self.player.bot4) # Bot 4 Brawler
        self.writeVint(0) # Bot 4 Skin
        self.writeVint(0) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(1) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.player.bot4_n) # Bot 4 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color

        self.writeVint(2) # Team and Star Player Type
        self.writeScId(16, self.player.bot5) # Bot 5 Brawler
        self.writeVint(0) # Bot 5 Skin
        self.writeVint(0) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(1) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.player.bot5_n) # Bot 5 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color
        
        # Experience Array
        self.writeVint(2) # Count
        self.writeVint(0) # Normal Experience ID
        self.writeVint(10) # Normal Experience Gained
        self.writeVint(8) # Star Player Experience ID
        self.writeVint(0) # Star Player Experience Gained

        # Rank Up and Level Up Bonus Array
        self.writeVint(0) # Count

        # Trophies and Experience Bars Array
        self.writeVint(2) # Count
        self.writeVint(1) # Trophies Bar Milestone ID
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)]) # Brawler Trophies
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)]) # Brawler Trophies for Rank
        self.writeVint(5) # Experience Bar Milestone ID
        self.writeVint(self.player.player_experience) # Player Experience
        self.writeVint(0) # Player Experience for Level
        
        self.writeScId(28, 0)  # Player Profile Icon (Unused since 2017)
        self.writeBoolean(False)  # Play Again
        if self.player.name != "VBC26":
            if self.double_trophies:
                self.player.bet = tropGained * 2
            else:
                self.player.bet = tropGained
            if self.double_tokens:
                self.player.betTok = tokenGained * 2
            else:
                self.player.betTok = tokenGained
            self.player.brawlers_trophies[str(self.player.brawler_id)] += self.player.bet
            DataBase.replaceValue(self, 'brawlersTrophies', self.player.brawlers_trophies)
            self.player.BPTOKEN = self.player.BPTOKEN + tokenGained
            DataBase.replaceValue(self, 'BPTOKEN', self.player.BPTOKEN)
            self.player.sdWINS = self.player.sdWINS + 1
            DataBase.replaceValue(self, 'sdWINS', self.player.sdWINS)
            self.player.player_experience += 10
            DataBase.replaceValue(self, 'playerExp', self.player.player_experience)
            
            brawler_trophies = self.player.brawlers_trophies[str(self.player.brawler_id)]
            DataBase.replaceValue(self, 'brawlersTrophies', self.player.brawlers_trophies)