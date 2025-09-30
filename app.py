from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your-secret-key"  # change this to a secure random value in production
app.permanent_session_lifetime = timedelta(days=30)  # session duration

# use environment variable in production for security
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres.okdgtumarvhlollsyafc:supabase168%3B@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        pw = request.form['password']

        # check if username or email already exists
        if User.query.filter((User.user_name == user_name) | (User.email == email)).first():
            error = "Username or Email already exists."
        else:
            hashed_pw = generate_password_hash(pw, method='pbkdf2:sha256:600000', salt_length=16)
            new_user = User(user_name=user_name, email=email, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_page'))

    return render_template("signup.html", error=error)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        pw = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, pw):
            session.permanent = True  # session will last app.permanent_session_lifetime
            session['user_id'] = str(user.user_id)  # store UUID as string in session
            session['user_name'] = user.user_name
            return redirect(url_for('home'))
        else:
            error = "Login failed. Please try again."

    return render_template("login.html", error=error)


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_name = session.get('user_name')
    return render_template("home.html", user_name=user_name)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# Only use this in development if you want to auto-create tables
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
