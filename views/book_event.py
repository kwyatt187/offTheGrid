from flask import Blueprint, render_template, redirect, url_for, request, flash
from pymongo import MongoClient
from ssl_decorators import no_ssl_required
from smtplib import SMTP
from email.mime.text import MIMEText

blueprint = Blueprint('book_event', __name__)

@blueprint.route('/bookevent', methods=['GET','POST'])
@no_ssl_required
def view():
    if request.method == 'POST':
        book_request = "Name: " + request.form['name'] + "\n"
        book_request += "Phone number: " + request.form['phone'] + "\n"
        book_request += "Reason: " + request.form['reason'] + "\n"
        book_request += "Location: " + request.form['location'] + "\n"
        book_request += "Secrecy level: " + request.form['secrecylevel'] + "\n"
        book_request += "Number of people: " + request.form['numpeople'] + "\n"
        book_request += "Budget: " + request.form['budget']

        msg = MIMEText(book_request)
        msg['Subject'] = "Booking request"
        msg['From'] = "Off The Grid booking"
        msg['To'] = "kwyatt187@gmail.com"
        
        s = SMTP('localhost')
        s.sendmail("Off_The_Grid_booking@offthegridadvertising.com", ["kwyatt187@gmail.com"], msg.as_string())
        s.quit()
        flash('Booking request sent')
        return redirect(url_for('book_event.view'))
    else:
        db = MongoClient().offTheGrid
        locations = db.locations.find().sort([("name" , 1)])
        return render_template('bookevent.html', locations=locations)
