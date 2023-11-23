from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from os import environ




# Create a Flask web application instance
app = Flask(__name__)

# Configure the secret key for Flask JWT Extended from .flaskenv using environ
app.config['JWT_SECRET_KEY'] = environ.get('JWT_SECRET_KEY')

# Configure the database URI for SQLAlchemy to connect to a PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')

# Create a SQLAlchemy database instance, passing in the Flask app
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)