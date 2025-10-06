from flask import Blueprint, request, render_template

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/add_note')
def add_note():
    if request.method =='POST':
        title = request.form.get('title')
        price = request.form.get('price')
        description = request.form.get('description')
        condition = request.form.get('condition')
        pickup_location = request.form.get('pickup_location')
        available_date = request.form.get('available_date')
        is_available = True
        is_lend = request.form.get('is_lend')
        lender_id = ''
        lended_to_id = ''
        
    return render_template('preview.html')
    pass

@notes_bp.route('/display_note')
def display_note():
    pass

@notes_bp.route('/update_note')
def update_note():
    pass
    
@notes_bp.route('/delete_note')
def delete_note():
    pass