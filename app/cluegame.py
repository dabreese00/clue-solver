from enum import Enum

class CluePersonCard(Enum):
    COLONEL_MUSTARD = "Colonel Mustard"
    MISS_SCARLET = "Miss Scarlet"

class ClueWeaponCard(Enum):
    ROPE = "Rope"
    LEAD_PIPE = "Lead pipe"

class ClueRoomCard(Enum):
    BILLIARD_ROOM = "Billiard Room"
    BALLROOM = "Ballroom"

class CluePlayer:
    def __init__(self, name, hand_size):
        self.name = name
        self.hand_size = hand_size
        self.show = 0
        self.card_knowledge = {}
        for c in (CluePersonCard + ClueWeaponCard + ClueRoomCard):


    def record_show(cards):
        for card in cards:
            self.potential_cards[card] = self.show
        self.show += 1

class ClueCard:
    def __init__(self, name):
        self.name = name

class ClueGame:
    total_cards = 21
    num_card_types = 3

    def __init__(self, players):
        if ( sum(p.hand_size for p in players) == self.total_cards - self.num_card_types ):
            self.players = players
        else:
            raise ValueError('Invalid player hand sizes')

    def __validate_show_pass(self, player_name, person, weapon, room):
        if not ( player_name in ( p.name for p in self.players ) ):
            raise ValueError('There is no such player as {} in this game'.format(player_name))
        if not ( person in CluePersonCard and weapon in ClueWeaponCard and room in ClueRoomCard ):
            raise ValueError('Invalid person, weapon, or room card.')

    def record_pass(self, player_name, person, weapon, room):
        self.__validate_show_pass(player_name, person, weapon, room)
        return 'Player {} has passed'.format(player_name)

    def record_show(self, player_name, person, weapon, room):
        self.__validate_show_pass(player_name, person, weapon, room)
        return 'Player {} has shown'.format(player_name)
