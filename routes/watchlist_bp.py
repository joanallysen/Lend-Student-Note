from flask import Blueprint, session, redirect, url_for, flash
from models import db, Watchlist

watchlist_bp = Blueprint('watchlist', __name__)

# TODO need login
@watchlist_bp.route('/add_watchlist/<int:note_id>', methods=['POST'])
def add_watchlist(note_id):
    user_id = session.get('user_id')

    exist = Watchlist.query.filter_by(user_id=user_id, note_id=note_id).first()
    # hardly possible but what can you expect
    if not exist:
        flash('Already on watchlist!', 'error')

    new_watchlist = Watchlist(user_id=user_id, note_id=note_id)
    db.session.add(new_watchlist)
    db.session.commit()
    return redirect(url_for('explore'))

@watchlist_bp.route('/remove_watchlist/<int:note_id>', methods=['POST'])
def remove_watchlist(note_id):
    user_id = session.get('user_id')
    watchlist_item = Watchlist.query.filter_by(user_id=user_id, note_id=note_id).first_or_404()
    
    db.session.delete(watchlist_item)
    db.session.commit()
    flash('Watchlist successfully deleted!', 'success')
    return redirect(url_for('watchlist'))
    


