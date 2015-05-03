from flask import Blueprint, render_template, redirect, url_for, session
from pymongo import MongoClient
from ssl_decorators import no_ssl_required

blueprint = Blueprint('after_party',__name__)

@blueprint.route('/afterparty')
@no_ssl_required
def view():
    if not session.get('account_current'):
        return redirect(url_for('login.view'))
    else:
        db = MongoClient().offTheGrid
        afterparties = db.afterparties.find().sort([( '_id', -1)])
        return render_template('afterparty.html', afterparties=afterparties)
