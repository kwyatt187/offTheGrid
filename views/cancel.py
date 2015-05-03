from flask import Blueprint, redirect, request, url_for, session, flash
from pymongo import MongoClient
from ssl_decorators import no_ssl_required
import stripe
import config

stripe.api_key = config.STRIPE_SECRET_KEY
blueprint = Blueprint('cancel', __name__)

@blueprint.route('/cancel_subscription', methods=['GET','POST'])
@no_ssl_required
def view():
    db = MongoClient().offTheGrid
    user = db.users.find_one({'username' : session['username']})
    customer = stripe.Customer.retrieve(user['customer_id'])
    customer.delete()
    db.users.update({'username' : session['username']},
                    {'$set' : {'status' : 'cancelled'}})
    flash("Subscription cancelled")
    return redirect(url_for('logout.view'))
