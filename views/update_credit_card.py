from flask import Blueprint, render_template, url_for, session, flash
from pymongo import MongoClient
from ssl_decorators import ssl_required
import stripe
import config

blueprint = Blueprint('update_credit_card', __name__)

@blueprint.route('/update_credit_card', methods=['GET', 'POST'])
@ssl_required
def view():
    """
    This method is needed because the button name isn't populated in the form.
    """
    db = MongoClient().offTheGrid
    user = db.users.find({'username': session['username']})
    email = user[0]['email']
    customer = db.users.find({'username' : session['username']})
    customer = stripe.Customer.retrieve(customer[0]['customer_id'])
    card = customer.sources.create(source=request.form['stripeToken'])
    customer['default_source'] = card['id']
    flash("Credit card updated")
    return render_template('account.html', error=None, email=email,
                           publishable_key=config.STRIPE_PUBLISHABLE_KEY)
