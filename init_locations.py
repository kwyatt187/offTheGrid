from time import sleep
from urllib import urlopen
from json import load
from pymongo import MongoClient
from  config import GOOGLE_API_KEY

client = MongoClient()
db = client["offTheGrid"]

def add_location(name, address):
    google_api = "https://maps.googleapis.com/maps/api/geocode/json?address="+address+"&key="+GOOGLE_API_KEY
    print google_api
    location_geodecode = load(urlopen(google_api))
    lat = float(location_geodecode["results"][0]["geometry"]["location"]["lat"])
    lng = float(location_geodecode["results"][0]["geometry"]["location"]["lng"])
    formatted_address = location_geodecode["results"][0]["formatted_address"]
    db.locations.update({"name" : name},{"name" : name, "address": formatted_address, "lat" : lat, "lng" : lng}, True)
    sleep(1) # We don't want to exceed the quota for API calls

if __name__ == "__main__":
    db.locations.drop()
    with open('static/locations') as locations_file:
        for location in locations_file:
            if ":" not in location:
                continue
            name, address = location.rstrip().split(":")
            add_location(name, address)
