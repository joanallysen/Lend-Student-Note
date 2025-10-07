from flask import Flask, redirect, url_for, request, render_template,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import re

app= Flask (__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(db.Enum('Minimum', 'Good', 'Brand New', name='condition_enum'), nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    available_date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    is_lend = db.Column(db.Boolean, default=True, nullable=False)
    lender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lended_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    lender = db.relationship('User', foreign_keys=[lender_id], backref='books_owned')
    borrower = db.relationship('User', foreign_keys=[lended_to_id], backref='books_borrowed')

    def __repr__(self):
        return f'<Book {self.title}>'
    
@app.route('/')
def index():
    return redirect(url_for("search"))
@app.route('/search', methods=["POST","GET"])
def search():
    
    user_input = request.args.get('user_input','')
    cleaned_input = re.sub(r'\s+', ' ', user_input).strip().lower()

    search_output=[]
    if cleaned_input:
            
        search_filter=[
            User.username.ilike(f'%{cleaned_input}%'),
            User.email.ilike(f'%{cleaned_input}%')
        ]
        search_output = User.query.filter(or_(*search_filter)).all()

   
        
    return render_template("search_testing.html", results = search_output, user_input = cleaned_input) 
    

if __name__ == "__main__":
    app.run(debug=True)