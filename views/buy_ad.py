from flask import Blueprint, render_template, redirect, url_for, request, flash
from pymongo import MongoClient
from ssl_decorators import no_ssl_required
from smtplib import SMTP
from email.mime.text import MIMEText

blueprint = Blueprint('buy_ad', __name__)

@blueprint.route('/buyad', methods=['GET','POST'])
@no_ssl_required
def view():
    if request.method == 'POST':
        ad_request = "Name: " + request.form['name'] + "\n"
        ad_request += "Phone number: " + request.form['phone'] + "\n"
        ad_request += "Location: " + request.form['location'] + "\n"
        ad_request += "Budget: " + request.form['budget'] + "\n"
        ad_request += "Ad type: " + request.form['adtype'] + "\n"

        msg = MIMEText(ad_request)
        msg['Subject'] = "Ad request"
        msg['From'] = "Off The Grid booking"
        msg['To'] = "kwyatt187@gmail.com"
        
        s = SMTP('localhost')
        s.sendmail("Off_The_Grid_booking@offthegridadvertising.com", ["kwyatt187@gmail.com"], msg.as_string())
        s.quit()
        flash('Ad request sent')
        return redirect(url_for('buy_ad.view'))
    else:
        db = MongoClient().offTheGrid
        locations = db.locations.find().sort([("name" , 1)])
        return render_template('buyad.html', locations=locations)
