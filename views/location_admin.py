from flask import Blueprint, request, redirect, session, render_template, url_for
from pymongo import MongoClient
from time import sleep
from urllib import urlopen
from json import load
from ssl_decorators import no_ssl_required

blueprint = Blueprint('location_admin', __name__)
db = MongoClient().offTheGrid;

def add_location(name, address):
    google_api = "https://maps.googleapis.com/maps/api/geocode/json?address="+address
    location_geodecode = load(urlopen(google_api))
    lat = float(location_geodecode["results"][0]["geometry"]["location"]["lat"])
    lng = float(location_geodecode["results"][0]["geometry"]["location"]["lng"])
    formatted_address = location_geodecode["results"][0]["formatted_address"]
    db.locations.update({"name" : name},{"name" : name, "address": formatted_address, "lat" : lat, "lng" : lng}, True)
    sleep(1) # We don't want to exceed the quota for API calls

@blueprint.route('/location_admin', methods=['GET','POST'])
@no_ssl_required
def view():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.view'))
    else:
        if request.method == 'POST':
            submitted_locations = request.form['locations'].split('\n')
            new_locations = []
            for location in submitted_locations:
                if ':' not in location:
                    continue
                name, address = location.split(':')
                add_location(name, address)
            return redirect(url_for('location_admin.view'))
        else:
            locations = db.locations.find().sort([('name', 1)])
            locations_string = ""
            for location in locations:
                locations_string += location['name']+":"+location['address']+"\n"
                
            return render_template('edit_locations.html', locations=locations_string)

