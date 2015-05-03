from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from bson.objectid import ObjectId
from pymongo import MongoClient
from ssl_decorators import no_ssl_required

blueprint = Blueprint('edit_after_parties', __name__)

@blueprint.route('/myafterparties', methods=['GET', 'POST'])
@no_ssl_required
def view():
    if not session.get('account_current'):
        return redirect(url_for('login.view'))
    else:
        db = MongoClient().offTheGrid
        if request.method == 'POST':
            success_message = ""
            if 'update' in request.form:
                db.afterparties.update({ '_id' : ObjectId(request.form['_id']),
                                         'submittedby' : session['username'] },
                                       { 'location' : request.form['location'],
                                         'date' : request.form['date'],
                                         'description' : request.form['description'],
                                         'submittedby' : session['username']},
                                       upsert=True  )
                success_message = "After party updated."
                                             
            elif 'delete' in request.form:
                db.afterparties.remove({ '_id' : ObjectId(request.form['_id']) ,
                                         'submittedby' : session['username'] })
                success_message = "After party deleted."

            flash(success_message)
            return redirect(url_for('edit_after_parties.view'))
        else:
            afterparties = db.afterparties.find({'submittedby' : session['username']}).sort([( '_id', -1)])
            return render_template('myafterparties.html', afterparties=afterparties)
