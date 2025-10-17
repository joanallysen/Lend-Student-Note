from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import not_

db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    avg_rating = db.Column(db.Numeric(3, 2), default=0.00)
    rating_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.username}>'

note_tag_association=db.Table(
    'note_tag_association', 
    db.Column('note_id',db.Integer, db.ForeignKey('note.note_id', primary_key=True)),
    db.Column('tag_id',db.Integer, db.ForeignKey('tag.tag_id', primary_key=True))
)
class Note(db.Model):
    note_id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(17), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(
        db.Enum('MINIMUM', 'GOOD', 'BRAND NEW', name='condition_enum'),
        nullable=False
    )
    pickup_location = db.Column(db.String(200), nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.Enum('AVAILABLE', 'LENT', 'SOLD', 'RESERVED', 'HIDDEN', 'NEED ACTION', name='status_enum'),
        default='AVAILABLE',
        nullable=False
    )

    listing_type = db.Column(
        db.Enum('RENTAL', 'SALE', 'BOTH', name='listing_type_enum'),
        nullable=False
    )
    listing_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    avg_rating = db.Column(db.Numeric(3, 2), default=0.00)
    rating_count = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='notes_owned')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='notes_bought')

    tags = db.relationship('Tag', secondary=note_tag_association, back_populates='notes')
    def __repr__(self):
        return f'<Note {self.title}>'
    
class Tag(db.Model):
    tag_id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable = False)

    notes = db.relationship('Note', secondary=note_tag_association, back_populates='tags')

class Watchlist(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), nullable=False, primary_key=True)
    added_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref ='watchlist_items')
    note = db.relationship('Note', foreign_keys=[note_id], backref = 'watchlisted_by')

class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    items= db.relationship('CartItem',back_populates='cart')

class CartItem(db.Model):
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    buying_type = db.Column(
        db.Enum('BUY', 'BORROW', name='buying_type_enum'),
        nullable=False
    )
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    cart = db.relationship('Cart', back_populates='items')
    note_details = db.relationship('Note')

class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    star = db.Column(db.Integer, nullable=False) # range 1-5
    review = db.Column(db.String(400), nullable=False) 
    added_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('note_id', 'user_id', name='unique_user_note_review'),
        db.CheckConstraint('star >= 1 AND star <= 5', name = 'check_star_range'),
    )

    note = db.relationship('Note', backref='reviews')
    user = db.relationship('User', backref='reviews')

    def __repr__(self):
        return f'<Review {self.review_id}: {self.star} stars by User {self.user_id}>'

class History(db.Model):
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), nullable=False)
    transaction_type = db.Column(
        db.Enum('BUY', 'BORROW', name='history_transaction_type_enum'),
        nullable=False
    )
    borrow_start_date = db.Column(db.DateTime)
    transaction_date = db.Column(db.DateTime) # buying or returning book
    
    user = db.relationship('User', foreign_keys=[user_id], backref='history')
    note = db.relationship('Note', backref='history_records')

    def __repr__(self):
        return f'<History {self.history_id}: {self.transaction_type} by User {self.user_id}>'
    