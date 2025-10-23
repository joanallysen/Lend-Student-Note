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


@borrowed_bp.route('/confirmed_returned/<int:note_id>', methods=['POST'])
def confirmed_returned(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Update history if it exists
    if note.current_history_id:
        history = History.query.get(note.current_history_id)
        if history:
            history.transaction_date = datetime.now()
    
    note.status = 'HIDDEN'
    note.buyer_id = None
    note.current_history_id = None

    db.session.commit()
    return f"{history.note.title} successfully returned! Deposit money will be returned to buyer. By default book / note is set to hidden, You can update to available if you want to lend again<a href='/dashboard'>Return to dashboard</a>"


