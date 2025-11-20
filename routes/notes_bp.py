from flask import Blueprint, request, render_template, session, url_for, redirect, flash
from werkzeug.utils import secure_filename
from models import db, Note, Watchlist, CartItem
from datetime import datetime
from embedding_service import encode_note
import os

notes_bp = Blueprint('notes', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_image():
    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            return filename
    return ''

def update_image(note):
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            # delete old image if exist
            if note.image_filename:
                old_path = os.path.join(UPLOAD_FOLDER, note.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
                
            # save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            return filename
        
        # return old image if not changed
        return note.image_filename
                

    
# TODO MAKE LOGIN REQUIRED
@notes_bp.route('/add_note', methods=['POST', 'GET'])
def add_note():
    error = None

    if request.method =='POST':
        available_date= request.form.get('available_date')
        if  available_date:
            # flash('Please enter the available date!')
            # return redirect(url_for)
            new_note = Note(
                image_filename = add_image(),
                title=request.form.get('title'),
                isbn=request.form.get('isbn'),
                price = request.form.get('price') or -1,
                price_sale = request.form.get('price_sale') or -1,
                description = request.form.get('description'),
                condition = request.form.get('condition'),
                pickup_location = request.form.get('pickup_location'),
                available_date=  datetime.strptime(available_date, '%Y-%m-%d').date(),
                status = 'AVAILABLE',
                
                listing_type = request.form.get('listing_type'),
                # listing date just default value
                owner_id = session['user_id'],
                buyer_id = None,
                tags= request.form.get('tags'),
                embedding = encode_note(title=request.form.get('title'), description=request.form.get('description'), tags=request.form.get('tags'))
            )   

            # try: TODO WILL ADD THE EXCEPTION BACK THIS IS FOR ERROR DEBUGGING
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
    if note.owner_id != session['user_id']:
        return 'Error : You do not have access to edit that book :('
    
    if request.method =='POST':
        note.image_filename = update_image(note)
        note.title = request.form.get('title')
        note.isbn = request.form.get('isbn')
        note.price = request.form.get('price') or -1
        note.price_sale = request.form.get('price_sale') or -1
        note.description = request.form.get('description')
        note.condition = request.form.get('condition')
        note.pickup_location = request.form.get('pickup_location')
        note.available_date = datetime.strptime(request.form.get('available_date'), '%Y-%m-%d').date()
        note.listing_type = request.form.get('listing_type')
        note.embedding = encode_note(title=request.form.get('title'), description=request.form.get('description'), tags=request.form.get('tags'))
        note.tags = request.form.get('tags')
        
        if request.form.get('status'):
            note.status = request.form.get('status')
        
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('preview.html', error=error, action='notes.update_note', note=note)
     
@notes_bp.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.status == 'LENT':
        flash('Unable to delete! Note is currently lent!')
        return redirect(url_for('dashboard'))
    
    note.status = 'DELETED'

    note_watchlisted = Watchlist.query.filter(Watchlist.note_id ==  note.note_id).all()
    for w in note_watchlisted:
        db.session.delete(w)

    note_cartitem = CartItem.query.filter(CartItem.note_id==note.note_id).all()
    for c in note_cartitem:
        db.session.delete(c)
    
    
    db.session.commit()
    flash('Note successfully deleted!', 'success')
    return redirect(url_for('dashboard'))