from flask import Blueprint, request, render_template, session, url_for, redirect, flash
from werkzeug.utils import secure_filename
from models import db, Note, Tag
from datetime import datetime
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
        new_note = Note(
            image_filename = add_image(),
            title=request.form.get('title'),
            isbn=request.form.get('isbn'),
            price = request.form.get('price'),
            price_sale = request.form.get('price_sale'),
            description = request.form.get('description'),
            condition = request.form.get('condition'),
            pickup_location = request.form.get('pickup_location'),
            available_date = datetime.strptime(request.form.get('available_date'), '%Y-%m-%d').date(),
            status = 'AVAILABLE',
            
            listing_type = request.form.get('listing_type'),
            # listing date just default value
            owner_id = session['user_id'],
            buyer_id = None
        )
        #Adding Tags
        tags = request.form.get('tags','')
        if tags:
                new_note.tags = clean_tags(tags)


        # try: TODO WILL ADD THE EXCEPTION BACK THIS IS FOR ERROR DEBUGGING
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('dashboard'))
        # except:
        #     db.session.rollback()
        #     error = 'Failed to add to database, please try again...'
        #     return render_template('preview.html', error=error, action='notes.add_note', note=None)
        
    return render_template('preview.html', error=error, action='notes.add_note', note=None)

def clean_tags(tags):
    cleaned_tags= [tag.strip().title() for tag in tags.split(',') if tag.strip()]

    
    #Remove duplicate iin the list of strings
    cleaned_tags = list(set(cleaned_tags))

    #List of tags
    tags_list=[]
    for tag in cleaned_tags:

        #Check if tag exists in the tag pool
        existing_tag = Tag.query.filter(Tag.name==tag).first()

        if not existing_tag:
            existing_tag = Tag(name=tag)
            db.session.add(existing_tag)
            

        tags_list.append(existing_tag)

        
    return tags_list

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
        note.price = request.form.get('price')
        note.price_sale = request.form.get('price_sale')
        note.description = request.form.get('description')
        note.condition = request.form.get('condition')
        note.pickup_location = request.form.get('pickup_location')
        note.available_date = datetime.strptime(request.form.get('available_date'), '%Y-%m-%d').date()
        note.listing_type = request.form.get('listing_type')
        
        if request.form.get('status'):
            note.status = request.form.get('status')
        
        tags = request.form.get('tags','')

        note.tags = clean_tags(tags)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('preview.html', error=error, action='notes.update_note', note=note)
     
@notes_bp.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    db.session.delete(note)
    db.session.commit()
    flash('Note successfully deleted!', 'success')
    return redirect(url_for('dashboard'))