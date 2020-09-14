from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, FieldList, FormField,
                     SelectField, SelectMultipleField, BooleanField)


class CreatePlayerForm(FlaskForm):
    name = StringField('Name')
    hand_size = StringField('Cards in hand')


class CreateGameForm(FlaskForm):
    player = FieldList(FormField(CreatePlayerForm),
                       min_entries=6, max_entries=6, label="Players")
    submit = SubmitField()


class InputHandForm(FlaskForm):
    myself = SelectField('Myself')
    cards = SelectMultipleField('My cards')
    submit = SubmitField()


class InputPassForm(FlaskForm):
    player = SelectField('Player')
    cards = FieldList(SelectField('Cards'), min_entries=3, max_entries=3)
    submit_pass = SubmitField('Record pass')


class InputShowForm(FlaskForm):
    player = SelectField('Player')
    cards = FieldList(SelectField('Cards'), min_entries=3, max_entries=3)
    submit_show = SubmitField('Record show')


class InputRevealForm(FlaskForm):
    player = SelectField('Player')
    card = SelectField('Card')
    submit_reveal = SubmitField('Record reveal')


class DeleteGameForm(FlaskForm):
    confirm = BooleanField('Are you sure you want to delete the saved game?')
    submit = SubmitField('Delete game')
