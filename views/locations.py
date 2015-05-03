from flask import Blueprint, render_template
from pymongo import MongoClient
from ssl_decorators import no_ssl_required

blueprint = Blueprint('locations', __name__)

@blueprint.route('/locations')
@no_ssl_required
def view():
    # This is undesirable, but necessary to go over the same list in the template
    db = MongoClient().offTheGrid
    locations_for_map = db.locations.find().sort([("name", 1)])
    locations_list = db.locations.find().sort([("name", 1)])
    return render_template('locations.html', 
                           locations_for_map=locations_for_map,
                           locations_list=locations_list,)
