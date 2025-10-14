from flask import Flask, Blueprint, render_template, url_for, redirect, session, request
from models import db, Cart, CartItem, Note

shopping_cart = Blueprint('shopping_cart',__name__)

@shopping_cart.route('/mall')
def mall():
    all_notes = Note.query.all()

    return render_template('mall.html',notes=all_notes)

@shopping_cart.route('/user_cart')
def user_cart():
    user_id= session.get('user_id')
    
    cart_exist = Cart.query.filter(Cart.user_id == user_id).first()

    if cart_exist:
        cart_items= cart_exist.items

        total_price = sum(item.note_details.price*item.quantity for item in cart_items)

    else:
        content="Nothing"

    return render_template('user_cart.html', items = cart_items, total_price=total_price)

# def total_bills(cart_items){
#     total_price
# }

@shopping_cart.route('/add_to_cart/<int:note_id>', methods=["GET"])
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
    return redirect(url_for('shopping_cart.mall'))

@shopping_cart.route('/add_quantity/<int:note_id>')
def add_quantity(note_id):
    user_id= session.get('user_id')
    user_cart = Cart.query.filter(Cart.user_id == user_id).first()
    user_cart_id = user_cart.cart_id

    #Search user item based on the note id
    selected_item = CartItem.query.filter(CartItem.cart_id == user_cart_id, CartItem.note_id == note_id).first()

    selected_item.quantity += 1

    db.session.commit()
    return redirect(url_for('shopping_cart.user_cart'))

@shopping_cart.route('/subtract_quantity/<int:note_id>')
def subtract_quantity(note_id):
    user_id= session.get('user_id')
    user_cart = Cart.query.filter(Cart.user_id == user_id).first()
    user_cart_id = user_cart.cart_id

    #Search user item based on the note id
    selected_item = CartItem.query.filter(CartItem.cart_id == user_cart_id, CartItem.note_id == note_id).first()

    selected_item.quantity -= 1

    if selected_item.quantity == 0:
        remove_item(note_id)

    db.session.commit()
    return redirect(url_for('shopping_cart.user_cart'))

@shopping_cart.route('/remove_item/<int:note_id>')
def remove_item(note_id):
    user_id = session.get('user_id')
    user_cart = Cart.query.filter(Cart.user_id == user_id).first()
    user_cart_id = user_cart.cart_id
    
    #Search user item based on the note id
    selected_item = CartItem.query.filter(CartItem.cart_id == user_cart_id, CartItem.note_id == note_id).first()
    db.session.delete(selected_item)
    db.session.commit()

    return redirect(url_for('shopping_cart.user_cart'))


# @shopping_cart.route('/checkout', methods=['POST'])
# def checkout():
#     if request.form == 'POST':
#         user_id = session.get('user_id')
#         cart_exist = Cart.query.filter(Cart.user_id == user_id).first()

#         if cart_exist:
#             cart_items = cart_exist.items
#         else:
#             cart_items = 'Nothing'

#         notes = list(set())
#         for item in cart_items:
#             notes.append(set(db.session.query(Note.note_id).all()))
        
#         for note in notes:
#             note.status = 
        
    
