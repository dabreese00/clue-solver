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
