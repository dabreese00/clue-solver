from app.cluegame import (Player, ClueRelationType, Game, ClueCardType)
import pytest


@pytest.fixture
def clue_game():
    hand_size = 3
    other_player_names = {'Adam', 'Cynthia', 'Greg'}
    other_players = set()
    for p in other_player_names:
        other_players.add(Player(p, hand_size))
    myself = Player('David', hand_size)

    return Game(
            {
                ClueCardType.PERSON:
                    [
                        "Colonel Mustard",
                        "Miss Scarlet",
                        "Professor Plum",
                        "Mrs. White",
                        "Mr. Green",
                        "Mrs. Peacock"
                    ],
                ClueCardType.WEAPON:
                    [
                        "Rope",
                        "Lead Pipe",
                        "Revolver",
                        "Candlestick",
                        "Knife",
                        "Wrench"
                    ],
                ClueCardType.ROOM:
                    [
                        "Billiard Room",
                        "Ballroom",
                        "Lounge",
                        "Kitchen",
                        "Conservatory",
                        "Library",
                        "Dining Room",
                        "Hall",
                        "Study"
                    ]
            },
            myself,
            other_players)


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
                game.get_card('Ballroom'),
                game.get_card('Rope')
            })

    game.record_have_pass(
            rel_type=ClueRelationType.HAVE,
            player=game.get_player('Greg'),
            card=game.get_card('Rope')
            )

    game.record_have_pass(
            rel_type=ClueRelationType.PASS,
            player=game.get_player('Greg'),
            card=game.get_card('Ballroom'))

    having_cards_dicts = []
    unhaving_cards_dicts = []
    for r in game.relations:
        if r.rel_type == ClueRelationType.HAVE:
            having_cards_dicts.append({
                "player": r.player.name,
                "card": r.cards[0].name})
        elif r.rel_type == ClueRelationType.PASS:
            unhaving_cards_dicts.append({
                "player": r.player.name,
                "card": r.cards[0].name})
    assert len(having_cards_dicts) == 4
    assert {"player": "Greg", "card": "Rope"} in having_cards_dicts
    assert {"player": "Greg", "card": "Ballroom"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Rope"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Ballroom"} in unhaving_cards_dicts


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

    game.record_have_pass(
            rel_type=ClueRelationType.HAVE,
            player=game.get_player('Greg'),
            card=game.get_card('Ballroom'))

    game.record_show(
            game.get_player('Greg'),
            {
                game.get_card('Colonel Mustard'),
                game.get_card('Rope'),
                game.get_card('Billiard Room')
            })

    for p in game.players:
        for c in ['Professor Plum', 'Knife', 'Library']:
            game.record_have_pass(
                    rel_type=ClueRelationType.PASS,
                    player=p,
                    card=game.get_card(c))

    assert game.get_card('Professor Plum') in game.cards_in_the_file
    assert game.get_card('Knife') in game.cards_in_the_file
    assert game.get_card('Library') in game.cards_in_the_file
    assert game.get_card('Colonel Mustard') not in game.cards_in_the_file
    assert game.get_card('Billiard Room') not in game.cards_in_the_file
    assert game.get_card('Ballroom') not in game.cards_in_the_file
    assert game.get_card('Lead Pipe') not in game.cards_in_the_file
    having_cards_dicts = []
    unhaving_cards_dicts = []
    for r in game.relations:
        if r.rel_type == ClueRelationType.HAVE:
            having_cards_dicts.append({
                "player": r.player.name,
                "card": r.cards[0].name})
        elif r.rel_type == ClueRelationType.PASS:
            unhaving_cards_dicts.append({
                "player": r.player.name,
                "card": r.cards[0].name})
    assert {"player": "Greg", "card": "Rope"} in having_cards_dicts
    assert {"player": "Cynthia", "card": "Rope"} in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Ballroom"} in unhaving_cards_dicts
