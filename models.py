from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import not_, and_

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    about = db.Column(db.String(200), nullable=False, default='Hey! I am using Student Lent Note')
    created_at = db.Column(db.DateTime, default=db.func.now())

    avg_rating = db.Column(db.Numeric(3, 2), default=0.00)
    rating_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.username}>'

class Note(db.Model):
    note_id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(17), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    price_sale = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(
        db.Enum('MINIMUM', 'GOOD', 'BRAND NEW', name='condition_enum'),
        nullable=False
    )
    pickup_location = db.Column(db.String(200), nullable=False)
    available_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum('AVAILABLE', 'LENT', 'SOLD', 'RESERVED', 'HIDDEN', 'NEED ACTION','DELETED', name='status_enum'),
        default='AVAILABLE',
        nullable=False
    )

    listing_type = db.Column(
        db.Enum('RENTAL', 'SALE', 'BOTH', name='listing_type_enum'),
        nullable=False
    )
    listing_date = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    
    incoming_return_date = db.Column(db.DateTime, nullable=True)
    avg_rating = db.Column(db.Numeric(3, 2), default=0.00)
    rating_count = db.Column(db.Integer, default=0)

    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    # Button later for updating history.transaction_date
    current_history_id = db.Column(db.Integer, db.ForeignKey('history.history_id'), nullable=True)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='notes_owned')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='notes_bought')
    current_history = db.relationship('History', foreign_keys=[current_history_id], post_update=True)

    tags = db.Column(db.String(200), nullable=True)

    # embed for similarity later
    embedding = db.Column(db.PickleType, nullable=True)
    def __repr__(self):
        return f'<Note {self.title}>'
    

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

    total_price = db.Column(db.Numeric(10, 2), nullable=False) # for lend per week and sale
    buying_type = db.Column(
        db.Enum('BUY', 'BORROW', name='buying_type_enum'),
        nullable=False
    )
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    cart = db.relationship('Cart', back_populates='items')
    note_details = db.relationship('Note')

    def weeks_borrowed(self):
        if self.buying_type == 'BORROW' and self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return (delta.days // 7) + (1 if delta.days % 7 > 0 else 0)
        return 0

# change to have owner_id, so can immediately access owner.gotten_review so owner can see the review they got
# so all review in owned owned notes will be the review to the seller ? Maybe in the future.
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

# buyer and owner history
class History(db.Model):
    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), nullable=False)
    transaction_type = db.Column(
        db.Enum('BUY', 'BORROW', name='history_transaction_type_enum'),
        nullable=False
    )
    borrow_start_date = db.Column(db.DateTime)
    transaction_date = db.Column(db.DateTime)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Two separate relationships for buyer and owner
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
    owner = db.relationship('User', foreign_keys=[owner_id], backref='sales')
    note = db.relationship('Note', foreign_keys=[note_id], backref='history_records')

    def __repr__(self):
        return f'<History {self.history_id}: {self.transaction_type} - Buyer: {self.buyer_id}, Owner: {self.owner_id}>'

'''
total lended = history get note filter by owner_id, transaction_type(BORROW)
total sold = history filter by owner_id, transaction_type(BUY)
earned from lending = total lended note.price sum
earned from selling = total sold note.price sum
total earned = lending earned + sell earnn
'''
