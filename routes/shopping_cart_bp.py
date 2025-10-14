from flask import Flask, Blueprint, render_template, url_for, redirect, session, request
from models import db, Cart, CartItem, Note, BorrowedBook
from datetime import datetime

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

    return render_template('user_cart.html', items=cart_items, total_price=total_price)


@shopping_cart.route('/add_to_cart/<int:note_id>', methods=['POST'])
def add_to_cart(note_id):
    if request.method == 'POST':
        user_id = session.get('user_id')

        # check if user cart exist
        user_cart=Cart.query.filter_by(user_id = user_id).first()
        if not user_cart:
            new_cart = Cart(user_id = user_id)
            user_cart = new_cart

            db.session.add(new_cart)
            db.session.commit()

        # check if the note is already in the cart or not
        item_exist= CartItem.query.filter(CartItem.cart_id == user_cart.cart_id, CartItem.note_id == note_id ).first()
        if item_exist:
            item_exist.quantity += 1
            return redirect(url_for('shopping_cart.mall'))
          
        # adding new cart item
        buying_type = request.form.get('buying_type')
        new_item = None
        if buying_type == 'BORROW':
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            new_item = CartItem(cart_id = user_cart.cart_id, note_id=note_id, quantity=1, buying_type='BORROW', start_date=start_date, end_date=end_date)
        elif buying_type == 'BUY':
            new_item = CartItem(cart_id = user_cart.cart_id, note_id=note_id, quantity=1, buying_type='BUY')
            
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


@shopping_cart.route('/checkout', methods=['POST'])
def checkout():
    if request.method == 'POST':
        user_id = session.get('user_id')
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.items:
            return "Cart is empty"

        for item in cart.items:
            note = item.note_details
            
            if not note:
                continue
            
            if item.buying_type == 'BUY':
                note.status = 'SOLD'
                note.buyer_id = user_id
                db.session.add(note)
            
            elif item.buying_type == 'BORROW':
                if item.start_date and item.end_date:
                    # create borrowed book
                    borrowed_book = BorrowedBook(
                        note_id=item.note_id,
                        user_id=user_id,
                        start_date=item.start_date,
                        end_date=item.end_date
                    )
                    note.status = 'LENT'
                    db.session.add(borrowed_book)
                    db.session.add(note)
        
        # clear the cart
        cart_items = CartItem.query.filter_by(cart_id=cart.cart_id).delete()
        db.session.commit()
        
        return redirect(url_for('explore'))

