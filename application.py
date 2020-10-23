# Imports
import os
from flask import Flask, redirect, render_template, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Import - Database
from flask_sqlalchemy import SQLAlchemy

# Import - Models
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Import - Forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, DateField, TimeField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

# Config
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'

# Models


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    games = db.relationship('Game', secondary="game_players")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin = db.relationship('User', backref='admin', lazy='joined')
    name = db.Column(db.String(64))
    description = db.Column(db.String(100))
    date = db.Column(db.Date())
    time = db.Column(db.Time())
    field = db.Column(db.String(100), nullable=True)
    players = db.relationship('User', secondary="game_players")

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.players.append(self.admin)


class GamePlayer(db.Model):
    __tablename__ = 'game_players'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    user = db.relationship('User', backref='user', lazy='joined')
    game = db.relationship('Game', backref='game', lazy='joined')


# Forms
# Forms - User
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')
    ])
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[
                              DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email alreadu registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

# Forms - Games


class NewGameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', validators=[
        DataRequired()], format='%Y-%m-%d')
    time = TimeField('Time', format='%H:%M')
    field = StringField('Field', validators=[DataRequired()])
    submit = SubmitField('Create New Game')


# Utils functions
def render_player_game(game_player):
    game = game_player.game

    game_rendered = {
        'date': game.date,
        'time': game.time,
        'name': game.name,
        'field': game.field,
        'id': game.id
    }
    return game_rendered


# Routes
# Routes - Games
@app.route('/')
@app.route('/games')
@login_required
def index():
    # Show all the games the user is in and a button to join game and another to create one
    game_player = GamePlayer.query.filter_by(user=current_user).all()

    games = list(map(render_player_game, game_player))

    return render_template('index.html', games=games)


@app.route('/games/join')
@app.route('/games/<int:id>')
def game_details(id=None):
    # Show the game details and players
    # The admin has the same page, but with extra commands to remove, add...
    game = Game.query.get(id)

    return render_template('game_details.html', game=game)


@app.route('/games/<int:id>/join')
@login_required
def game_join(id):
    game = Game.query.get(id)

    if game:
        if current_user not in game.players:
            game.players.append(current_user)
            db.session.commit()
            flash('You were added succesfully', 'sucess')
        else:
            flash('You already were in this game', 'warning')
    else:
        flash("The game you're trying to enter does not exist", 'warning')

    return redirect(url_for('game_details', id=id))

@app.route('/games/<int:id>/quit')
@login_required
def game_quit(id):
    game = Game.query.get(id)

    if game:
        if current_user in game.players:
            game.players.remove(current_user)
            db.session.commit()
            flash('You were removed succesfully', 'sucess')
        else:
            flash('You were not in this game', 'warning')
    else:
        flash("The game you're trying to quit does not exist", 'warning')

    return redirect(url_for('game_details', id=id))


@app.route('/games/new', methods=['GET', 'POST'])
@login_required
def new_game():
    # A form to create a new game
    form = NewGameForm()
    if form.validate_on_submit():
        new_game = Game(
            admin=current_user,
            name=form.name.data,
            description=form.description.data,
            date=form.date.data,
            time=form.time.data,
            field=form.field.data,
        )

        db.session.add(new_game)
        db.session.commit()

        flash('Your game was created succesfully', 'success')
        return redirect(url_for('game_details', id=new_game.id))
    return render_template('new_game.html', form=form)


# Routes - User
@app.route('/register', methods=['GET', 'POST'])
def user_register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            password=form.password.data,
            name=form.name.data
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        flash('Invalid email or password')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def user_logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/test')
def test():
    return render_template('layout.html', title='Test')
