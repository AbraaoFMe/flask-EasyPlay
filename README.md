# Easyplay

EasyPLay is the new way to go when matching a Game. You can create a game event and let your friends join it.

## Tecnologies
This project was developed using the following tecnologies:

- [Python] (https://www.python.org/)
- [Flask] (https://flask.palletsprojects.com/)
- [SQLite] (https://www.sqlite.org/index.html)
- [FontAwesome] (https://fontawesome.com/)

## Project

It is a single file application, all the setup, forms and models are defined in the 'application.py' file. The templates and the static files, such as stylesheets and scripts are in the static folder.

## Installation

```bash
pip3 install requirements.txt # install the dependencies using pip
export SECRET_KEY='hard to guess string' # set up the secret key environment variable
python3 database-creatioin.py # creates the database and populates it with examples
export FLASK_APP=application.py # Set environment variable FLASK_APP to be the application.py file
flask run # run flask application
```

If you want to test the app without creating the users and games in the database, here are some ready examples for you to try
- user: 'a@mail.com' 'asdf'
- user: 'b@mail.com' 'asdf'
- user: 'c@mail.com' 'asdf

## Usage

- The user can register in the endpoint '/register'
- The user can login in the endpoint '/login'

Once logged in, the user can:

- See the games he is enrolled in '/games' or '/'
- Create a game in 'games/new'
- Join a game in 'games/join'
- Query the details of a game in 'games/{id_game}'
- Join a specific game in 'games/{id_game}/join'
- Quit a specific game in 'games/{id_game}/quit'

## License

This project is under MIT License.