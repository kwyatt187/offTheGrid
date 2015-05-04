from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from pymongo import MongoClient
from ssl_decorators import no_ssl_required

blueprint = Blueprint('admin_login',__name__)

@blueprint.route('/admin', methods=['GET', 'POST'])
@no_ssl_required
def view():
    error = None
    if request.method == 'POST':
        db = MongoClient().offTheGrid
        user = db.users.find({'username' : request.form['username']})
        
        if user.count() == 0:
            error = "Invalid username"
            return render_template('admin_login.html', error=error)
        elif user[0]['password'] != request.form['password']:
            error = "Invalid  password"
            return render_template('admin_login.html', error=error)
        elif 'admin' not in user[0]:
            error = "Username "+request.form['username']+" is not an administrator"
            return render_template('admin_login.html', error=error)
        else:
            session['admin_logged_in'] = True
            session['logged_in'] = True
            session['username'] = request.form['username']
            return render_template('admin_home.html')
    else:
        return render_template('admin_login.html', error=error)
