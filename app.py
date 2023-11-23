from flask import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.card import Card, CardSchema
from setup import *
from blueprints.cli_bp import db_commands
from blueprints.users_bp import users_bp


def admin_required():
    # get instance of a user
    user_email = get_jwt_identity()
    # select user from db where email matches the one in the JWT token
    stmt = db.select(User).where(User.email == user_email)
    # scalar() returns the first result of the query
    user = db.session.scalar(stmt)

    # check if user is admin
    if not (user and user.is_admin):
        # return is not used here because we want to stop the execution of the function and return a 401 error instead of continuing with the rest of the code in the '/cards' route
        abort(401)


# Define a custom error handler for all 401 Unauthorized responses
@app.errorhandler(401)
def unauthorized(err):
    return {'error': 'You are not authorized to access this resource'}

# Register the Flask CLI blueprint to the app
app.register_blueprint(db_commands)

# Register the Flask users blueprint to the app
app.register_blueprint(users_bp)


@app.route('/cards')
@jwt_required()
def all_cards():

    # check if user is admin
    admin_required()

    # else return all cards from db
    stmt = db.select(Card).order_by(Card.title.desc())
    # stmt = db.select(Card).where(db.or_(Card.status != 'Done', Card.id > 2)).order_by(Card.title.desc())
    cards = db.session.scalars(stmt).all()
    return CardSchema(many=True).dump(cards)
    # return [card.to_dict() for card in cards]


@app.route('/')
def index():
    return 'Hello World!'
