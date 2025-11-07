from flask import Flask, Blueprint, render_template, url_for, redirect, session, request, render_template_string, flash
from models import db, Cart, CartItem, Note, History
from datetime import datetime

shopping_cart = Blueprint('shopping_cart',__name__)

def check_user_cart_exist():
    user_id= session.get('user_id')

    # check if user cart exist
    user_cart=Cart.query.filter_by(user_id = user_id).first()
    if not user_cart:
        print('User cart has not exist yet, making a new one.')
        new_cart = Cart(user_id = user_id)
        user_cart = new_cart

        db.session.add(new_cart)
        db.session.commit()
    
    print('User cart exist')
    return user_cart

@shopping_cart.route('/user_cart')
def user_cart():
    user_id= session.get('user_id')

    # check if user cart exist
    user_cart = check_user_cart_exist()

    #check if the cart is not empty
    if user_cart.items:
        cart_items= user_cart.items
        total_price = sum(item.note_details.price for item in cart_items)
        return render_template('user_cart.html', items=cart_items, total_price=total_price)
    else:
        cart_items=[]
        return render_template('user_cart.html', items=cart_items)


@shopping_cart.route('/add_to_cart/<int:note_id>', methods=['POST'])
def add_to_cart(note_id):
    if request.method == 'POST':
        user_id = session.get('user_id')

        # check if user cart exist
        user_cart = check_user_cart_exist()

        # check if the note is already in the cart or not
        item_exist= CartItem.query.filter(CartItem.cart_id == user_cart.cart_id, CartItem.note_id == note_id ).first()
        if item_exist:
            return render_template_string("""
                Item is already on cart! 
                <a href='{{ url_for('shopping_cart.user_cart') }}'>Go to your cart?</a> 
                <a href='{{ url_for('explore') }}'>Return to explore page</a>
            """)
          
        # adding new cart item
        buying_type = request.form.get('buying_type')
        total_price = request.form.get('total_price')
        new_item = None
        if buying_type == 'BORROW':
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            
            new_item = CartItem(cart_id = user_cart.cart_id, note_id=note_id, buying_type='BORROW', start_date=start_date, end_date=end_date, total_price=total_price)
        elif buying_type == 'BUY':
            new_item = CartItem(cart_id = user_cart.cart_id, note_id=note_id, buying_type='BUY', total_price=total_price)
            
        if new_item:
            db.session.add(new_item)
            db.session.commit()
            return render_template_string("""
                Item added to cart! 
                <a href='{{ url_for('shopping_cart.user_cart') }}'>Go to your cart?</a> 
                <a href='{{ url_for('explore') }}'>Return to explore page</a>
            """)


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

        new_history = None
        for item in cart.items:
            note = item.note_details
            
            if not note: continue
    
            if item.buying_type == 'BUY':
                note.status = 'SOLD'
                note.buyer_id = user_id
                
                db.session.add(note)
                new_history = History(
                    buyer_id = user_id,
                    owner_id = note.owner_id,
                    note_id = note.note_id,
                    transaction_type = item.buying_type,
                    transaction_date = datetime.now(),
                    total_price = item.total_price
                )
                db.session.add(new_history)
                
            elif item.buying_type == 'BORROW':
                if item.start_date and item.end_date:
                    note.status = 'LENT'
                    note.buyer_id = user_id
                    note.incoming_return_date = item.end_date

                    db.session.add(note)
                    new_history = History(
                        buyer_id = user_id,
                        owner_id = note.owner_id,
                        note_id = note.note_id,
                        transaction_type = item.buying_type,
                        borrow_start_date = datetime.now(),
                        transaction_date = None,
                        total_price = item.total_price
                    )

            db.session.add(new_history)
            db.session.flush()

            note.current_history_id = new_history.history_id
            note.buyer_id = user_id

        # delete the cart item
        CartItem.query.filter_by(cart_id=cart.cart_id).delete()
        db.session.commit()
        
        return render_template('successful.html')

