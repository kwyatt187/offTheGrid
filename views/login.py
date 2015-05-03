from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from pymongo import MongoClient
from ssl_decorators import ssl_required
import stripe
import config

stripe.api_key = config.STRIPE_SECRET_KEY
blueprint = Blueprint('login',__name__)

@blueprint.route('/login', methods=['GET', 'POST'])
@ssl_required
def view():
    error = None
    if request.method == 'POST':
        db = MongoClient().offTheGrid
        user = db.users.find({'username' : request.form['username']})

        if user.count() == 0:
            error = "Invalid username"
            return render_template('login.html', error=error)
        elif user[0]['password'] != request.form['password']:
            error = "Invalid  password"
            return render_template('login.html', error=error)
        elif user[0]['status'] == 'cancelled':
            error = "Subscription for this account has been cancelled."
            return render_template('login.html', error=error)
        elif user[0]['status'] == 'unverified':
            error = "Please click the link in your email to verify your account."
            return render_template('login.html', error=error)
        else:
            customer = stripe.Customer.retrieve(user[0]['customer_id'])
            status = customer['subscriptions']['data'][0]['status']

            if status.rstrip() == 'past_due':
                error = "There was an issue with your last payment. Please update payment information."
                session['logged_in'] = True
                session['username'] = request.form['username']
                return render_template('account.html', error=error, email=user[0]['email'])
            else:
                session['account_current'] = True
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("Welcome to the after party.")
                return redirect(url_for('after_party.view'))
    else:
        return render_template('login.html', error=error)
