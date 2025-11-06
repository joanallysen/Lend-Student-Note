from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy import and_

from models import db, User, Note, Watchlist,Tag,note_tag_association,CartItem, Cart,not_, History, Review

from routes.notes_bp import notes_bp
from routes.watchlist_bp import watchlist_bp
from routes.search_bp import search_bp
from routes.shopping_cart_bp import shopping_cart
from routes.borrowed_bp import borrowed_bp
from routes.review_bp import review_bp

from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(notes_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(search_bp)
app.register_blueprint(shopping_cart)
app.register_blueprint(borrowed_bp)
app.register_blueprint(review_bp)
# create the database tables
with app.app_context():
    db.create_all()

# login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Session check - user_id present: {'user_id' in session}")
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# routes
@app.route('/')
def index():
    # if 'user_id' in session:
    #     user = db.session.get(User, session['user_id'])
    #     return render_template('index.html', user=user)
    # return render_template('index.html')
    return redirect(url_for('explore'))

@app.route('/explore')
def explore():
    user_id = session.get('user_id')
    notes = Note.query.filter(not_(Note.status == 'HIDDEN')).all()

    watchlisted_note_ids = {nid[0] for nid in db.session.query(Watchlist.note_id).filter_by(user_id=user_id).all()}

    user_cart = Cart.query.filter_by(user_id=user_id).first()
    
    # user cart is not created upon initialization but when opening user_cart
    if not user_cart:
        cart_note_ids = None
    else:
        cart_note_ids = {nid[0] for nid in db.session.query(CartItem.note_id).filter_by(cart_id=user_cart.cart_id).all()}

    return render_template('explore.html', notes=notes, user_id=user_id, watchlisted_note_ids=watchlisted_note_ids, cart_note_ids=cart_note_ids)

@app.route('/detail/<int:note_id>', methods=['POST', 'GET'])
def detail(note_id):
    user_id= session.get('user_id')
    if request.method == 'POST':
        pass

    note = Note.query.get_or_404(note_id)

    related_books = db.session.query(Note).join(
    note_tag_association, Note.note_id == note_tag_association.c.note_id
    ).filter(
    note_tag_association.c.tag_id.in_(
        db.session.query(note_tag_association.c.tag_id)
        .filter(note_tag_association.c.note_id == note_id)
    ),
    Note.note_id != note_id ).distinct().all()

    my_review = None
    other_reviews = []
    
    for review in note.reviews:
        if review.user_id != user_id:
            other_reviews.append(review)
        else:
            my_review = review
    
    return render_template('detail.html', note=note, related_books=related_books,
                            my_review=my_review.to_dict() if my_review else None, 
                            note_reviews=[review.to_dict() for review in other_reviews])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        # check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('signup'))

        # create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['email'] = user.email
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, int(session['user_id']))
    # notes_owned is redundant
    owned_notes = user.notes_owned

    return render_template('dashboard.html', user=user, owned_notes=owned_notes)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/watchlist')
@login_required
def watchlist():
    user_id = session['user_id']
    watchlist_items = Watchlist.query.filter_by(user_id=user_id).all()
    notes = [item.note for item in watchlist_items]
    return render_template('watchlist.html', notes=notes)

def make_history_dictionary(history):
    history_dict = defaultdict(list)
    for h in history:
        transaction_date = h.transaction_date.date() if h.transaction_date else h.borrow_start_date.date()
        transaction_date = transaction_date.strftime('%#d %B')
        history_dict[transaction_date].append({
            'note': h.note,
            'transaction_type': h.transaction_type,
            'borrow_start_date': h.borrow_start_date,
            'transaction_date': h.transaction_date,
            'total_price': h.total_price
        })
        print(f'this are the borrow start date: {h.borrow_start_date}')
    return history_dict

@app.route('/history')
@login_required
def history():
    print(f"Adding to history")
    user_id = session['user_id']
    history_buyer = History.query.filter_by(buyer_id=user_id).order_by(History.transaction_date).all()
    history_owner = History.query.filter_by(owner_id=user_id).order_by(History.transaction_date).all()
    history_buyer = make_history_dictionary(history_buyer) 
    history_owner = make_history_dictionary(history_owner)
    
    return render_template('history.html', history_buyer=history_buyer, history_owner=history_owner)

if __name__ == '__main__':
    app.run(debug=True)