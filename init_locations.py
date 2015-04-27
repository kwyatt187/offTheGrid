from time import sleep
from urllib import urlopen
from json import load
from pymongo import MongoClient
from  config import GOOGLE_API_KEY

def init_locations():
    client = MongoClient()
    db = client["offTheGrid"]
    db.locations.drop()
    with open('static/locations') as locations_file:
        for location in locations_file:
            if ":" not in location:
                continue
            name, address = location.rstrip().split(":")
            google_api = "https://maps.googleapis.com/maps/api/geocode/json?address="+address+"&key="+GOOGLE_API_KEY
            print google_api
            location_geodecode = load(urlopen(google_api))
            lat = float(location_geodecode["results"][0]["geometry"]["location"]["lat"])
            lng = float(location_geodecode["results"][0]["geometry"]["location"]["lng"])
            formatted_address = location_geodecode["results"][0]["formatted_address"]
            sleep(1)
            db.locations.update({"name" : name},{"name" : name, "address": formatted_address, "lat" : lat, "lng" : lng}, True)

if __name__ == "__main__":
    init_locations()
