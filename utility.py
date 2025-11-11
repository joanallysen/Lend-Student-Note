from flask import flash, url_for, redirect, session
from models import db, User
from functools import wraps

# login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Session check - user_id present: {'user_id' in session}")
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            print('User ID not found in the database.')
            flash('User not found. Please log in again.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function