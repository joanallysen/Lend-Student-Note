from flask import Flask, redirect, url_for, request, render_template, Blueprint, session
from sqlalchemy import or_
from models import db, Note, Cart, CartItem, Watchlist
import re

search_bp = Blueprint("search_bp",__name__)

def is_eligible(num):
    try:
        return float(num)>0
    except ValueError:
        return False

@search_bp.route('/search', methods=["GET"])
def search_note():
    user_id = session.get('user_id')
    watchlisted_note_ids = {nid[0] for nid in db.session.query(Watchlist.note_id).filter_by(user_id=user_id).all()}

    user_cart = Cart.query.filter_by(user_id=user_id).first()
    
    # user cart is not created upon initialization but when opening user_cart
    if not user_cart:
        cart_note_ids = None
    else:
        cart_note_ids = {nid[0] for nid in db.session.query(CartItem.note_id).filter_by(cart_id=user_cart.cart_id).all()}
    
    user_input = request.args.get('user_input','')
    #Additional Filter
    sort_by = request.args.get('sort_by','')
    availability = request.args.get('is_available')
    condition = request.args.get('condition','')
    min_price =  request.args.get('min_price')
    max_price = request.args.get('max_price')

    cleaned_input = re.sub(r'\s+', ' ', user_input).strip().lower()
    
    search_output=[]
    if cleaned_input or condition:
            
        search_filter=[
            Note.title.ilike(f'%{cleaned_input}%')
        ]
            # Note.isbn == cleaned_input,

        if condition:
            search_filter.append(Note.condition == condition)
        
        if availability == 'available':
            search_filter.append(Note.status == 'AVAILABLE')

        if min_price:
            if is_eligible(min_price):
                search_filter.append(Note.price>=float(min_price))
        if max_price:
            if is_eligible(max_price):
                search_filter.append(Note.price<=float(max_price))

        if sort_by == "Rating":
            search_output = Note.query.filter(*search_filter).order_by(Note.avg_rating.desc()).all()

        elif sort_by == "Popularity":
            search_output = Note.query.filter(*search_filter).order_by(Note.rating_count.desc()).all()

        else:
            search_output = Note.query.filter(*search_filter).all()
    return render_template("search.html", user_id=user_id, watchlisted_note_ids=watchlisted_note_ids, cart_note_ids=cart_note_ids
                           , results = search_output, user_input = cleaned_input
                           , condition=condition, sort_by=sort_by, availability =availability, min_price=min_price, max_price=max_price) 
