import enum
import pickle
import os
import collections


class ClueCardType(enum.Enum):
    PERSON = "Person"
    WEAPON = "Weapon"
    ROOM = "Room"


Player = collections.namedtuple('Player', 'name hand_size')
Card = collections.namedtuple('Card', 'name card_type')


class ClueRelationType(enum.Enum):
    HAVE = "have"
    PASS = "pass"
    SHOW = "show"


class Have:
    """Records a given player's having, or not having, of a given card.

    Instance variables:
        player: the player who is known to have, or not have, the card
        card:   the card which is known to be had, or not had
        yesno:  True means the player has it; false, the opposite
    """
    def __init__(self, player, card, yesno):
        self.player = player
        self.card = card
        self.yesno = yesno

    def __repr__(self):
        return "Have(Player={}, Card={}, {})".format(
                self.player, self.card, self.yesno)

    def __contains__(self, obj):
        return obj == self.player \
            or obj == self.card \
            or obj == self.card.card_type


class Show:
    """Records that a given player showed one of several given cards.

    Instance variables:
        player:  the player who showed one of the cards
        cards:   the list of cards of which one was shown
    """
    def __init__(self, player, cards):
        self.player = player
        if len(set(cards)) != len(cards):
            raise ValueError("A Show cannot contain duplicate cards!")
        self.cards = cards.copy()  # Shallow copy, avoid mutating input set

    def __repr__(self):
        return "Show(Player={}, Cards={})".format(
                self.player, self.cards)

    def __contains__(self, obj):
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

        # Catch any overlap with existing haves -- Don't record it!
        matching_haves = ClueRelationFilter(player).add(
            "and", ClueRelationFilter(card)).get(self.haves)

        for h in matching_haves:
            if h.yesno == yesno:
                return  # Ignore attempted duplicate record.
            else:
                raise ValueError("Cannot mark Have for " +
                                 "{} and {} as {}; ".format(
                                                player, card, yesno) +
                                 "the opposite is already marked!")

        # Now record it!
        self.haves.append(Have(player, card, yesno))

        # Finally, make and record any deductions.
        if yesno:
            for other_p in self.players:
                if other_p != player:
                    self.record_have(other_p, card, False)
            self.__deduce_player_passes_from_known_whole_hand(player)
            self.__deduce_card_passes_from_cardtype_completion(card.card_type)

        else:
            matching_shows = ClueRelationFilter(player).add(
                "and", ClueRelationFilter(card)).get(self.shows)
            for s in matching_shows:
                self.__pop_show(s)
            self.__deduce_cards_in_file_from_passes()

    def record_show(self, player, cards):
        """Record a Show relationship; make and record any related deductions.

        Arguments:
            player -- the player for the Show; see Show class
            cards  -- the cards for the Show; see Show class
        """
        new_show = Show(player, cards)
        self.shows.append(new_show)
        self.__pop_show(new_show)

    def __deduce_player_passes_from_known_whole_hand(self, player):
        """If all player's cards are known, mark passes for all other cards."""
        player_haves = ClueRelationFilter(player).add(
                "and", ClueRelationFilter(ClueRelationType.HAVE)).get(
                    self.haves)

        if len(player_haves) == player.hand_size:
            for other_c in self.cards:
                if other_c not in [h.card for h in player_haves]:
                    self.record_have(player, other_c, False)

    def __deduce_card_passes_from_cardtype_completion(self, cluecardtype):
        """If all cards but 1 of this type are accounted for, mark passes.

        If we know which player has every card of this type but 1, mark passes
        for all players for the remaining card.
        """
        cards_of_type_located = set(ClueRelationFilter(
            cluecardtype).get(self.haves))
        cards_of_type_total = set()
        for card_name in self.clue_cards[cluecardtype]:
            cards_of_type_total.add(self.get_card(card_name))
        if len(cards_of_type_located) == len(cards_of_type_total) - 1:
            remaining_card = (
                    cards_of_type_total - cards_of_type_located).pop()
            for p in self.players:
                self.record_have(p, remaining_card, False)

    def __deduce_cards_in_file_from_passes(self):
        """If all players have passed for a card, add it to the file!"""
        for c in self.cards:
            players_passing = ClueRelationFilter(c).add(
                "and", ClueRelationFilter(ClueRelationType.PASS)).get(
                    self.haves)
            if len(players_passing) == len(self.players):
                self.cards_in_the_file.add(c)

    def __pop_show(self, show):
        """If show has 2 passed cards and none had, deduce & record a Have."""
        q = ClueRelationFilter()
        for c in show.cards:
            q = q.add("or", ClueRelationFilter(c))
        q = q.add("and", ClueRelationFilter(show.player))

        if len(q.add("and", ClueRelationFilter(ClueRelationType.HAVE)).get(
                self.haves)) == 0:
            passed_cards = [h.card for h in
                            q.add("and", ClueRelationFilter(
                                ClueRelationType.PASS)).get(self.haves)]
            unpassed_cards = set(show.cards) - set(passed_cards)
            if len(unpassed_cards) == 1:
                for c in unpassed_cards:
                    self.record_have(show.player, c, True)

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

    The filter can be used to search for Clue relations who have members listed
    in the filter statement, and/or who match the filter statement magic string
    meaning (see below).

    The filter is represented as a binary tree structure; this allows building
    compound filters by joining independent filters using a logical operator.

    Meanings of magic string values for `statement`:
        and, or, not -- child filters combined using a logical operator
        all          -- no filter; query will return all elements
        have         -- matches only True Haves
        pass         -- matches only False Haves a.k.a. passes

    Public methods:
        match      -- check a single relation against the filter
        add        -- add a filter condition to the query using "and"
        get        -- query a list and return results based on the filter

    Instance variables:
        left       -- left child filter
        right      -- right child filter
        statement  -- this node's filter component
    """
    def __init__(self, statement=None):
        """Initialize a filter.

        Arguments:
            statement -- a relationship member, or a magic string
                (see class docstring above)
        """
        self.left = None
        self.right = None
        self.statement = statement

    def match(self, relation):
        """Recursively check if relation matches all filter statements.

        Arguments:
            statement -- a relationship member, or a magic string
                (see ClueRelationFilter class docstring above)
        """
        if self.statement == "and":
            return self.left.match(relation) and self.right.match(relation)
        elif self.statement == "or":
            return self.left.match(relation) or self.right.match(relation)
        elif self.statement == "not":
            return not self.left.match(relation)
        elif self.statement == "all":
            return True
        elif self.statement == ClueRelationType.HAVE:
            return relation.yesno
        elif self.statement == ClueRelationType.PASS:
            return not relation.yesno
        elif self.statement == ClueRelationType.SHOW:
            return len(relation.cards) > 1
        else:
            return self.statement in relation

    # TODO: How can this interface be made more simple and Pythonic to use?
    def add(self, op="and", other_filter=None):
        """Combine with another filter to create a compound filter.

        Arguments:
            op           -- logical operator to combine
            other_filter
        """
        if op in ["and", "or", "not"]:
            new = ClueRelationFilter(op)
            new.left = self
            new.right = other_filter
            return new
        else:
            raise ValueError("Specified op was {}; ".format(op) +
                             "expected 'and', 'or', or 'not'")

    def get(self, relations_list):
        """Return all from relations_list that match all filter statements."""
        matching_relations = []
        for r in relations_list:
            if self.match(r):
                matching_relations.append(r)
        return matching_relations
