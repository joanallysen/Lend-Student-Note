from flask import Blueprint, request, render_template, url_for, session, redirect
from models import db, Review
from datetime import datetime
import os

review_bp = Blueprint('review', __name__)

#TODO make login required
@review_bp.route('/add_review/<int:note_id>', methods=['POST', 'GET'])
def add_review(note_id):
    error = None

    if request.method == 'POST':
        new_review = Review(
            note_id = note_id,
            user_id = session['user_id'],
            star = request.form.get('star'),
            review = request.form.get('review'),
        )

        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('review_form.html')