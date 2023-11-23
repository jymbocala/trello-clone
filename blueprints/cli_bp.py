from flask import Blueprint
from setup import db, bcrypt
from models.user import User
from models.card import Card
from datetime import date

db_commands = Blueprint('db', __name__)


@db_commands.cli.command('create')
def db_create():
    db.drop_all()
    db.create_all()
    print('Created tables')


# Define a Flask CLI command 'db_seed' to add sample data to the database
@db_commands.cli.command('seed')
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
