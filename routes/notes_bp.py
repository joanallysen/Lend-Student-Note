from flask import Blueprint, request, render_template, session, url_for, redirect
from models import db, Note
from datetime import datetime

notes_bp = Blueprint('notes', __name__)

# TODO MAKE LOGIN REQUIRED
@notes_bp.route('/add_note', methods=['POST', 'GET'])
def add_note():
    error = None
    if request.method =='POST':
        new_note = Note(
            title=request.form.get('title'),
            isbn=request.form.get('isbn'),
            price = request.form.get('price'),
            description = request.form.get('description'),
            condition = request.form.get('condition'),
            pickup_location = request.form.get('pickup_location'),
            available_date = datetime.strptime(request.form.get('available_date'), '%Y-%m-%d').date(),
            is_available = True,
            is_lend = request.form.get('is_lend') == 'lend',
            lender_id = session['user_id'],
            lended_to_id = None
        )

        # try:
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('dashboard'))
        # except:
        #     db.session.rollback()
        #     error = 'Failed to add to database, please try again...'
        #     return render_template('preview.html', error=error, action='notes.add_note', note=None)
        
    return render_template('preview.html', error=error, action='notes.add_note', note=None)


@notes_bp.route('/update_note/<int:note_id>', methods=['GET', 'POST'])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)

    error = None
    if note.lender_id != session['user_id']:
        return 'Error : You do not have access to edit that book :('
    
    if request.method =='POST':
        note.title = request.form['title']
        note.isbn = request.form['isbn']
        note.price = request.form['price']
        note.description = request.form['description']
        note.condition = request.form['condition']
        note.pickup_location = request.form['pickup_location']
        note.available_date = datetime.strptime(request.form['available_date'], '%Y-%m-%d').date()

        db.session.commit()
        return redirect(url_for('dashboard'))

        
    return render_template('preview.html', error=error, action=url_for('notes.update_note'))
     
@notes_bp.route('/delete_note')
def delete_note():
    pass