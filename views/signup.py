from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from pymongo import MongoClient
from smtplib import SMTP
from email.mime.text import MIMEText
from ssl_decorators import ssl_required
import stripe
import config

stripe.api_key = config.STRIPE_SECRET_KEY
blueprint = Blueprint('signup', __name__)

@blueprint.route('/signup', methods=['GET', 'POST'])
@ssl_required
def view():
    error = None
    fee = 2
    cents = fee*100
    if request.method == 'POST':
        db = MongoClient().offTheGrid
        user = db.users.find({'username' : request.form['username']})
        email = db.users.find({'email' : request.form['email']})
        if user.count() > 0:
            error = "Username already exists."
            return render_template('signup.html', error=error,
                                   publishable_key=config.STRIPE_PUBLISHABLE_KEY,
                                   cents=cents, fee=fee)

        elif request.form['password1'] != request.form['password2']:
            error = "Passwords do not match."
            return render_template('signup.html', error=error,
                                   publishable_key=config.STRIPE_PUBLISHABLE_KEY,
                                   cents=cents, fee=fee)

        elif email.count() > 0:
            error = "Email address "+request.form['email']+" has already been used."
            return render_template('signup.html', error=error,
                                   publishable_key=config.STRIPE_PUBLISHABLE_KEY,
                                   cents=cents, fee=fee)

        else:
            verification = "Click the link below to activate your account\n"
            verification = "http://offthegridadvertising.com/verify/"+request.form['stripeToken']
            
            msg = MIMEText(verification)
            msg['Subject'] = "Email verification"
            msg['From'] = "Off The Grid Advertising"
            msg['To'] = request.form['email']
                
            s = SMTP('localhost')
            try:
                s.sendmail("Off_The_Grid@offthegridadvertising.com", [request.form['email']], msg.as_string())
                s.quit()
                db.users.insert({'username' : request.form['username'],
                                 'password' : request.form['password1'],
                                 'email' : request.form['email'],
                                 'token' : request.form['stripeToken'],
                                 'status' : 'unverified'})

            
                flash("An email has been sent to "+request.form['email']+". Click the link to activate your account")
            except Exception:
                flash("Unknown error sending email")

            return redirect(url_for('login.view'))
    else:
        return render_template('signup.html', error=error,
                               publishable_key=config.STRIPE_PUBLISHABLE_KEY,
                               cents=cents, fee=fee)
