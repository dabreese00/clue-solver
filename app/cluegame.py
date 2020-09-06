import enum

class ClueCardType(enum.Enum):
    PERSON = "Person"
    WEAPON = "Weapon"
    ROOM = "Room"

class Player:
    def __init__(self, name, hand_size):
        self.name = name
        self.hand_size = hand_size

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "Player(Name={}, Hand size={})".format(self.name, self.hand_size)

class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "Card(Name={}, Type={})".format(self.name, self.card_type)

# A yes/no: Does this player have this card?
# Created when this fact is known.
class Have:
    def __init__(self, player, card, yesno):
        self.player = player
        self.card = card
        self.yesno = yesno

    def overlaps(self, other):
        if type(other) is type(self):
            return self.player == other.player and self.card == other.card
        else:
            return NotImplemented

# A 4-way relationship between a player and 3 cards.
# Created when a player shows a card to someone else.
class Show:
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards.copy()  # Shallow copy, avoid mutating input set
        self.is_void = False

    def remove_card(self, card):
        self.cards.remove(card)

class Game:
    clue_cards = {
        ClueCardType.PERSON: {"Colonel Mustard", "Miss Scarlet", "Professor Plum", "Mrs. White", "Mr. Green", "Mrs. Peacock"},
        ClueCardType.WEAPON: {"Rope", "Lead Pipe", "Revolver", "Candlestick", "Knife", "Wrench"},
        ClueCardType.ROOM: {"Billiard Room", "Ballroom", "Lounge", "Kitchen", "Conservatory", "Library"}
        }

    def __init__(self, myself, other_players):
        self.myself = myself
        self.players = other_players.copy()
        self.players.add(myself)

        self.cards = set()
        for t in ClueCardType:
            for c in self.clue_cards[t]:
                self.cards.add(Card(c, t))

        self.cards_in_the_file = set()

        self.haves = []
        self.shows = []

    def record_have(self, player, card, yesno):

        prospective_have = Have(player, card, yesno)

        # Catch any overlap with existing haves -- Don't record it!
        for h in self.haves:
            if h.overlaps(prospective_have):
                if h.yesno == prospective_have.yesno:
                    return  # Assume this has all been done already; move on.
                else:
                    raise ValueError("Cannot mark Have for {} and {} as {}; the opposite is already marked!".format(player, card, yesno))

        # Now record it!
        self.haves.append(prospective_have)

        # Additional triggered actions
        if yesno:  # we know player has card

            # 1. Mark passes for all other players
            for other_p in self.players:
                if other_p != player:
                    self.record_have(other_p, card, False)

            # 2. If all the player's cards are accounted for, mark passes for all other cards.
            player_known_cards = self.player_known_cards(player, True)
            if len(player_known_cards) == player.hand_size:
                for other_c in self.cards:
                    if other_c not in player_known_cards:
                        self.record_have(player, other_c, False)

            # 3. If all but 1 card of this ClueCardType are accounted for, mark
            #     passes for all players for the remaining card.
            cards_of_type_located = set()
            cards_of_type_total = set()
            for h in self.haves:
                if h.card.card_type == card.card_type:
                    cards_of_type_located.add(h.card)
            for card_name in self.clue_cards[card.card_type]:
                cards_of_type_total.add(self.get_card(card_name))
            if len(cards_of_type_located) == len(cards_of_type_total) - 1:
                remaining_card = (cards_of_type_total - cards_of_type_located).pop()
                for p in self.players:
                    self.record_have(p, remaining_card, False)

            # 4. If the player has this card in any of their "shows", void those shows.
            for s in self.shows:
                if s.player == player and card in s.cards:
                    s.is_void = True

        else:  # we know player does not have card
            # 1. If the passing player & card are in any Shows together, try to "pop"
            #    them.
            for s in self.shows:
                if s.player == player and card in s.cards:
                    s.remove_card(card)
                self.pop_show(s)
            # 2. Check if card is added to file.
            for c in self.cards:
                players_passing = set()
                for h in self.haves:
                    if h.card == c and (not h.yesno):
                        players_passing.add(h.player)
                if len(players_passing) == len(self.players):
                    self.cards_in_the_file.add(c)


    def record_show(self, player, cards):
        new_show = Show(player, cards)
        self.shows.append(new_show)

        player_passes = self.player_known_cards(player, False)
        player_known_cards = self.player_known_cards(player, True)
        for c in cards:
            if c in player_passes:
                new_show.remove_card(c)
            elif c in player_known_cards:
                new_show.is_void = True

        self.pop_show(new_show)

    def pop_show(self, show):
        if (not show.is_void) and (len(show.cards) == 1):
            show.is_void = True
            self.record_have(show.player, show.cards.pop(), True)

    # Return the known cards a player has, or does not have.
    def player_known_cards(self, player, yesno):
        cards = set()
        for h in self.haves:
            if h.player == player and h.yesno == yesno:
                cards.add(h.card)
        return cards

    def input_hand(self, cards):
        for c in cards:
            self.record_have(self.myself, c, True)

    def get_card(self, name):
        for c in self.cards:
            if c.name == name:
                return c
        raise ValueError("No such card! {}".format(name))

    def get_player(self, name):
        for p in self.players:
            if p.name == name:
                return p
        raise ValueError("No such player! {}".format(name))
