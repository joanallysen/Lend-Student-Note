from flask import Blueprint, request, render_template, session, url_for, redirect
from models import db, Note, History, CartItem
from datetime import datetime

borrowed_bp = Blueprint('borrowed', __name__)

@borrowed_bp.route('/show_borrowed')
def show_borrowed(): 
    user_id = session['user_id']
    borrowed_notes = Note.query.filter_by(buyer_id=user_id).all()
    return render_template('borrowed.html', borrowed_notes=borrowed_notes)

# accessed only by buyer
@borrowed_bp.route('/return_borrowed/<int:note_id>', methods=['POST'])
def return_borrowed(note_id):
    user_id = session['user_id']
    borrowed_note = Note.query.filter_by(buyer_id=user_id, note_id=note_id).first()
    borrowed_note.status = 'NEED ACTION'
    db.session.commit()
    return f"{borrowed_note.title} sucessfully tagged as returned! Please wait for lender respond <a href='/show_borrowed'>Return to borrowed note/book page</a>"

# accessed only by owner
@borrowed_bp.route('/confirmed_returned/<int:note_id>', methods=['POST'])
def confirmed_returned(note_id):
    user_id = session['user_id']
    borrowed_note = Note.query.filter_by(owner_id=user_id, note_id=note_id).first()

    if not borrowed_note or not borrowed_note.buyer_id:
        return 'Note not found or not currently borrowed', 404
    
    cart_item = CartItem.query.filter_by(note_id = note_id, buying_type='BORROW').first()
    print(f'Getting cart item : {cart_item}')

    # edit history that was borrowed

    borrowed_history = History.query.filter_by(note_id=note_id, user_id=borrowed_note.buyer_id).first()
    if not borrowed_history:
        return 'Borrowed history not found', 404
    
    borrowed_history.transaction_date = db.func.now()
    borrowed_note.status = 'HIDDEN'
    borrowed_note.buyer_id = None

    db.session.commit()
    return f"{borrowed_note.title} successfully returned! Deposit money will be returned to buyer. By default book / note is set to hidden, You can update to available if you want to lend again<a href='/dashboard'>Return to dashboard</a>"