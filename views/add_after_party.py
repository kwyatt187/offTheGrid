from flask import Blueprint, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from ssl_decorators import no_ssl_required

blueprint = Blueprint('add_after_party', __name__)

@blueprint.route('/addafterparty', methods=['GET', 'POST'])
@no_ssl_required
def view():
    if not session.get('account_current'):
        return redirect(url_for('login.view'))
    else:
        if request.method == 'POST':
            db = MongoClient().offTheGrid
            db.afterparties.insert({'location': request.form['location'],
                                    'date': request.form['date'],
                                    'description': request.form['description'],
                                    'submittedby': session['username']})
            return redirect(url_for('after_party.view'))
        else:
            return render_template('addafterparty.html')
