"""Clue Solver -- Lets you record a Clue game so your computer can solve it!

The board game of Clue is also known as Cluedo.

This package runs a simple Flask web app (see frontend modules, listed below),
which leverages the programming interface provided by the backend modules
(listed below) to allow the user to record the Clue game events as they happen,
and to continually view the resulting sum total Clue game knowledge that this
program is able to deduce from the recorded events.

Flask skeleton and boilerplate code is based on Miguel Grinberg's excellent
Flask Mega-Tutorial, which can be found online.

Frontend modules:
    routes.py -- Flask view functions
    forms.py -- Flask-WTF web form classes

Backend modules:
    cluegame.py -- Tools to record and solve a Clue game
    objectfilter.py -- General tools to query custom Python objects
"""

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
