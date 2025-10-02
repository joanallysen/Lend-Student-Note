from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
from functools import wraps
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'backupkey')
app.permanent_session_lifetime = timedelta(days=30)

# initialize supabase
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)



def has_login():
    if 'access_token' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('/login_page'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_name = request.form.get('user_name', '')

        try:
            # create user with supabase auth
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "user_name": user_name
                    }
                }
            })
            
            if response.user:
                flash('Signup successful! Please check your email to verify your account.', 'success')
                return redirect(url_for('login_page'))
            
        except Exception as e:
            flash(f'Signup failed: {str(e)}', 'error')

    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # sign in with supabase
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # store tokens in session
                session.permanent = True
                session['access_token'] = response.session.access_token
                session['refresh_token'] = response.session.refresh_token
                session['user_id'] = response.user.id
                session['email'] = response.user.email
                session['user_name'] = response.user.user_metadata.get('user_name', '')
                
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
                
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')

    return render_template("login.html")


@app.route('/home')
def home():
    if (result := has_login()):
        return result
    user_name = session.get('user_name', 'User')
    email = session.get('email')
    return render_template("home.html", user_name=user_name, email=email)


@app.route('/logout')
def logout():
    try:
        # sign out from supabase
        if 'access_token' in session:
            supabase.auth.sign_out()
    except:
        pass  # even if Supabase logout fails, clear the session
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))


@app.route('/')
def index():
    if 'access_token' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)