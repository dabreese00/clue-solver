# Clue Solver

## Overview

An app to record your [Clue game](https://en.wikipedia.org/wiki/Cluedo) as it
happens, and let the computer solve it for you!

It has a rudimentary web frontend using Flask.

This is a personal pet (Python) project, pursued purely per paucity of
proficiency, to discover how hard it would be to program decent logic for
solving Clue.  (I may or may not have also been frustrated about messing up my
Clue game sheet by forgetting to cancel a "show" mark at the right time, and
thought to myself that a computer should be doing this for me...)


## Notes on the backend

I've chosen not to use SQL, at least for now.  I was curious whether I could
make the code more concise and elegant by just using plain custom Python
classes.  I'm still not sure if I've succeeded, but I've learned a lot in the
attempt either way.  The most interesting challenge has been developing a way
to write readable queries without SQL.

The high-level Game API is probably somewhat stable now.  For some examples of
the API usage, see the tests for the Game class.


## Notes on the frontend

The web frontend is currently *very* crude and experimental.

There is no multi-user capability right now.  If multiple users try to access
the same instance of this app, confusion will certainly ensue!

Game save-and-load is "possible", in that your game is automatically saved and
loaded on each page reload.  But if you lose/exit your browser window and
revisit the home page, you'll find that your only real option at the moment
(without magic special knowledge) is to delete your game and start over.


## Known issues

- The web app is prone to crash if the user enters invalid data (or even valid
  data that's just logically impossible given the state of the game).  Building
  better error handling and input validation is on the to-do list.

- The web app's Game Status display is nearly unreadable; it's currently little
  more than a debugging info dump of the game state.  Improving this is also on
  the to-do list.

- There are surely lots of other UI/UX improvements to make too.  Maybe I'll
  get there someday.


## Theory

Not to go into too much detail, this section describes how we model a Clue
player's game knowledge.  We have 2 basic entities, of course: Players and
Cards.  We want to track certain types of special relationships between them,
that we find out about during the game, and then make deductions based on those
relations.  (When we're lucky, our deductions in turn generate knowledge of
additional such relations, and our patchwork prognosis propagates!)  The types
of relations we want to track:

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
