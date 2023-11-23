from datetime import timedelta
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from models.user import User, UserSchema
from setup import db, bcrypt
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/register', methods=['POST'])
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


@users_bp.route('/login', methods=['POST'])
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
