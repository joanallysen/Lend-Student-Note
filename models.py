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
    isbn = db.Column(db.String(13), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(
        db.Enum('Minimum', 'Good', 'Brand New', name='condition_enum'),
        nullable=False
    )
    pickup_location = db.Column(db.String(200), nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    is_lend = db.Column(db.Boolean, default=True, nullable=False)
    lender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lended_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    lender = db.relationship('User', foreign_keys=[lender_id], backref='books_owned')
    borrower = db.relationship('User', foreign_keys=[lended_to_id], backref='books_borrowed')

    def __repr__(self):
        return f'<Note {self.title}>'
    
# class Cart(db.Model):
#     cart_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

#     user = db.relationship('User', backref='carts')
#     items= db.relationship('Cart_Item',back_populates='cart')

# class Cart_Item(db.Model):
#     cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id'), primary_key=True)
#     book_id = db.Column(db.Integer, db.ForeignKey('note.note_id'), primary_key=True)
#     quantity = db.Column(db.Integer, nullable=False)

#     cart = db.relationship('Cart', backpopulates='items')

