from app.cluegame import CluePersonCard, ClueWeaponCard, ClueRoomCard, CluePlayer, ClueGame
import pytest

def test_one():
    with pytest.raises(ValueError):
        david = CluePlayer("David", 3)
        adam = CluePlayer("Adam", 3)
        players = [david, adam]

        game = ClueGame(players)

def test_two():
    players = []
    for n in ['a', 'b', 'c', 'd', 'e', 'f']:
        players.append(CluePlayer(n, 3))

    game = ClueGame(players)
    assert game.players == players

def test_three():
    players = []
    for n in ['a', 'b', 'c', 'd', 'e', 'f']:
        players.append(CluePlayer(n, 3))

    game = ClueGame(players)

    msg = game.record_show('a', CluePersonCard.COLONEL_MUSTARD, 
            ClueWeaponCard.ROPE, ClueRoomCard.BILLIARD_ROOM)

    assert msg == "Player a has shown"
