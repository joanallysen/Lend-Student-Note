from flask import Blueprint, request, render_template, url_for, session, redirect
from models import db, Review, Note, History
from datetime import datetime
from sqlalchemy import and_
import os

review_bp = Blueprint('review', __name__)

#TODO make login required
@review_bp.route('/add_review/<int:note_id>', methods=['POST', 'GET'])
def add_review(note_id):
    
    note = Note.query.get_or_404(note_id)
    user_history= History.query.filter(and_(History.user_id==session['user_id'],History.note_id == note_id)).first()

    #Checking if user has bought/borrowed the note
    if not user_history:
        return 'Error, user_id does not match buyer_id please try again.'

    if request.method == 'POST':
        new_review = Review(
            note_id = note_id,
            user_id = session['user_id'],
            star = request.form.get('star'),
            review = request.form.get('review'),
            added_at = datetime.today().date()
        )

        db.session.add(new_review)

        total_star= sum(int(review.star) for review in note.reviews)
        total_reviews = len(note.reviews)
        note.avg_rating = total_star/total_reviews

        db.session.commit()
        return redirect(url_for('detail',note_id = note_id))
    return render_template('review_form.html')

#try to change by getting review id
@review_bp.route('/delete_review/<int:review_id>', methods=["POST"])
def delete_review(review_id):
    review = Review.query.filter(and_(Review.review_id==review_id,Review.user_id==session['user_id'])).first()
    
    if not review:
        return 'It is not your review'
    
    if request.method == "POST":
  
        if review:
            db.session.delete(review)
            db.session.commit()
      
    return redirect(url_for('detail',note_id = review.note_id))

@review_bp.route('/edit_review/<int:review_id>',methods=["POST"])
def edit_review(review_id):
    
    review = Review.query.filter(and_(Review.review_id==review_id,Review.user_id==session['user_id'])).first()
    
    if not review:
        return 'It is not your review'
    
    if request.method == "POST":
        review.review = request.form["edited_review"]
        review.star = request.form["star"]
        db.session.commit()
    return redirect(url_for('detail',note_id = review.note_id))
        