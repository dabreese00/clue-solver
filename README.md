# Clue Solver

## Overview

An app to record your [Clue game](https://en.wikipedia.org/wiki/Cluedo) as it
happens, and let the computer solve it for you!

It has a rudimentary web frontend using Flask.

This is a personal pet (Python) project, pursued purely per passion to see how
hard it would be to program decent logic for solving Clue.  (I may or may not
have also been frustrated about messing up my Clue game sheet by forgetting to
cancel a "show" mark at the right time, and thought to myself that a computer
should be doing this for me...)

Disclaimer regarding the state of the art: I am not targeting it here.  I
haven't even looked around for other extant Clue solvers yet.  I doubt that the
world is seriously lacking a good-enough Clue solver program, at this moment.
I'm just curious to see what I can do.

Other priorities beckon, as always, so I'm writing this README largely as a way
to let myself close the book on this project now, without feeling like it'll be
impossible to re-open it later.


## Notes on the backend

The backend lives in the file `src/app/cluegame.py`.  The classes in this file
are designed to model everything one would write down on one's Clue game sheet.
Essentially, this means: players, cards, and several types of relationships
between them (see [Theory](#theory), below, for more details).

I chose not to use SQL, at least for the initial implementation.  I was curious
whether I could make the code more concise and elegant by just using plain
custom Python classes.  I'm still not sure whether I've succeeded or not, but
I've learned a lot in the attempt either way.  Players and Cards are
namedtuples; relations between them are represented by the ClueRelation class;
and last but not least, the ClueRelationFilter class provides a syntax to build
queries about these relations.

It also needs better unit tests.  But I think it works.

For some examples of the API usage, see the tests for the Game class.

The backend can operate fine without any persistence, but it does implement
persistence methods (for the web interface's benefit) using `pickle`.


## Notes on the frontend

The frontend is currently *very* crude and experimental.

Due to the lack of a proper database, there is no multi-user capability right
now.  If multiple users try to access the same instance of this app, confusion
will certainly ensue!

Game save-and-load is "possible", in that your game is automatically saved and
loaded on each page reload.  But if you lose/exit your browser window and
revisit the home page, you'll find that your only real option at the moment
(without magic special knowledge) is to delete your game and start over.

Error handling is near-nonexistent.  The app crashes easily, because the
frontend neither prevents invalid data entry by the user very well, nor handles
the resulting exceptions raised by the backend.

The UI is exceedingly clunky, and entirely un-styled.  The worst offender
currently, the Game Status display, is nearly unreadable; it's little more than
a debugging info dump of the game state.  There are many major UX improvements
that could or should be made to the input forms, as well.

Some of the above items will hopefully be improved at some point, and at such
time, I'll try to remember to update this README accordingly.

BUT!  For now, if you are an exceptionally savvy user who can read my mind --
or my code -- or if you are just me -- then all the functionality is there for
you to track a game of Clue, and let the computer solve it for you
automatically.


## Theory

Not to go into too much detail, this is how we model a Clue player's game
knowledge.  We have 2 basic entities, of course: Players and Cards.  We want to
track certain types of special relationships between them, that we find out
about during the game, and then make deductions based on those relations.
(When we're lucky, our deductions in turn generate knowledge of additional such
relations, and our patchwork prognosis propagates!)  The types of relations we
want to track:

- a "Have": A relation between 1 player and 1 card, indicating that we know the
  player has the card.

- a "Pass": A relation between 1 player and 1 card, indicating that we know the
  player _does not_ have the card; the opposite of a "Have".

- a "Show": A relation between 1 player and up to 3 cards.  Whenever we
  know that player A showed player B one of several cards, we record a
  "Show" for player A and those cards.

I contend that these three relation types contain all the information we
(or our computers) need to track, in order to be solid Clue players.

In order to show myself precisely _how_ all necessary deductions can be made
from just recording the above relation types, based on standard Clue events --
player A passes for cards XYZ, player B shows player C one of cards XYZ, player
C reveals to me card W -- I've done a little diagram, which can be found in the
"doc" directory.  It is not terribly rigorous in notation, and may need further
explication, but it's what I've got right now, and I found it helpful, so maybe
you will too.

Crazy man's side note, if you have gotten as far as opening the diagram, there
is one particular deduction arrow that I believe is missing from it -- I wonder
if you can spot it?  It's missing from the implementation too; but my faith in
the Clue Solver's efficacy does not waver at this!
