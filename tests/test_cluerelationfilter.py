from app.cluegame import (ClueCardType, Card, Player, Have, Show,
                          ClueRelationFilter)

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
        "Library",
        "Study"
    }
}


def get_obj(obj_list, name):
    for o in obj_list:
        if o.name == name:
            return o


def test_one():

    hand_size = 3
    player_names = {'Adam', 'Cynthia', 'Greg', 'David'}
    players = set()
    for p in player_names:
        players.add(Player(p, hand_size))

    cards = set()
    for t in ClueCardType:
        for c in clue_cards[t]:
            cards.add(Card(c, t))

    haves = []
    haves.append(Have(
        get_obj(players, "Cynthia"),
        get_obj(cards, "Billiard Room"),
        True))
    haves.append(Have(
        get_obj(players, "David"),
        get_obj(cards, "Billiard Room"),
        False))
    haves.append(Have(
        get_obj(players, "Cynthia"),
        get_obj(cards, "Rope"),
        True))
    haves.append(Have(
        get_obj(players, "Cynthia"),
        get_obj(cards, "Study"),
        False))

    shows = []
    shows.append(Show(
        get_obj(players, "Cynthia"),
        [
            get_obj(cards, "Billiard Room"),
            get_obj(cards, "Rope"),
            get_obj(cards, "Study")
        ]))
    shows.append(Show(
        get_obj(players, "David"),
        [
            get_obj(cards, "Mrs. White"),
            get_obj(cards, "Rope"),
            get_obj(cards, "Study")
        ]))
    shows.append(Show(
        get_obj(players, "Adam"),
        [
            get_obj(cards, "Billiard Room"),
            get_obj(cards, "Rope"),
            get_obj(cards, "Study")
        ]))

    filter1 = ClueRelationFilter(get_obj(players, "Cynthia"))
    filter2 = filter1.add("and", ClueRelationFilter(
        get_obj(cards, "Billiard Room")))
    filter3 = filter2.add("and", ClueRelationFilter(
        get_obj(cards, "Rope")))

    filter4 = filter1.add("or", ClueRelationFilter(
        get_obj(cards, "Billiard Room")))

    filter5 = filter1.add("not")

    assert len(filter1.get(haves)) == 3
    assert len(filter2.get(haves)) == 1
    assert len(filter3.get(haves)) == 0
    assert len(filter4.get(haves)) == 4
    assert len(filter5.get(haves)) == 1
    assert len(filter1.get(shows)) == 1
    assert len(filter2.get(shows)) == 1
    assert len(filter3.get(shows)) == 1
    assert len(filter4.get(shows)) == 2
    assert len(filter5.get(shows)) == 2
