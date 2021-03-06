from app import app
from app.forms import (CreateGameForm, InputHandForm, InputPassForm,
                       InputShowForm, InputRevealForm, DeleteGameForm)
from app.cluegame import Game
from flask import render_template, redirect, url_for
import os


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/create_game', methods=['GET', 'POST'])
def create_game():
    if os.path.isfile(app.config['PICKLE_FILEPATH']):
        return redirect(url_for('delete_game'))

    form = CreateGameForm()

    if form.validate_on_submit():
        players = []
        for entry in form.player.data:
            if entry['name'] and entry['hand_size']:
                players.append((entry['name'], int(entry['hand_size'])))
        game = Game(app.config['CLUE_CARDS_PERSONS'],
                    app.config['CLUE_CARDS_WEAPONS'],
                    app.config['CLUE_CARDS_ROOMS'],
                    players)
        game.save(app.config['PICKLE_FILEPATH'])
        return redirect(url_for('input_hand'))
    return render_template('create_game.html', form=form)


@app.route('/input_hand', methods=['GET', 'POST'])
def input_hand():
    game = Game.load(app.config['PICKLE_FILEPATH'])
    if not game:
        return redirect(url_for('index'))  # TODO: Flash warning

    form = InputHandForm()
    form.myself.choices = [(p.name, p.name) for p in game.players]
    form.cards.choices = [(c.name, c.name) for c in game.cards]
    if form.validate_on_submit():
        for c in form.cards.data:
            game.record_have(form.myself.data, c)
        game.save(app.config['PICKLE_FILEPATH'])
        return redirect(url_for('gameplay_view'))

    return render_template('input_hand.html', form=form)


@app.route('/gameplay_view', methods=['GET', 'POST'])
def gameplay_view():
    game = Game.load(app.config['PICKLE_FILEPATH'])
    if not game:
        return redirect(url_for('index'))  # TODO: Flash warning

    # TODO: Check if game is over, do something if so.

    player_choices = [(p.name, p.name) for p in game.players]
    card_choices = [(c.name, c.name) for c in game.cards]

    form_pass = InputPassForm()
    form_show = InputShowForm()
    form_reveal = InputRevealForm()
    for form in [form_pass, form_show, form_reveal]:
        form.player.choices = player_choices
    for form in [form_pass, form_show]:
        for field in form.cards:
            field.choices = card_choices
    form_reveal.card.choices = card_choices

    # work around validate_on_submit bug with multiple forms in one page.
    # ref: https://stackoverflow.com/a/39766205/11686201
    if form_pass.submit_pass.data and form_pass.validate():
        for c in form_pass.cards.data:
            game.record_pass(form_pass.player.data, c)
    elif form_show.submit_show.data and form_show.validate():
        game.record_show(
            form_show.player.data,
            form_show.cards.data)
    elif form_reveal.submit_reveal.data and form_reveal.validate():
        game.record_have(form_reveal.player.data, form_reveal.card.data)

    game.save(app.config['PICKLE_FILEPATH'])

    return render_template('gameplay_view.html', form_pass=form_pass,
                           form_show=form_show, form_reveal=form_reveal,
                           players=game.players, cards=game.cards,
                           relations=game.relations,
                           cards_in_the_file=game.cards_in_the_file)


@app.route('/delete_game', methods=['GET', 'POST'])
def delete_game():
    game = Game.load(app.config['PICKLE_FILEPATH'])
    if not game:
        return redirect(url_for('index'))  # TODO: Flash warning

    form = DeleteGameForm()
    if form.validate_on_submit():
        if form.confirm.data:
            Game.delete(app.config['PICKLE_FILEPATH'])
        return redirect(url_for('index'))
    return render_template('delete_game.html', form=form)
