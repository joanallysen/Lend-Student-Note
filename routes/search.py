from flask import Flask, redirect, url_for, request, render_template,Blueprint
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from models import db,Note
import re

search = Blueprint("search",__name__)

# search.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

@search.route('/search', methods=["POST","GET"])
def search_note():
    
    user_input = request.args.get('user_input','')
    cleaned_input = re.sub(r'\s+', ' ', user_input).strip().lower()

    search_output=[]
    if cleaned_input:
            
        search_filter=[
            Note.title.ilike(f'%{cleaned_input}%'),
            Note.isbn == cleaned_input
        ]

        search_output = Note.query.filter(or_(*search_filter)).all()

    return render_template("search_testing.html", results = search_output, user_input = cleaned_input) 
