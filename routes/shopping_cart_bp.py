from flask import Flask, Blueprint, render_template, url_for, redirect, session, request
from models import db, Cart, CartItem, Note

shopping_cart = Blueprint('shopping_cart',__name__)

@shopping_cart.route('/mall')
def cart():
    all_notes = Note.query.all()

    return render_template('mall.html',notes=all_notes)

@shopping_cart.route('/add_to_cart/<string:note_id>', methods=["GET"])
def add_to_cart(note_id):
    
    user_id = session.get('user_id')

    #Check if user cart exist
    user_cart=Cart.query.filter_by(user_id = user_id).first()
    if not user_cart:
        new_cart = Cart(user_id = user_id)
        user_cart = new_cart

        db.session.add(new_cart)
        db.session.commit()

    #Check if the note is already in the cart or not
    item_exist= CartItem.query.filter(CartItem.cart_id == user_cart.cart_id, CartItem.note_id == note_id ).first()
    if item_exist:
        item_exist.quantity += 1
    else:
        new_item=CartItem(cart_id = user_cart.cart_id, note_id= note_id, quantity=1 )
        db.session.add(new_item)
    
    db.session.commit()
    return redirect(url_for('shopping_cart.cart'))

@shopping_cart.route('/user_cart')
def user_cart():
    user_id= session.get('user_id')
    
    cart_exist = Cart.query.filter(Cart.user_id == user_id).first()

    if cart_exist:
        content= cart_exist.items
    else:
        content="Nothing"

    return render_template('user_cart.html', items = content)