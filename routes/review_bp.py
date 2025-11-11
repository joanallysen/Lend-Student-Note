from flask import Blueprint, request, render_template, url_for, session, redirect
from models import db, Review, Note, History
from datetime import datetime
from sqlalchemy import and_
import os

from utility import login_required
review_bp = Blueprint('review', __name__)

#TODO make login required
@review_bp.route('/add_review/<int:note_id>', methods=['POST', 'GET'])
@login_required
def add_review(note_id):
    note = Note.query.get_or_404(note_id)
    user_history= History.query.filter(and_(History.buyer_id==session['user_id'],History.note_id == note_id)).first()

    #Checking if user has bought/borrowed the note
    if not user_history:
        return 'Error, user_id does not match buyer_id please try again.'

    if request.method == 'POST':
        new_review = Review(
            note_id = note_id,
            user_id = session['user_id'],
            star = request.form.get('star'),
            review = request.form.get('review'),
        )

        # will automatically link to note.reviews too.
        db.session.add(new_review)
        note.rating_count += 1
        update_avg_rating(note)

        note.owner.rating_count += 1
        update_seller_avg_rating(note.owner)
 
        db.session.commit()
        return redirect(url_for('detail',note_id = note_id))
    return render_template('review_form.html')

#try to change by getting review id
@review_bp.route('/delete_review/<int:review_id>', methods=["POST"])
def delete_review(review_id):
    review = Review.query.filter(and_(Review.review_id==review_id,Review.user_id==session['user_id'])).first()
    
    if not review:
        return 'It is not your review'
    
    note_id = review.note_id

    if request.method == "POST":
        if review:
            review.note.rating_count -= 1
            review.note.owner.rating_count -= 1
            update_avg_rating(review.note)
            update_seller_avg_rating(review.note.owner)
            db.session.delete(review)
            db.session.commit()
      
    return redirect(url_for('detail', note_id = note_id))

# con, needing to recalculate every review star every edit.
@review_bp.route('/edit_review/<int:review_id>',methods=["POST"])
def edit_review(review_id):
    
    review = Review.query.filter(and_(Review.review_id==review_id,Review.user_id==session['user_id'])).first()
    
    if not review:
        return 'It is not your review'
    
    if request.method == "POST":
        review.review = request.form["edited_review"]
        review.star = request.form["star"]
        update_avg_rating(review.note)
        update_seller_avg_rating(review.note.owner)
        db.session.commit()
    return redirect(url_for('detail',note_id = review.note_id))

def update_avg_rating(model): # nvm, if user it will show the review that we do to other people not people to us.
    if model.rating_count == 0:
        model.avg_rating = 0
    else:
        total_star = sum(int(review.star) for review in model.reviews)
        model.avg_rating = total_star / model.rating_count

# rather than this, how about using memory, so less cost intensive, probably for future development
def update_seller_avg_rating(owner):
    if owner.rating_count == 0:
        owner.avg_rating = 0
    else:
        # each note has its own avg_rating, sum them all up and get the avg
        total_avg = 0
        for note in owner.notes_owned:
            total_avg += note.avg_rating or 0

        # only count the average with notes that has a rating on them (unrated note doesnt count)
        rated_notes = len([note for note in owner.notes_owned if note.rating_count >= 1])
        owner.avg_rating = total_avg / rated_notes
        