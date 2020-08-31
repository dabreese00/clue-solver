from app.cluegame import ClueCardType, Card, Player, Have, Show, Game
import pytest

def test_one():
    hand_size = 3
    other_player_names = [ 'Adam', 'Cynthia', 'Greg' ]
    other_players = []
    for p in other_player_names:
        other_players.append(Player(p, hand_size))
    myself = Player('David', hand_size)

    game = Game(myself, other_players)

    assert len(game.cards) > 2

def test_two():
    hand_size = 3
    other_player_names = [ 'Adam', 'Cynthia', 'Greg' ]
    other_players = []
    for p in other_player_names:
        other_players.append(Player(p, hand_size))
    myself = Player('David', hand_size)

    game = Game(myself, other_players)

    assert len(game.players) > 2
