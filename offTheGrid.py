from urllib import urlopen
import smtplib
from email.mime.text import MIMEText
import os
import json
from functools import wraps
from flask import Flask, request, session, redirect, url_for, render_template, flash, current_app
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from contextlib import closing
import config

app = Flask(__name__)
app.config.from_object('config')
mongo = PyMongo(app)

def no_ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if request.is_secure:
            return redirect(request.url.replace("https://","http://"))
        return fn(*args, **kwargs)
    return decorated_view

def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("SSL"):
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://","https://"))
        return fn(*args, **kwargs)
    return decorated_view


@app.route('/')
@no_ssl_required
def home():
    os.chdir('/var/www/offTheGrid/static/home_images')
    scrolling_images = os.listdir('.')
    scrolling_images = ["home_images/"+img for img in scrolling_images]
    return render_template('home.html', scrolling_images=scrolling_images)

@app.route('/findlocations')
@no_ssl_required
def find_locations():
    # This is undesirable, but necessary to go over the same list in the template
    locations_for_map = mongo.db.locations.find().sort([("name", 1)])
    locations_list = mongo.db.locations.find().sort([("name", 1)])
    return render_template('findlocations.html', locations_for_map=locations_for_map,
                           locations_list=locations_list, key=config.GOOGLE_API_KEY)


@app.route('/buyad', methods=['GET','POST'])
@no_ssl_required
def buy_ad():
    if request.method == 'POST':
        ad_request = "Name: " + request.form['name'] + "\n"
        ad_request += "Phone number: " + request.form['phone'] + "\n"
        ad_request = "Location: " + request.form['location'] + "\n"
        ad_request += "Budget: " + request.form['budget'] + "\n"
        ad_request += "Ad type: " + request.form['adtype'] + "\n"

        msg = MIMEText(ad_request)
        msg['Subject'] = "Ad request"
        msg['From'] = "Off The Grid booking"
        msg['To'] = "kwyatt187@gmail.com"
        
        s = smtplib.SMTP('localhost')
        s.sendmail("Off_The_Grid_booking@offthegridadvertising.com", ["kwyatt187@gmail.com"], msg.as_string())
        s.quit()
        flash('Ad request sent')
        return redirect(url_for('buy_ad'))
    else:
        locations = mongo.db.locations.find().sort([("name" , 1)])
        return render_template('buyad.html', locations=locations)

@app.route('/bookevent', methods=['GET', 'POST'])
@no_ssl_required
def book_event():
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
        
        s = smtplib.SMTP('localhost')
        s.sendmail("Off_The_Grid_booking@offthegridadvertising.com", ["kwyatt187@gmail.com"], msg.as_string())
        s.quit()
        flash('Booking request sent')
        return redirect(url_for('book_event'))
    else:
        locations = mongo.db.locations.find().sort([("name" , 1)])
        return render_template('bookevent.html', locations=locations)

@app.route('/afterparty')
@no_ssl_required
def after_party():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        afterparties = mongo.db.afterparties.find().sort([( '_id', -1)])
        return render_template('afterparty.html', afterparties=afterparties)

@app.route('/addafterparty', methods=['GET', 'POST'])
@no_ssl_required
def add_after_party():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            mongo.db.afterparties.insert({'location': request.form['location'],
                                          'date': request.form['date'],
                                          'description': request.form['description'],
                                          'submittedby': session['username']})
            return redirect(url_for('after_party'))
        else:
            return render_template('addafterparty.html')

@app.route('/myafterparties', methods=['GET', 'POST'])
@no_ssl_required
def edit_after_parties():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            success_message = ""
            if 'update' in request.form:
                mongo.db.afterparties.update({ '_id' : ObjectId(request.form['_id']),
                                               'submittedby' : session['username'] },
                                             { 'location' : request.form['location'],
                                               'date' : request.form['date'],
                                               'description' : request.form['description'],
                                               'submittedby' : session['username']},
                                             upsert=True  )
                success_message = "After party updated."
                                             
            elif 'delete' in request.form:
                mongo.db.afterparties.remove({ '_id' : ObjectId(request.form['_id']) ,
                                               'submittedby' : session['username'] })
                success_message = "After party deleted."

            flash(success_message)
            return redirect(url_for('edit_after_parties'))
        else:
            afterparties = mongo.db.afterparties.find({'submittedby' : session['username']}).sort([( '_id', -1)])
            return render_template('myafterparties.html', afterparties=afterparties)
            
@app.route('/login', methods=['GET', 'POST'])
@ssl_required
def login():
    error = None
    if request.method == 'POST':
        user = mongo.db.users.find({'username' : request.form['username']})
        if user.count() == 0:
            error = "Invalid username"
            return render_template('login.html', error=error)
        elif user[0]['password'] != request.form['password']:
            error = "Invalid  password"
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('after_party'))
    else:
        return render_template('login.html', error=error)
        

@app.route('/logout')
@no_ssl_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
@ssl_required
def signup():
    error = None
    if request.method == 'POST':
        user = mongo.db.users.find({'username' : request.form['username']})
        email = mongo.db.users.find({'email' : request.form['email']})
        if user.count() > 0:
            error = "Username already exists"
            return render_template('signup.html', error=error)
        elif request.form['password1'] != request.form['password2']:
            error = "Passwords do not match"
            return render_template('signup.html', error=error)
        elif email.count() > 0:
            error = "A username with that email already exists"
            return render_template('signup.html', error=error)
        else:
            mongo.db.users.insert({'username' : request.form['username'],
                                   'password' : request.form['password1'],
                                   'email' : request.form['email']})

            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('after_party'))
    else:
        return render_template('signup.html', error=error)

@app.route('/forgotpassword', methods=['GET','POST'])
@no_ssl_required
def forgot_password():
    error = None
    if request.method == 'POST':
        user = mongo.db.users.find({'email' : request.form['email']})
        if user.count() == 0:
            error = "Could not find account for email: '"+request.form['email']+"'"
            return render_template("forgotpassword.html", error=error)
        else:
            credentials = "Account credentials for Off The Grid Advertising:\n"
            credentials +="Username: "+ user[0]['username']+"\n"
            credentials +="Password: "+ user[0]['password']+"\n"

            msg = MIMEText(credentials)
            msg['Subject'] = "Forgot Password"
            msg['From'] = "Off The Grid Advertising"
            msg['To'] = request.form['email']
            
            s = smtplib.SMTP('localhost')
            s.sendmail("Off_The_Grid_Account@offthegrid.com", [request.form['email']], msg.as_string())
            s.quit()
            flash("Email with password sent to "+request.form['email']+". Don't forget to check your spam.")
            return redirect(url_for('forgot_password'))
    else:
        return render_template('forgotpassword.html', error=error)
# @app.route('/calendar')
# def calendar():
#     return render_template('calendar.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
