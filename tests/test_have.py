from app.cluegame import ClueCardType, Card, Player, Have


def test_simple_have_init():
    c = Card('Professor Plum', ClueCardType.PERSON)
    p = Player('David', hand_size=3)
    h1 = Have(p, c, True)
    h2 = Have(p, c, False)

    assert h1.player.name == 'David'
    assert h1.card.card_type == ClueCardType.PERSON
    assert h1 != h2
    assert h1.yesno
    assert not h2.yesno


def test_have_overlaps():
    c = Card('Professor Plum', ClueCardType.PERSON)
    p = Player('David', hand_size=3)
    q = Player('George', hand_size=4)
    r = Player('David', hand_size=3)
    s = Player('David', hand_size=4)
    h1 = Have(p, c, True)
    h2 = Have(p, c, False)
    h3 = Have(q, c, True)
    h4 = Have(r, c, True)
    h5 = Have(s, c, True)

    assert h1.overlaps(h2)
    assert not h1.overlaps(h3)
    assert h1.overlaps(h4)
    assert h1.overlaps(h5)
