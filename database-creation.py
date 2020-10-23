from application import db, User, Game, GamePlayer
import datetime

db.drop_all()
db.create_all()

users = [
    {
        'email': 'a@mail.com',
        'username': 'atest',
        'name': 'A Teast',
        'password': 'asdf'
    },
    {
        'email': 'b@mail.com',
        'username': 'btest',
        'name': 'B Test',
        'password': 'asdf'
    },
    {
        'email': 'c@mail.com',
        'username': 'ctest',
        'name': 'C Test',
        'password': 'asdf'
    },
]

games = [
    {
        'name': 'Handball Top',
        'description': 'Jogo terça no ginásio',
        'date': {
            'year': 2020,
            'month': 10,
            'day': 23
        },
        'time': {
            'hour': 10,
            'minute': 30
        },
        'field': 'Quadra do ginásio'
    },
    {
        'name': 'Handball Top1',
        'description': 'Jogo terça no ginásio',
        'date': {
            'year': 2020,
            'month': 10,
            'day': 24
        },
        'time': {
            'hour': 10,
            'minute': 30
        },
        'field': 'Quadra do ginásio'
    },
    {
        'name': 'Handball Top2',
        'description': 'Jogo terça no ginásio',
        'date': {
            'year': 2020,
            'month': 10,
            'day': 23
        },
        'time': {
            'hour': 11,
            'minute': 30
        },
        'field': 'Quadra do ginásio'
    },
    {
        'name': 'Handball CSL',
        'description': 'Jogo terça no ginásio',
        'date': {
            'year': 2020,
            'month': 10,
            'day': 23
        },
        'time': {
            'hour': 10,
            'minute': 31
        },
        'field': 'Quadra do csl'
    },
]

for user in users:
    new_user = User(
        email=user['email'],
        username=user['username'],
        password=user['password'],
        name=user['name']
    )

    db.session.add(new_user)

user1 = User.query.first()
user2 = User.query.filter_by(id=2).first()

for game in games:
    new_game = Game(
        admin=user2,
        name=game['name'],
        description=game['description'],
        date=datetime.date(
            year=game['date']['year'],
            month=game['date']['month'],
            day=game['date']['day']
        ),
        time=datetime.time(
            hour=game['time']['hour'],
            minute=game['time']['minute'],
        ),
        field=game['field']
    )

    db.session.add(new_game)
    new_game.players.append(user1)


db.session.commit()

