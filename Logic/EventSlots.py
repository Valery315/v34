import time
import random
class EventSlots:
    Timer = 86399

    maps = [
        # Status = [3 = Nothing, 2 = Star Token, 1 = New Event]
        {
            'ID': random.choice([7,8,9,10,11,12]), #Гем граб
            'Status': 2,
            'Ended': False,
            'Modifier': 3,
            'Tokens': 10
        },

        {
            'ID': random.choice([13,14,15,16,32,33,43,45]), #Шд
            'Status': 2,
            'Ended': False,
            'Modifier': 1,
            'Tokens': 10
        },
        {
            'ID': random.choice([50,51,132,144,160]), #броулболл
            'Status': 2,
            'Ended': False,
            'Modifier': 3,
            'Tokens': 10
        },
        {
            'ID': random.choice([4,5,54,81,82,83,159,295,301,336,18,19,23,53,81,82,83,302]), #Награда за поимку или банк
            'Status': 2,
            'Ended': False,
            'Modifier': 2,
            'Tokens': 10
        },
        {
            'ID': random.choice([97,98,99,131,142,264]), #осада
            'Status': 2,
            'Ended': False,
            'Modifier': 1,
            'Tokens': 10
        },
        {
            'ID': random.choice([21, 30]), #Большая игра - 21, 30 | Бой с боссом - 57 | Разгром Суперсити - 269 | Роборубка - 68
            'Status': 2,
            'Ended': False,
            'Modifier': 1,
            'Tokens': 10
        },
        {
            'ID': random.choice([57]), #Большая игра - 21, 30 | Бой с боссом - 57 | Разгром Суперсити - 269 | Роборубка - 68
            'Status': 2,
            'Ended': False,
            'Modifier': 1,
            'Tokens': 10
        },
        {
            'ID': random.choice([68]), #Большая игра - 21, 30 | Бой с боссом - 57 | Разгром Суперсити - 269 | Роборубка - 68
            'Status': 2,
            'Ended': False,
            'Modifier': 1,
            'Tokens': 10
        },
        {
            'ID': random.choice([269]), #Большая игра - 21, 30 | Бой с боссом - 57 | Разгром Суперсити - 269 | Роборубка - 68
            'Status': 2,
            'Ended': False,
            'Modifier': 1,
            'Tokens': 10
        }
    ]