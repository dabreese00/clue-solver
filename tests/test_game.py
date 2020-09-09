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


def test_game_setup(clue_game):
    game = clue_game

    assert len(game.cards) > 2
    assert len(game.players) == 4


def test_simple_show_and_have(clue_game):
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

def test_simple_game(clue_game):
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
                game.get_card('Rope'),
                game.get_card('Ballroom')
            })

    game.record_have(
            game.get_player('Greg'),
            game.get_card('Ballroom'),
            True
            )

    game.record_show(
            game.get_player('Greg'),
            {
                game.get_card('Colonel Mustard'),
                game.get_card('Rope'),
                game.get_card('Billiard Room')
            })


    for p in game.players:
        for c in ['Professor Plum', 'Knife', 'Library']:
            game.record_have(
                    p,
                    game.get_card(c),
                    False)

    assert game.get_card('Professor Plum') in game.cards_in_the_file
    assert game.get_card('Knife')          in game.cards_in_the_file
    assert game.get_card('Library')        in game.cards_in_the_file
    assert game.get_card('Colonel Mustard') not in game.cards_in_the_file
    assert game.get_card('Billiard Room') not in game.cards_in_the_file
    assert game.get_card('Ballroom') not in game.cards_in_the_file
    assert game.get_card('Lead Pipe') not in game.cards_in_the_file
    having_cards_dicts = []
    for h in game.haves:
        if h.yesno:
            having_cards_dicts.append({"player": h.player.name, "card": h.card.name})
    assert {"player": "Greg", "card": "Rope"} in having_cards_dicts
    unhaving_cards_dicts = []
    for h in game.haves:
        if not h.yesno:
            unhaving_cards_dicts.append({"player": h.player.name, "card": h.card.name})
    assert {"player": "Cynthia", "card": "Rope"} in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Ballroom"} in unhaving_cards_dicts
