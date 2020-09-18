"""cluegame.py -- Classes to track Clue game events and make inferences

The board game Clue is also known as Cluedo.  This module contains classes that
make it possible to record specific knowledge-generating events that a Clue
player may observe during the course of a game (such as, for example, that
Player A showed Player B one of either Card X, Card Y, or Card Z).

More to the point, Clue is a game about building knowledge through logical
inference. As such, these classes are designed to track not only these events
themselves, but also the sum total of game knowledge that can be logically
inferred from them.

Classes:
    ClueCardType     -- an Enum of possible card types in the game
    ClueRelationType -- an Enum of possible types of Player-Card relation
    Player           -- a player in the Clue game
    Card             -- a card in the Clue game
    ClueRelation     -- an individual Player-Card relation that is known
    Game             -- a tracker and inference engine for total game knowledge
"""

from app.objectfilter import ObjectFilter
import enum
import pickle
import os
import collections


class ClueCardType(enum.Enum):
    """an Enum of possible card types in a Clue game"""
    PERSON = "Person"
    WEAPON = "Weapon"
    ROOM = "Room"


class ClueRelationType(enum.Enum):
    """an Enum of possible types of Player-Card relation to record in Clue

    These represent my own semi-invented terminology for describing a player's
    knowledge in a Clue game.  In case their meanings are not entirely
    self-evident, an explanation of these terms and how they relate to player
    knowledge in the game of Clue can be found the package README.md file; see
    esp. the "Theory" section.
    """
    HAVE = "have"
    PASS = "pass"
    SHOW = "show"


Player = collections.namedtuple('Player', 'name hand_size')
Player.__doc__ += ': A player in the Clue game'
Player.name.__doc__ = 'A name by which this player is identified'
Player.hand_size.__doc__ = 'Number of cards in hand of this player'

Card = collections.namedtuple('Card', 'name card_type')
Card.__doc__ += ': A card in the Clue game'
Card.name.__doc__ = 'A name by which this card is identified'
Card.card_type.__doc__ = 'Which ClueCardType this card belongs to'


class ClueRelation(collections.namedtuple(
        'ClueRelation', 'rel_type player cards')):
    """A generalized representation of a piece of Clue game knowledge to record

    A ClueRelation instance represents knowledge of a specific type of
    relationship between a given Player, and one or more given Cards.

    How many Cards are in a relation, depends on the relation's type:
        A HAVE or PASS relation has 1 card.
        A SHOW relation has 3 cards.

    Instance variables:
        rel_type -- a ClueRelationType, defining the type of this relation
        player   -- the Player who is involved in this relation
        cards    -- a list of the Card(s) involved in this relation

    The __contains__ method is signficiantly customized (perhaps "bastardized")
    to aid querying.
    """
    __slots__ = ()

    def __repr__(self):
        return "ClueRelation(Type={}, Player={}, Cards={})".format(
            self.rel_type, self.player, self.cards)

    def __contains__(self, obj):
        """Checks for any of several distinct conditions

        The inherited method is overridden, in a slight abuse, to check whether
        ANY of the following two conditions holds (logical "or"):
            - a given Player is self.player
            - a given Card is in self.cards
            - a given ClueCardType is represented among self.cards

        The last condition may seem strange, but I found it a useful trick to
        help keep the semantics consistently intuitive for certain queries that
        become relevant when making inferences in the game of Clue.  If I come
        up with a better way (i.e. a simple way to query lists of ClueRelations
        with intuitive-enough semantics that avoids the need for it), then I
        may consider removing this last condition, as it seems potentially
        confusing.
        """
        return obj == self.player \
            or obj in self.cards \
            or obj in [c.card_type for c in self.cards]


class ClueRelationFilter(ObjectFilter):
    """A tool to query a list of ClueRelations

    Public methods (besides inherited methods):
        match -- recursively tests aspects of a ClueRelation
    """
    def match(self, relation):
        """Recursively check if relation matches all filter statements.

        Arguments:
            relation -- the relation to check
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


class Game:
    """Encapsulates and updates the total state of the game knowledge.

    The Game instance knows the following:
        - a set of Cards (self.cards)
        - a set of Players (self.players)
        - all known ClueRelations between Players and Cards (self.relations)
        - which Cards are "in the file", meaning the Clue confidential file --
          this is how you win folks! (self.cards_in_the_file)

    The Game instance provides public methods to record new ClueRelations as
    they become known.

    These same public methods also recursively check for and record the
    consequences of any logical deductions that follow from each
    newly-discovered ClueRelation.

    There are also save/load/delete methods to handle persisting the game
    state.

    Public methods:
        record_have
        record_pass
        record_show
        save

    Class methods:
        load
        delete

    Instance variables:
        players
        cards
        cards_in_the_file
        relations
    """

    def __init__(self,
                 clue_cards_persons,
                 clue_cards_weapons,
                 clue_cards_rooms,
                 players):
        """Initializes the game state.

        Creates a set of Players and a set of Cards.  All other instance
        variables are initialized to empty.

        Arguments:
            clue_cards_persons -- a list of Person card names to play with
            clue_cards_weapons -- a list of Weapon card names to play with
            clue_cards_rooms -- a list of Room card names to play with
            players -- a list of tuples representing all Players in the Game
        """

        # Setup the Cards
        clue_cards = {
            ClueCardType.PERSON: clue_cards_persons,
            ClueCardType.WEAPON: clue_cards_weapons,
            ClueCardType.ROOM: clue_cards_rooms
        }
        self.cards = set()
        for t in ClueCardType:
            for c in clue_cards[t]:
                self.cards.add(Card(c, t))

        # Setup the Players
        self.players = set()
        for p in players:
            self.players.add(Player._make(p))

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

    def record_have(self, player, card):
        """Record a HAVE relation, and make deductions accordingly."""
        # Allow to pass arguments by object or by name
        player = self.__normalize_input_player_or_card(player, self.players)
        card = self.__normalize_input_player_or_card(card, self.cards)

        # Record the relation
        new_have = self.__generate_valid_have_pass(
            ClueRelationType.HAVE, player, card)
        if new_have:
            self.relations.append(new_have)

            # Make inferences
            self.__deduce_other_player_passes_from_have(player, card)
            self.__deduce_player_passes_from_known_whole_hand(player)
            self.__deduce_card_passes_from_cardtype_completion(card.card_type)

    def record_pass(self, player, card):
        """Record a PASS relation, and make deductions accordingly."""
        # Allow to pass arguments by object or by name
        player = self.__normalize_input_player_or_card(player, self.players)
        card = self.__normalize_input_player_or_card(card, self.cards)

        # Record the relation
        new_pass = self.__generate_valid_have_pass(
            ClueRelationType.PASS, player, card)
        if new_pass:
            self.relations.append(new_pass)

            # Make inferences
            matching_shows = (
                    ClueRelationFilter(player) +
                    ClueRelationFilter(card) +
                    ClueRelationFilter(ClueRelationType.SHOW)
                ).get(self.relations)
            for s in matching_shows:
                self.__deduce_have_from_show(s)

    def record_show(self, player, cards):
        """Record a SHOW relation, and make deductions accordingly."""
        # Allow to pass arguments by object or by name
        player = self.__normalize_input_player_or_card(player, self.players)
        my_cards = []
        for c in cards:
            my_cards.append(
                self.__normalize_input_player_or_card(c, self.cards))
        cards = my_cards

        # Record the relation
        new_show = self.__generate_valid_show(player, cards)
        if new_show:
            self.relations.append(new_show)

            # Make inferences
            self.__deduce_have_from_show(new_show)

    def __generate_valid_have_pass(self, rel_type, player, card):
        """Create a HAVE or PASS relation.

        First checks to make sure the HAVE or PASS is logically valid within
        the context of the current Game.  Then constructs and returns the
        ClueRelation.

        Arguments:
            rel_type -- ClueRelationType.HAVE or .PASS
            player   -- the Player who has (or not) the card
            card     -- the Card which is had (or not)
        Returns:
            a ClueRelation of type HAVE or PASS
        """
        # Catch any overlapping relations -- Don't record it!
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
                raise ValueError("Cannot mark Relation {} {} {}; ".format(
                                 rel_type, player, card) +
                                 "the opposite is already marked!")

        # Now record it!
        return ClueRelation(
            rel_type=rel_type,
            player=player,
            cards=[card])

    def __generate_valid_show(self, player, cards):
        """Create a SHOW relation.

        Arguments:
            player   -- the Player who showed the cards
            cards     -- the Card which were shown
        Returns:
            a ClueRelation of type SHOW
        """
        new_show = ClueRelation(
            rel_type=ClueRelationType.SHOW,
            player=player,
            cards=cards)
        return new_show

    def __deduce_other_player_passes_from_have(self, player, card):
        """If player has card, we infer all other players do not have card."""
        for other_p in self.players:
            if other_p != player:
                self.record_pass(other_p, card)

    def __deduce_player_passes_from_known_whole_hand(self, player):
        """If all player's cards are known, mark passes for all other cards."""
        known_cards_in_hand = [r.cards[0] for r in (
                ClueRelationFilter(player) +
                ClueRelationFilter(ClueRelationType.HAVE)
            ).get(self.relations)]

        if len(known_cards_in_hand) == player.hand_size:
            for other_c in self.cards:
                if other_c not in known_cards_in_hand:
                    self.record_pass(player, other_c)

    def __deduce_card_passes_from_cardtype_completion(self, cluecardtype):
        """If all cards but 1 of this type are accounted for, mark passes.

        If we know which player has every card of this type but 1, mark passes
        for all players for the remaining card.
        """
        cards_of_type_located = [r.cards[0] for r in (
                ClueRelationFilter(cluecardtype) +
                ClueRelationFilter(ClueRelationType.HAVE)
            ).get(self.relations)]

        cards_of_type_total = []
        for card_name in [c.name for c in
                          self.cards if c.card_type == cluecardtype]:
            cards_of_type_total.append(
                self.__normalize_input_player_or_card(card_name, self.cards))

        if len(cards_of_type_located) == len(cards_of_type_total) - 1:
            remaining_card = (
                    set(cards_of_type_total) -
                    set(cards_of_type_located)
                ).pop()
            for p in self.players:
                self.record_pass(p, remaining_card)

    def __deduce_have_from_show(self, show):
        """If given SHOW has 2 PASSed cards for player, infer & record a HAVE.

        If show.cards contains exactly 2 cards that show.player has PASSes
        recorded for, then infer and record a HAVE for show.player and the 3rd
        card.
        """
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
                    self.record_have(show.player, c)

    def __normalize_input_player_or_card(self, obj, lst):
        """Returns a matching member of a Player or Card list, if possible.

        Arguments:
            obj -- a Player, Card, or a name (string)
            lst -- a list of Players or Cards

        Returns:
            a Player or Card from the list, matching obj
        """
        if obj in lst:
            return obj
        else:
            my_obj = next(o for o in lst if o.name == obj)
            if my_obj == StopIteration:
                raise ValueError("No such player or card! {}".format(obj))
            else:
                return my_obj

    def save(self, path):
        """Persists the Game state to a file.

        BEWARE: Overwrites any existing file at 'path'.
        """
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
        """Deletes a persisted Game state in a file.

        BEWARE: Deletes any existing file at 'path'.
        """
        os.remove(path)


Game.load = classmethod(Game.load)
Game.delete = classmethod(Game.delete)
