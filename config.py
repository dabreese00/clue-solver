import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    PICKLE_FILEPATH = os.environ.get('CLUE_PICKLE_FILEPATH') or 'game.pickledb'
    CLUE_CARDS_PERSONS = \
        [
            "Colonel Mustard",
            "Miss Scarlet",
            "Professor Plum",
            "Mrs. White",
            "Mr. Green",
            "Mrs. Peacock"
        ]
    CLUE_CARDS_WEAPONS = \
        [
            "Rope",
            "Lead Pipe",
            "Revolver",
            "Candlestick",
            "Knife",
            "Wrench"
        ]
    CLUE_CARDS_ROOMS = \
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
