from flask import Blueprint, render_template
from ssl_decorators import no_ssl_required
from pymongo import MongoClient

blueprint = Blueprint('events', __name__)

def get_todays_events():
    return []

def get_tomorrows_events():
    return []

def get_this_weeks_events():
    return []

def get_this_months_events():
    return []

@blueprint.route('/events')
@no_ssl_required
def view():
    return render_template('events.html',
                           todays_events=get_todays_events(),
                           tomorrows_events=get_tomorrows_events(),
                           this_weeks_events=get_this_weeks_events(),
                           this_months_events=get_this_months_events())
