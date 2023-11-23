from setup import db, ma

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