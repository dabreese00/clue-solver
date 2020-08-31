from enum import Enum


class ClueCardType(Enum):
    PERSON = "Person"
    WEAPON = "Weapon"
    ROOM = "Room"

class Player:
    def __init__(self, name, hand_size):
        self.name = name
        self.hand_size = hand_size

class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type

# A yes/no: Does this player have this card?
# Created when this fact is known.
class Have:
    def __init__(self, player, card, have):
        self.player = player
        self.card = card
        self.have = have

# A 4-way relationship between a player and 3 cards.
# Created when a player shows a card to someone else.
class Show:
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards

class Game:
    clue_cards = {
        ClueCardType.PERSON: ["Colonel Mustard", "Miss Scarlet"],
        ClueCardType.WEAPON: ["Rope", "Lead pipe"],
        ClueCardType.ROOM: ["Billiard Room", "Ballroom"]
        }

    def __init__(self, myself, other_players):
        self.myself = myself
        self.players = other_players.copy()
        self.players.append(myself)

        self.cards = []
        for t in ClueCardType:
            for c in self.clue_cards[t]:
                self.cards.append(Card(c, t))

        haves = []
        shows = []

    def record_have(self, player, card):
        pass
        # 0. Record the have.
        # 1. Mark passes for all other players
        # 2. If all the player's cards are accounted for, mark passes for all other cards.
        # 3. If all but 1 card of this ClueCardType are accounted for, mark
        #     passes for all players for the remaining card.
        # 4. If the player has this card in any of their "shows", void those shows.

    def record_pass(self, player, card):
        pass
        # 0. Record the pass.
        # 1. If the passing player & card are in any Shows together, check if
        #    the Shows have "popped".  If so, record a Have and void the Show.

    def record_show(self, player, card):
        pass
        # 0. Record the show.
        # 1. Check if the Show has "popped".  If so, record a Have and void the Show.

    def input_hand(self, cards):
        for c in cards:
            record_have(self.myself, c)
