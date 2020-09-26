from app.cluegame import ClueRelationType, Game
import pytest


@pytest.fixture
def clue_game():
    return Game(
            [
                "Colonel Mustard",
                "Miss Scarlet",
                "Professor Plum",
                "Mrs. White",
                "Mr. Green",
                "Mrs. Peacock"
            ],
            [
                "Rope",
                "Lead Pipe",
                "Revolver",
                "Candlestick",
                "Knife",
                "Wrench"
            ],
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
            ],
            {
                ('Adam', 5),
                ('Cynthia', 5),
                ('Greg', 4),
                ('David', 4)
            }
        )


def test_game_setup(clue_game):
    game = clue_game

    assert len(game.cards) > 2
    assert len(game.players) == 4


def test_unique_names():
    with pytest.raises(ValueError):
        Game(
                [
                    "Colonel Mustard"
                ],
                [
                    "Rope"
                ],
                [
                    "Billiard Room",
                    "Ballroom"
                ],
                {
                    ('Adam', 1),
                    ('Adam', 0)
                }
            )
    with pytest.raises(ValueError):
        Game(
                [
                    "Colonel Mustard",
                    "Colonel Mustard"
                ],
                [
                    "Rope",
                    "Lead Pipe"
                ],
                [
                    "Billiard Room",
                    "Ballroom"
                ],
                {
                    ('Adam', 2),
                    ('Cynthia', 1)
                }
            )


def test_invalid_hand_sizes():
    with pytest.raises(ValueError):
        Game(
                [
                    "Colonel Mustard"
                ],
                [
                    "Rope"
                ],
                [
                    "Billiard Room"
                ],
                {
                    ('Adam', 1),
                    ('Cynthia', 0)
                }
            )
    with pytest.raises(ValueError):
        Game(
                [
                    "Colonel Mustard",
                    "Miss Scarlet"
                ],
                [
                    "Rope"
                ],
                [
                    "Billiard Room"
                ],
                {
                    ('Adam', 0),
                    ('Cynthia', 0)
                }
            )

    game = Game(
            [
                "Colonel Mustard",
                "Miss Scarlet"
            ],
            [
                "Rope"
            ],
            [
                "Billiard Room"
            ],
            {
                ('Adam', 1),
                ('Cynthia', 0)
            }
        )
    assert len(game.cards) == 4
    assert len(game.players) == 2


def test_simple_show_and_have(clue_game):
    game = clue_game

    myself = 'David'
    initial_hand = ['Colonel Mustard',
                    'Miss Scarlet',
                    'Billiard Room',
                    'Mr. Green']
    for c in initial_hand:
        game.record_have(myself, c)

    game.record_show(
            'Greg',
            {
                'Colonel Mustard',
                'Ballroom',
                'Rope'
            })

    game.record_have('Greg', 'Rope')

    game.record_pass('Greg', 'Ballroom')

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
    assert len(having_cards_dicts) == 5
    assert {"player": "Greg", "card": "Rope"} in having_cards_dicts
    assert {"player": "Greg", "card": "Ballroom"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Rope"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Ballroom"} in unhaving_cards_dicts
    having_cards_dicts = []
    unhaving_cards_dicts = []


def test_player_whole_hand_known(clue_game):
    game = clue_game

    myself = 'David'
    initial_hand = ['Colonel Mustard',
                    'Miss Scarlet',
                    'Billiard Room',
                    'Mr. Green']
    for c in initial_hand:
        game.record_have(myself, c)

    for c in ['Professor Plum', 'Knife', 'Library', 'Kitchen', 'Rope']:
        game.record_have('Adam', c)

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
    assert {"player": "David", "card": "Study"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Mrs. White"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Mrs. Peacock"} in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Study"} in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Mrs. White"} in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Mrs. Peacock"} in unhaving_cards_dicts
    having_cards_dicts = []
    unhaving_cards_dicts = []


def test_card_type_completed(clue_game):
    game = clue_game

    myself = 'David'
    initial_hand = ['Colonel Mustard',
                    'Miss Scarlet',
                    'Billiard Room',
                    'Mr. Green']
    for c in initial_hand:
        game.record_have(myself, c)

    for c in ['Professor Plum', 'Mrs. White']:
        game.record_have('Adam', c)

    assert 'Mrs. Peacock' in [c.name for c in game.cards_in_the_file]
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
    assert {"player": "David", "card": "Study"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Mrs. White"} in unhaving_cards_dicts
    assert {"player": "David", "card": "Mrs. Peacock"} in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Study"} not in unhaving_cards_dicts
    assert {"player": "Adam", "card": "Mrs. White"} in having_cards_dicts
    assert {"player": "Adam", "card": "Mrs. Peacock"} in unhaving_cards_dicts
    having_cards_dicts = []
    unhaving_cards_dicts = []


def test_simple_game(clue_game):
    game = clue_game

    myself = 'David'
    initial_hand = ['Colonel Mustard',
                    'Miss Scarlet',
                    'Billiard Room',
                    'Mr. Green']
    for c in initial_hand:
        game.record_have(myself, c)

    game.record_show(
            'Greg',
            {
                'Colonel Mustard',
                'Rope',
                'Ballroom'
            })

    game.record_have('Greg', 'Ballroom')

    game.record_show(
            'Greg',
            {
                'Colonel Mustard',
                'Rope',
                'Billiard Room'
            })

    for p in game.players:
        for c in ['Professor Plum', 'Knife', 'Library']:
            game.record_pass(p, c)

    assert 'Professor Plum' in [c.name for c in game.cards_in_the_file]
    assert 'Knife' in [c.name for c in game.cards_in_the_file]
    assert 'Library' in [c.name for c in game.cards_in_the_file]
    assert 'Colonel Mustard' not in [c.name for c in game.cards_in_the_file]
    assert 'Billiard Room' not in [c.name for c in game.cards_in_the_file]
    assert 'Ballroom' not in [c.name for c in game.cards_in_the_file]
    assert 'Lead Pipe' not in [c.name for c in game.cards_in_the_file]
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
    having_cards_dicts = []
    unhaving_cards_dicts = []
