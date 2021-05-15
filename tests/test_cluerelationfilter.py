from app.cluegame import (ClueCardType, Card, Player, ClueRelationFilter,
                          ClueRelationType, ClueRelation)
import pytest


@pytest.fixture
def clue_card_set():
    card_dict = {
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
            "Library",
            "Study"
        }
    }

    cards = set()
    for t in ClueCardType:
        for c in card_dict[t]:
            cards.add(Card(c, t))

    return cards


@pytest.fixture
def get_obj():
    def f(obj_list, name):
        for o in obj_list:
            if o.name == name:
                return o
    return f


@pytest.fixture
def four_players():
    player_names = {'Adam', 'Cynthia', 'Greg', 'David'}
    hand_size = 3

    players = set()
    for p in player_names:
        players.add(Player(p, hand_size))

    return players


@pytest.fixture
def four_haves_passes(four_players, clue_card_set, get_obj):
    players = four_players
    cards = clue_card_set

    haves = []
    haves.append(ClueRelation(
        rel_type=ClueRelationType.HAVE,
        player=get_obj(players, "Cynthia"),
        cards=[get_obj(cards, "Billiard Room")]))
    haves.append(ClueRelation(
        rel_type=ClueRelationType.PASS,
        player=get_obj(players, "David"),
        cards=[get_obj(cards, "Billiard Room")]))
    haves.append(ClueRelation(
        rel_type=ClueRelationType.HAVE,
        player=get_obj(players, "Cynthia"),
        cards=[get_obj(cards, "Rope")]))
    haves.append(ClueRelation(
        rel_type=ClueRelationType.PASS,
        player=get_obj(players, "Cynthia"),
        cards=[get_obj(cards, "Study")]))

    return haves


@pytest.fixture
def three_shows(four_players, clue_card_set, get_obj):
    players = four_players
    cards = clue_card_set

    shows = []
    shows.append(ClueRelation(
        rel_type=ClueRelationType.SHOW,
        player=get_obj(players, "Cynthia"),
        cards=[
            get_obj(cards, "Billiard Room"),
            get_obj(cards, "Rope"),
            get_obj(cards, "Study")
        ]))
    shows.append(ClueRelation(
        rel_type=ClueRelationType.SHOW,
        player=get_obj(players, "David"),
        cards=[
            get_obj(cards, "Mrs. White"),
            get_obj(cards, "Rope"),
            get_obj(cards, "Study")
        ]))
    shows.append(ClueRelation(
        rel_type=ClueRelationType.SHOW,
        player=get_obj(players, "Adam"),
        cards=[
            get_obj(cards, "Billiard Room"),
            get_obj(cards, "Rope"),
            get_obj(cards, "Study")
        ]))

    return shows


def test_one(clue_card_set, get_obj, four_players, four_haves_passes,
             three_shows):

    players = four_players
    cards = clue_card_set
    haves = four_haves_passes
    shows = three_shows

    filter1 = ClueRelationFilter(get_obj(players, "Cynthia"))

    assert len(filter1.get(haves)) == 3
    assert len(filter1.get(shows)) == 1

    filter2 = filter1.compound("and", ClueRelationFilter(
        get_obj(cards, "Billiard Room")))

    assert len(filter2.get(haves)) == 1
    assert len(filter2.get(shows)) == 1

    filter3 = filter2.compound("and", ClueRelationFilter(
        get_obj(cards, "Rope")))

    assert len(filter3.get(haves)) == 0
    assert len(filter3.get(shows)) == 1

    filter4 = filter1.compound("or", ClueRelationFilter(
        get_obj(cards, "Billiard Room")))

    assert len(filter4.get(haves)) == 4
    assert len(filter4.get(shows)) == 2

    filter5 = filter1.compound("not")

    assert len(filter5.get(haves)) == 1
    assert len(filter5.get(shows)) == 2


def test_operator_syntax(clue_card_set, get_obj, four_players,
                         four_haves_passes, three_shows):

    players = four_players
    cards = clue_card_set
    haves = four_haves_passes
    shows = three_shows

    filter1 = ClueRelationFilter(get_obj(players, "Cynthia"))

    assert len(filter1.get(haves)) == 3
    assert len(filter1.get(shows)) == 1

    filter2 = filter1 + ClueRelationFilter(get_obj(cards, "Billiard Room"))

    assert len(filter2.get(haves)) == 1
    assert len(filter2.get(shows)) == 1

    filter3 = filter2 + ClueRelationFilter(get_obj(cards, "Rope"))

    assert len(filter3.get(haves)) == 0
    assert len(filter3.get(shows)) == 1

    filter4 = filter1 / ClueRelationFilter(get_obj(cards, "Billiard Room"))

    assert len(filter4.get(haves)) == 4
    assert len(filter4.get(shows)) == 2

    filter5 = -filter1

    assert len(filter5.get(haves)) == 1
    assert len(filter5.get(shows)) == 2
