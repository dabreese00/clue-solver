import enum
import pickle
import os


class ClueCardType(enum.Enum):
    PERSON = "Person"
    WEAPON = "Weapon"
    ROOM = "Room"


class Player:
    """Represents a player in the Clue game.

    Instance variables:
        name: the player's name in real life
        hand_size: how many cards the player is holding
    """
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
        return "Player(Name={}, Hand size={})".format(
                self.name, self.hand_size)


class Card:
    """Represents a card in the Clue game.

    Instance variables:
        name: the card's name
        type: which type of clue card it is (see enum ClueCardType)
    """
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
    """Records a given player's having, or not having, of a given card.

    Public methods:
        overlaps: check whether two Haves's subjects are the same

    Instance variables:
        player: the player who is known to have, or not have, the card
        card:   the card which is known to be had, or not had
        yesno:  True means the player has it; false, the opposite
    """
    def __init__(self, player, card, yesno):
        self.player = player
        self.card = card
        self.yesno = yesno

    def overlaps(self, other):
        if type(other) is type(self):
            return self.player == other.player and self.card == other.card
        else:
            return NotImplemented

    def __repr__(self):
        return "Have(Player={}, Card={}, {})".format(
                self.player, self.card, self.yesno)

    def __contains__(self, obj):
        return obj == self.player \
            or obj == self.card \
            or obj == self.card.card_type


# A 4-way relationship between a player and 3 cards.
# Created when a player shows a card to someone else.
class Show:
    """Records that a given player showed one of several given cards.

    Public methods:
        remove_card: narrows down the Show by removing one of the possibilities

    Instance variables:
        player:  the player who showed one of the cards
        cards:   the list of cards of which one was shown
        is_void: marked True if this Show's info can no longer be used
    """
    def __init__(self, player, cards):
        self.player = player
        self.cards = cards.copy()  # Shallow copy, avoid mutating input set
        self.is_void = False

    def remove_card(self, card):
        self.cards.remove(card)

    def __repr__(self):
        return "Show(Player={}, Cards={}, Void={})".format(
                self.player, self.cards, self.is_void)

    def __contains__(self, obj):
        if self.is_void:
            return False
        return obj == self.player \
            or obj in self.cards


class Game:
    """Encapsulates and updates the total state of the game knowledge.

    The Game instance knows the following:
        - a set of Cards (self.cards)
        - a set of Players (self.players)
        - which Player represents the user (self.myself)

    The Game instance also keeps track of all known relationships between the
    Players and the Cards -- in the form of Haves, and Shows.  (See README.md
    for a more detailed explanation of how this models a Clue game.)

    Game provides methods to record Haves and Shows as they become known, which
    also recursively check for and record the consequences of any deductions
    that follow from each newly-discovered relationship.

    And the Game instance keeps track of which Cards are "in the file", meaning
    the Clue confidential file -- this is how you win folks!

    There are also methods to query the above state (which are also used
    internally by the recording methods to make deductions), and
    save/load/delete methods to handle persisting the game state.

    Public methods:
        record_have
        record_show
        pop_show
        player_known_cards
        input_hand
        get_card
        get_player
        save
        load
        delete

    Instance variables:
        myself
        other_players
        players
        cards
        cards_in_the_file
        haves
        shows
    """

    clue_cards = {
        ClueCardType.PERSON: {
            "Colonel Mustard",
            "Miss Scarlet",
            "Professor Plum",
            "Mrs. White",
            "Mr. Green",
            "Mrs. Peacock"
        },
        ClueCardType.WEAPON: {
            "Rope",
            "Lead Pipe",
            "Revolver",
            "Candlestick",
            "Knife",
            "Wrench"
        },
        ClueCardType.ROOM: {
            "Billiard Room",
            "Ballroom",
            "Lounge",
            "Kitchen",
            "Conservatory",
            "Library"
        }
    }

    def __init__(self, myself, other_players):
        """Initializes the game state.

        Creates a set of Players and a set of Cards, including which Player is
        the user.  All other instance variables are initialized to empty.

        Note: Even though the contents of the user's own hand would typically
        be already known at game start, too, this set of Player-Card
        relationships is currently recorded separately, after game
        initialization, using the input_hand method.

        Arguments:
            myself -- a Player representing the user
            other_players -- a list of all other Players in the Game
        """

        # Setup the Cards
        self.cards = set()
        for t in ClueCardType:
            for c in self.clue_cards[t]:
                self.cards.add(Card(c, t))

        # Setup the Players
        self.myself = myself
        self.other_players = other_players
        self.players = other_players.copy()
        self.players.add(myself)

        for p in self.players:
            for c in self.cards:
                if p.name == c.name:
                    raise ValueError(
                        "Forbidden Player name: {}".format(p.name))

        # Setup the Game state knowledge
        self.haves = []
        self.shows = []
        self.cards_in_the_file = set()

    def record_have(self, player, card, yesno):
        """Record a Have relationship; make and record any related deductions.

        Arguments:
            player -- the player for the Have; see Have class
            card   -- the card for the Have; see Have class
            yesno  -- the True/False of the Have; see Have class
        """

        prospective_have = Have(player, card, yesno)

        # Catch any overlap with existing haves -- Don't record it!
        for h in self.haves:
            if h.overlaps(prospective_have):
                if h.yesno == prospective_have.yesno:
                    return  # Assume this has all been done already; move on.
                else:
                    raise ValueError("Cannot mark Have for " +
                                     "{} and {} as {}; ".format(
                                                    player, card, yesno) +
                                     "the opposite is already marked!")

        # Now record it!
        self.haves.append(prospective_have)

        # Additional triggered actions
        if yesno:  # we know player has card

            # 1. Mark passes for all other players
            for other_p in self.players:
                if other_p != player:
                    self.record_have(other_p, card, False)

            # 2. If all the player's cards are accounted for, mark passes for
            # all other cards.
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
                remaining_card = (
                        cards_of_type_total - cards_of_type_located).pop()
                for p in self.players:
                    self.record_have(p, remaining_card, False)

            # 4. If the player has this card in any of their "shows", void
            # those shows.
            for s in self.shows:
                if s.player == player and card in s.cards:
                    s.is_void = True

        else:  # we know player does not have card
            # 1. If the passing player & card are in any Shows together, try to
            # "pop" them.
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
        """Record a Show relationship; make and record any related deductions.

        Arguments:
            player -- the player for the Show; see Show class
            cards  -- the cards for the Show; see Show class
        """
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

    def player_known_cards(self, player, yesno):
        """Returns the known Cards a Player has, or does not have."""
        cards = set()
        for h in self.haves:
            if h.player == player and h.yesno == yesno:
                cards.add(h.card)
        return cards

    def input_hand(self, cards):
        """Records 3 Cards as belonging to the self.myself Player."""
        for c in cards:
            self.record_have(self.myself, c, True)

        for c in self.cards:
            if c not in cards:
                self.record_have(self.myself, c, False)

    def get_card(self, name):
        """Returns a Card object from the Game's list, by name."""
        for c in self.cards:
            if c.name == name:
                return c
        raise ValueError("No such card! {}".format(name))

    def get_player(self, name):
        """Returns a Player object from the Game's list, by name."""
        for p in self.players:
            if p.name == name:
                return p
        raise ValueError("No such player! {}".format(name))

    def save(self, path):
        """Persists the Game state to a file."""
        with open(path, 'wb') as dbfile:
            pickle.dump(self, dbfile)

    def load(obj, path):
        """Loads a persisted Game state from a file."""
        if os.path.isfile(path):
            with open(path, 'rb') as dbfile:
                return pickle.load(dbfile)
        else:
            return None

    def delete(obj, path):
        """Deletes a persisted Game state (or any file, really; be careful)."""
        os.remove(path)


Game.load = classmethod(Game.load)
Game.delete = classmethod(Game.delete)


# TODO: Make this class immutable?
class ClueRelationFilter:
    """Represents a filter to match Clue relations.

    Public methods:
        match      -- check a single relation against the filter
        add        -- add a filter condition to the query using "and"
        get        -- query a list and return results based on the filter
    """
    def __init__(self, statement="all"):
        self.left = None
        self.right = None
        self.statement = statement

    def match(self, relation):
        """Recursively check if statement(s) are in relation."""
        if self.statement == "and":
            return self.left.match(relation) and self.right.match(relation)
        elif self.statement == "or":
            return self.left.match(relation) or self.right.match(relation)
        elif self.statement == "all":
            return True
        elif self.statement == "have":
            return relation.yesno
        elif self.statement == "pass":
            return not relation.yesno
        else:
            return self.statement in relation

    def add(self, op="and", statement=None):
        new = ClueRelationFilter(op)
        new.left = self
        new.right = ClueRelationFilter(statement)
        return new

    def get(self, relations_list):
        matching_relations = []
        for r in relations_list:
            if self.match(r):
                matching_relations.append(r)
        return matching_relations
