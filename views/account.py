from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from pymongo import MongoClient
from ssl_decorators import ssl_required
import stripe
import config

stripe.api_key = config.STRIPE_SECRET_KEY
blueprint = Blueprint('account', __name__)

@blueprint.route('/account', methods=['GET','POST'])
@ssl_required
def view():
    error = None

    if not session.get('logged_in'):
        return redirect(url_for('login.view'))
    else:
        db = MongoClient().offTheGrid
        user = db.users.find_one({'username': session['username']})
        email = user['email']
        
        if request.method == 'POST':
            for key in request.form:
                print key
            if 'update_email' in request.form:
                newemail = db.users.find({'email' : request.form['newemail']})
                if newemail.count() > 0:
                    error = "Email address "+request.form['newemail']+" is already in registered"
                else:
                    email = request.form['newemail']
                    db.users.update({'username' : session['username']},
                                          {'$set' : {'email' : email}})
                    flash("Email updated.")
                return render_template('account.html', error=error, email=email,
                                       publishable_key=config.STRIPE_PUBLISHABLE_KEY)

            elif 'update_password' in request.form:
                user = db.users.find({'username' : session['username']})
                                            
                if request.form['password1'] != request.form['password2']:
                    error = "New passwords do not match"
                else:
                    db.users.update({'username' : session['username']},
                                          {'$set' : {'password' : request.form['password1']}})
                    flash('Password updated')
                return render_template('account.html', error=error, email=email,
                                       publishable_key=config.STRIPE_PUBLISHABLE_KEY)

        else:
            return render_template('account.html', error=error, email=email,
                                   publishable_key=config.STRIPE_PUBLISHABLE_KEY)


