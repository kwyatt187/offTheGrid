from flask import Blueprint, render_template, redirect, url_for, flash
from pymongo import MongoClient
from time import mktime, localtime
from ssl_decorators import no_ssl_required
import stripe
import config

stripe.api_key = config.STRIPE_SECRET_KEY
blueprint = Blueprint('verify', __name__)

def add_subscriber(token, email, plan):
    try:
        customer = stripe.Customer.create(source=token, email=email, plan=plan)
        return customer, None
    except stripe.error.CardError, e:
        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err  = body['error']

        return (None, err['message'])
    except stripe.error.InvalidRequestError, e:
        # Invalid parameters were supplied to Stripe's API
        pass
    except stripe.error.AuthenticationError, e:
        pass
    
@blueprint.route('/verify/<token>')
@no_ssl_required
def view(token):
    db = MongoClient().offTheGrid
    user = db.users.find({'token': token})
    if user.count == 0 or user[0]['status'] in ['cancelled', 'verified']:
        error = "Invalid account verification link"
        return render_template('login.html', error=error)
    else:
        customer, error = add_subscriber(token, user[0]['email'], "afterparty")
        if error:
            return render_template('login.html', error=error)
        else:
            db.users.update({'token' : user[0]['token']},
                            {'$set' : {'customer_id' : customer['id'],
                                       'status' : 'verified',
                                       'verified_on' : mktime(localtime())}})
            flash('Account activated.')
            return redirect(url_for('login.view'))
