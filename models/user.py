from setup import db, ma


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