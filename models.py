from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Note(db.Model):
    note_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(17), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(
        db.Enum('Minimum', 'Good', 'Brand New', name='condition_enum'),
        nullable=False
    )
    pickup_location = db.Column(db.String(200), nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('AVAILABLE', 'LENT', 'SOLD', 'RESERVED', name='status_enum'),
        default='AVAILABLE',
        nullable=False
    )

    listing_type = db.Column(
        db.Enum('RENTAL', 'SALE', name='listing_type_enum'),
        nullable=False
    )

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='notes_owned')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='notes_bought')

    def __repr__(self):
        return f'<Note {self.title}>'
    
class Watchlist(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), nullable=False, primary_key=True)
    added_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref ='watchlist_items')
    note = db.relationship('Note', foreign_keys=[note_id], backref = 'watchlisted_by')