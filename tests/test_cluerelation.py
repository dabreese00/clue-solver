import pytest
from app.cluegame import (ClueCardType, ClueRelationType, Card, Player,
                          ClueRelation)


@pytest.fixture
def one_player():
    return Player("David", 3)


@pytest.fixture
def one_room_card():
    return Card("Ballroom", ClueCardType.ROOM)


@pytest.fixture
def one_person_card():
    return Card("Ms. Scarlet", ClueCardType.PERSON)


@pytest.fixture
def one_weapon_card():
    return Card("Rope", ClueCardType.WEAPON)


@pytest.fixture
def one_card(one_room_card):
    return one_room_card


@pytest.fixture
def three_cards_diff_types(one_room_card, one_person_card, one_weapon_card):
    return [one_room_card, one_person_card, one_weapon_card]


def test_signature(one_player, one_card):
    p = one_player
    c = one_card

    for t in list(ClueRelationType):

        r = ClueRelation(t, p, [c])

        assert r.rel_type == t
        assert r.player == p
        assert c in r.cards
        assert len(r.cards) == 1


def test_have_contains(one_player, three_cards_diff_types):
    p = one_player
    t = ClueRelationType.HAVE

    for c in three_cards_diff_types:
        r = ClueRelation(t, p, [c])

        assert p in r
        assert c in r
        assert c.card_type in r


def test_show_contains(one_player, three_cards_diff_types):
    p = one_player
    cs = three_cards_diff_types
    t = ClueRelationType.SHOW

    r = ClueRelation(t, p, cs)

    assert p in r
    for c in cs:
        assert c in r
        assert c.card_type in r
