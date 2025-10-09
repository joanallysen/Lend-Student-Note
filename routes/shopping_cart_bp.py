from flask import Flask, Blueprint, render_template, url_for, redirect, session, request
from models import db, Cart, Cart_Item, Note

shopping_cart = Blueprint('shopping_cart',__name__)

@shopping_cart.route('/shopping_cart')
def cart():
    all_notes = Note.query.all()

    return render_template('shopping_cart.html',notes=all_notes)

@shopping_cart.route('/add_to_cart', methods=["GET"])
def add_to_cart():
    note_id = request.args.get('note_id', type=int)
    user_id = session.get('user_id')

    #Check if user cart exist
    user_cart=Cart.query.filter_by(user_id = user_id).first()
    if not user_cart:
        new_cart = Cart(user_id = user_id)
        user_cart = new_cart

        db.session.add(new_cart)
        db.session.commit()

    #Check if the note is already in the cart or not
    item_exist= Cart_Item.query.filter(Cart.cart_id == user_cart.cart_id, note_id == note_id ).first()
    if item_exist:
        item_exist.quantity += 1
    else:
        new_item=Cart_Item(cart_id = user_cart.cart_id, note_id= note_id, quantity=1 )
        db.session.add(item_exist)
    
    db.session.commit()
    return redirect(url_for('shopping_cart.cart'))
