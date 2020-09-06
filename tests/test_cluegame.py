from app.cluegame import ClueCardType, Card, Player, Have, Show, Game
import pytest

@pytest.fixture
def clue_game():
    hand_size = 3
    other_player_names = { 'Adam', 'Cynthia', 'Greg' }
    other_players = set()
    for p in other_player_names:
        other_players.add(Player(p, hand_size))
    myself = Player('David', hand_size)

    return Game(myself, other_players)


def test_one(clue_game):
    game = clue_game

    assert len(game.cards) > 2
    assert len(game.players) == 4


def test_three(clue_game):
    game = clue_game

    game.input_hand({
            game.get_card('Colonel Mustard'),
            game.get_card('Miss Scarlet'),
            game.get_card('Billiard Room')
            })

    game.record_show(
            game.get_player('Greg'),
            {
                game.get_card('Colonel Mustard'),
                game.get_card('Billiard Room'),
                game.get_card('Rope')
            })

    game.record_have(
            game.get_player('Greg'),
            game.get_card('Rope'),
            True
            )

    assert game.shows[0].is_void
