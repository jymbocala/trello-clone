from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from os import environ

# Create a Flask web application instance
app = Flask(__name__)

# Configure the secret key for Flask JWT Extended from .flaskenv using environ
app.config['JWT_SECRET_KEY'] = environ.get('JWT_SECRET_KEY')

# Configure the database URI for SQLAlchemy to connect to a PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:spameggs123@127.0.0.1:5432/trello'

# Create a SQLAlchemy database instance, passing in the Flask app
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


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

# Define a model class 'Card' that represents a table in the database


class Card(db.Model):
    __tablename__ = 'cards'

    # Define columns for the 'cards' table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    status = db.Column(db.String(30))
    date_created = db.Column(db.Date())

# Define a schema class 'CardSchema' to serialize the Card model to JSON through Marshmallow
class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'descriptioon', 'status', 'date_created')

# Define a model class 'User' that represents a table in the database
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # unique=True prevents repeated email addresses in the table
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


# Define a schema class 'UserSchema' to serialize the User model to JSON through Marshmallow
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'is_admin')


@app.cli.command('db_create')
def db_create():
    db.drop_all()
    db.create_all()
    print('Created tables')


# Define a Flask CLI command 'db_seed' to add sample data to the database
@app.cli.command('db_seed')
def db_seed():
    # Create a list of users  with sample data
    users = [
        User(
            email='admin@example.com',
            password=bcrypt.generate_password_hash(
                'spinynorman').decode('utf8'),
            is_admin=True
        ),
        User(
            name='John Cleese',
            email='johnc@example.com',
            password=bcrypt.generate_password_hash('test123').decode('utf8')
        )
    ]

    # Create a list of cards  with sample data
    cards = [
        Card(
            title='Start the project',
            description='Stage 1 - ERD Creation',
            status='Done',
            date_created=date.today()
        ),
        Card(
            title='ORM Queries',
            description='Stage 2 - Implement CRUD queries',
            status='In Progress',
            date_created=date.today()
        ),
        Card(
            title='Marshmallow',
            description='Stage 3 - Implement JSONify of models',
            status='In Progress',
            date_created=date.today()
        ),
    ]

    # Add cards list to the database session and commit the changes
    db.session.add_all(users)
    db.session.add_all(cards)
    db.session.commit()

    print('Database seeded')


@app.route('/users/register', methods=['POST'])
def register():
    try:
        # Parse incoming POST body through the schema
        # Exlude the id field from the schema as it is auto-generated and should not be provided by the user
        user_info = UserSchema(exclude=['id']).load(request.json)
        # Create a new user with the parsed data
        user = User(
            # .get method returns the value of the key if it exists, otherwise returns an empty string
            name=user_info.get('name', ''),
            email=user_info['email'],
            password=bcrypt.generate_password_hash(
                user_info['password']).decode('utf8')
        )

        # Add the new user to the database session and commit the changes
        db.session.add(user)
        db.session.commit()

        # Return the new user data and 201 Created status code
        return UserSchema(exclude=['password', 'is_admin']).dump(user), 201
    except IntegrityError:
        # Return 409 Conflict status code if the email already exists in the database
        return {'message': 'Email already exists'}, 409


@app.route('/users/login', methods=['POST'])
def login():
    # 1. Parse incoming POST body through the schema
    user_info = UserSchema(
        exclude=['id', 'name', 'is_admin']).load(request.json)

    # 2. Select the user with email that matches the one in the POST body
    stmt = db.select(User).where(User.email == user_info['email'])
    user = db.session.scalar(stmt)

    # 3. Check password hash
    if user and bcrypt.check_password_hash(user.password, user_info['password']):
        # 4. Create a JWT token
        token = create_access_token(identity=user.email, expires_delta=timedelta(
            # identity is the payload of the JWT token (the user's email)
            hours=2))

        # 5. Return the token and user data
        return {'token': token, 'user': UserSchema(exclude=['password', 'is_admin', 'name']).dump(user)}
    else:
        return {'error': 'Invalid email or password'}, 401


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
