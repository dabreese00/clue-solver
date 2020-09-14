from app.cluegame import (ClueCardType, Card, Player, ClueRelationFilter,
                          ClueRelationType, ClueRelation)

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

    filter1 = ClueRelationFilter(get_obj(players, "Cynthia"))
    filter2 = filter1.compound("and", ClueRelationFilter(
        get_obj(cards, "Billiard Room")))
    filter3 = filter2.compound("and", ClueRelationFilter(
        get_obj(cards, "Rope")))

    filter4 = filter1.compound("or", ClueRelationFilter(
        get_obj(cards, "Billiard Room")))

    filter5 = filter1.compound("not")

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


def test_operator_syntax():

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

    filter1 = ClueRelationFilter(get_obj(players, "Cynthia"))
    filter2 = filter1 + ClueRelationFilter(get_obj(cards, "Billiard Room"))
    filter3 = filter2 + ClueRelationFilter(get_obj(cards, "Rope"))

    filter4 = filter1 / ClueRelationFilter(get_obj(cards, "Billiard Room"))

    filter5 = -filter1

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
