import string
import random

class Helpers:
    game1 = [{"LogicGameObjects": 2}, {"id": 1, "hp": 3000, "immun": True, "UltiPress": False, "UltiCharge": 0, "battleX": 3150, "battleY": 6725, "angle": 270}, {"id": 228, "hp": 3000, "immun": True, "UltiPress": False, "UltiCharge": 0, "battleX": 3150, "battleY": 3725, "angle": 180}]
    rooms = []

    def randomStringDigits(self):
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join(random.choice(lettersAndDigits) for i in range(40))
    
    def randomID(self):
        used_ids_for_random = set()
        length = 6
        while True:
            new_id = int(''.join([str(random.randint(0, 9)) for _ in range(length)]))  # Генерация 6-значного ID
            if new_id not in used_ids_for_random:
                used_ids_for_random.add(new_id)
                return new_id
    
    def randomClubID(self):
        used_ids_for_club = set()
        length = 9
        while True:
            new_id = int(''.join([str(random.randint(0, 9)) for _ in range(length)]))
            if new_id not in used_ids_for_club:
                used_ids_for_club.add(new_id)
                return new_id
    
    def generateID(self, length=6):
        used_ids_for_generate = set()
        while True:
            new_id = int(''.join([str(random.randint(0, 6)) for _ in range(length)]))
            if new_id not in used_ids_for_generate:
                used_ids_for_generate.add(new_id)
                return new_id