import enum
import pickle
import os
import collections


class ClueCardType(enum.Enum):
    PERSON = "Person"
    WEAPON = "Weapon"
    ROOM = "Room"


Player = collections.namedtuple('Player', 'name hand_size')
Player.__doc__ += ': A player in the Clue game'
Player.name.__doc__ = 'A name by which this player is identified'
Player.hand_size.__doc__ = 'Number of cards in hand of this player'

Card = collections.namedtuple('Card', 'name card_type')
Card.__doc__ += ': A card in the Clue game'
Card.name.__doc__ = 'A name by which this card is identified'
Card.card_type.__doc__ = 'Which ClueCardType this card belongs to'


class ClueRelationType(enum.Enum):
    HAVE = "have"
    PASS = "pass"
    SHOW = "show"


class ClueRelation(collections.namedtuple(
        'ClueRelation', 'rel_type player cards')):
    __slots__ = ()

    def __repr__(self):
        return "ClueRelation(Type={}, Player={}, Cards={})".format(
            self.rel_type, self.player, self.cards)

    def __contains__(self, obj):
        return obj == self.player \
            or obj in self.cards \
            or obj in [c.card_type for c in self.cards]


ClueRelation.__doc__ = \
    'A relation between a Player and one or more Cards.'
ClueRelation.rel_type.__doc__ = \
    'Which ClueRelationType this relation belongs to'
ClueRelation.player.__doc__ = \
    'The Player that this relation pertains to'
ClueRelation.cards.__doc__ = \
    'The list of Cards (possible singleton) that this relation pertains to'


class Game:
    """Encapsulates and updates the total state of the game knowledge.

    The Game instance knows the following:
        - a set of Cards (self.cards)
        - a set of Players (self.players)
        - which Player represents the user (self.myself)
        - all known ClueRelations between Players and Cards (self.relations)
        - which Cards are "in the file", meaning the Clue confidential file --
          this is how you win folks! (self.cards_in_the_file)

    The Game instance provides methods to record new ClueRelations as they
    become known.  These methods also recursively check for and record the
    consequences of any deductions that follow from each newly-discovered
    relation.

    There are also lightweight methods to query the above state, and
    save/load/delete methods to handle persisting the game state.  (For more
    powerful querying of ClueRelations, see the ClueRelationFilter class.)

    Public methods:
        record_have_pass
        record_show
        input_hand
        get_card
        get_player
        save

    Class methods:
        load
        delete

    Instance variables:
        myself
        other_players
        players
        cards
        cards_in_the_file
        relations
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
        self.relations = []

    @property
    def cards_in_the_file(self):
        """If we know that no player has a given card, it is in the file!"""
        cards_in_the_file = set()
        for c in self.cards:
            players_passing = [r.player for r in (
                    ClueRelationFilter(c) +
                    ClueRelationFilter(ClueRelationType.PASS)
                ).get(self.relations)]
            if len(players_passing) == len(self.players):
                cards_in_the_file.add(c)
        return cards_in_the_file

    def record_have_pass(self, rel_type, player, card):
        """Record a HAVE or PASS relation, and make deductions accordingly.

        Arguments:
            rel_type -- ClueRelationType.HAVE or .PASS
            player   -- the Player who has (or not) the card
            card     -- the Card which is had (or not)
        """
        matching_haves_passes = (
                ClueRelationFilter(player) +
                ClueRelationFilter(card) +
                (
                    ClueRelationFilter(ClueRelationType.HAVE) /
                    ClueRelationFilter(ClueRelationType.PASS)
                )
            ).get(self.relations)

        for h in matching_haves_passes:
            if h.rel_type == rel_type:
                return  # Ignore attempted duplicate record.
            else:
                raise ValueError("Cannot mark Relation; " +
                                 "the opposite is already marked!")

        # Now record it!
        self.relations.append(ClueRelation(
            rel_type=rel_type,
            player=player,
            cards=[card]))

        # Finally, make and record any deductions.
        if rel_type == ClueRelationType.HAVE:
            for other_p in self.players:
                if other_p != player:
                    self.record_have_pass(
                        rel_type=ClueRelationType.PASS,
                        player=other_p,
                        card=card)
            self.__deduce_player_passes_from_known_whole_hand(player)
            self.__deduce_card_passes_from_cardtype_completion(card.card_type)

        else:
            matching_shows = (
                    ClueRelationFilter(player) +
                    ClueRelationFilter(card) +
                    ClueRelationFilter(ClueRelationType.SHOW)
                ).get(self.relations)
            for s in matching_shows:
                self.__pop_show(s)

    def record_show(self, player, cards):
        """Record a SHOW relation, and make deductions accordingly.

        Arguments:
            player -- the player for the Show; see Show class
            cards  -- the cards for the Show; see Show class
        """
        new_show = ClueRelation(
            rel_type=ClueRelationType.SHOW,
            player=player,
            cards=cards)
        self.relations.append(new_show)
        self.__pop_show(new_show)

    def __deduce_player_passes_from_known_whole_hand(self, player):
        """If all player's cards are known, mark passes for all other cards."""
        player_haves = (
                ClueRelationFilter(player) +
                ClueRelationFilter(ClueRelationType.HAVE)
            ).get(self.relations)

        if len(player_haves) == player.hand_size:
            for other_c in self.cards:
                if other_c not in [r.cards[0] for r in player_haves]:
                    self.record_have_pass(
                        rel_type=ClueRelationType.PASS,
                        player=player,
                        card=other_c)

    def __deduce_card_passes_from_cardtype_completion(self, cluecardtype):
        """If all cards but 1 of this type are accounted for, mark passes.

        If we know which player has every card of this type but 1, mark passes
        for all players for the remaining card.
        """
        cards_of_type_located = (
                ClueRelationFilter(cluecardtype) +
                ClueRelationFilter(ClueRelationType.HAVE)
            ).get(self.relations)

        cards_of_type_total = []
        for card_name in self.clue_cards[cluecardtype]:
            cards_of_type_total.append(self.get_card(card_name))

        if len(cards_of_type_located) == len(cards_of_type_total) - 1:
            remaining_card = (
                    set(cards_of_type_total) -
                    set(cards_of_type_located)
                ).pop()
            for p in self.players:
                self.record_have_pass(
                    rel_type=ClueRelationType.PASS,
                    player=p,
                    card=remaining_card)

    def __pop_show(self, show):
        """If show has 2 passed cards and none had, deduce & record a Have."""
        q = ClueRelationFilter()
        for c in show.cards:
            q = q / ClueRelationFilter(c)
        q = q + ClueRelationFilter(show.player)

        if len((q + ClueRelationFilter(ClueRelationType.HAVE)
                ).get(self.relations)) == 0:
            passed_cards = [r.cards[0] for r in
                            (q + ClueRelationFilter(ClueRelationType.PASS)
                             ).get(self.relations)]
            unpassed_cards = set(show.cards) - set(passed_cards)
            if len(unpassed_cards) == 1:
                for c in unpassed_cards:
                    self.record_have_pass(
                        rel_type=ClueRelationType.HAVE,
                        player=show.player,
                        card=c)

    def input_hand(self, cards):
        """Records 3 Cards as belonging to the self.myself Player."""
        for c in cards:
            self.record_have_pass(
                rel_type=ClueRelationType.HAVE,
                player=self.myself,
                card=c)

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
        elif self.statement in ClueRelationType:
            return relation.rel_type == self.statement
        else:
            return self.statement in relation

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

    def __add__(self, other):
        """Combine with another filter to create a compound "and" filter."""
        new = ClueRelationFilter("and")
        new.left = self
        new.right = other
        return new

    def __truediv__(self, other):
        """Combine with another filter to create a compound "or" filter."""
        new = ClueRelationFilter("or")
        new.left = self
        new.right = other
        return new

    def __neg__(self):
        """Invert filter, creating a compound "not" filter."""
        new = ClueRelationFilter("not")
        new.left = self
        new.right = None
        return new

    def get(self, relations_list):
        """Return all from relations_list that match all filter statements."""
        matching_relations = []
        for r in relations_list:
            if self.match(r):
                matching_relations.append(r)
        return matching_relations
