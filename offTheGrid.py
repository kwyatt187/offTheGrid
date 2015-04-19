import smtplib
from email.mime.text import MIMEText
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
from flask_googlemaps import GoogleMaps
import config

app = Flask(__name__)
app.config.from_object('config')
GoogleMaps(app)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    os.chdir('/var/www/offTheGrid/static/home_images')
    scrolling_images = os.listdir('.')
    scrolling_images = ["home_images/"+img for img in scrolling_images]
    return render_template('home.html', scrolling_images=scrolling_images
)

@app.route('/findlocations')
def find_locations():
    return render_template('findlocations.html')

@app.route('/buyad', methods=['GET','POST'])
def buy_ad():
    if request.method == 'POST':
        book_request = "Location: " + request.form['location'] + "\n"
        book_request += "Budget: " + request.form['budget'] + "\n"
        book_request += "Ad type: " + request.form['adtype'] + "\n"

        msg = MIMEText(book_request)
        msg['Subject'] = "Ad request"
        msg['From'] = "Off The Grid booking"
        msg['To'] = "kwyatt187@gmail.com"
        
        s = smtplib.SMTP('localhost')
        s.sendmail("Off_The_Grid_booking@offthegrid.com", ["kwyatt187@gmail.com"], msg.as_string())
        s.quit()
        flash('Ad request sent')
        return redirect(url_for('buy_ad'))
    else:
        cur = g.db.execute("select * from locations")
        locations = [str(row[0]) for row in cur.fetchall()]
        return render_template('buyad.html', locations=locations)

@app.route('/bookevent', methods=['GET', 'POST'])
def book_event():
    if request.method == 'POST':
        book_request = "Reason: " + request.form['reason'] + "\n"
        book_request += "Location: " + request.form['location'] + "\n"
        book_request += "Secrecy level: " + request.form['secrecylevel'] + "\n"
        book_request += "Number of people: " + request.form['numpeople'] + "\n"
        book_request += "Budget: " + request.form['budget']

        msg = MIMEText(book_request)
        msg['Subject'] = "Booking request"
        msg['From'] = "Off The Grid booking"
        msg['To'] = "kwyatt187@gmail.com"
        
        s = smtplib.SMTP('localhost')
        s.sendmail("Off_The_Grid_booking@offthegrid.com", ["kwyatt187@gmail.com"], msg.as_string())
        s.quit()
        flash('Booking request sent')
        return render_template('bookevent.html')
    else:
        cur = g.db.execute("select * from locations")
        locations = [str(row[0]) for row in cur.fetchall()]
        return render_template('bookevent.html', locations=locations)

@app.route('/afterparty')
def after_party():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        cur = g.db.execute('select * from afterparty order by id desc')
        afterparties = [dict(location=row[1],date=row[2],description=row[3],submittedby=row[4]) for row in cur.fetchall()]
        return render_template('afterparty.html', afterparties=afterparties)

@app.route('/addafterparty', methods=['GET', 'POST'])
def add_after_party():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == 'POST':
            g.db.execute('insert into afterparty (location,date,description,username) values (?, ?, ?, ?)',
                         [request.form['location'], request.form['date'], request.form['description'], request.form['username']])
            g.db.commit()
            return redirect(url_for('after_party'))
        else:
            return render_template('addafterparty.html')

@app.route('/myafterparties', methods=['GET', 'POST'])
def edit_after_parties():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.method == 'POST':
            if 'update' in request.form:
                g.db.execute('update afterparty set location=?,date=?,description=? where id == ?',
                             [request.form['location'], request.form['date'], request.form['description'], request.form['id']])
            elif 'delete' in request.form:
                g.db.execute('delete from afterparty where id == ?', request.form['id'])

            g.db.commit()
            return redirect(url_for('edit_after_parties'))
        else:
            cur = g.db.execute('select * from afterparty where username == ? order by id desc', [session['username']])
            afterparties = [dict(id=row[0],location=row[1],date=row[2],description=row[3],submittedby=row[4]) for row in cur.fetchall()]
            return render_template('myafterparties.html', afterparties=afterparties)
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute("select username,password from users where username == ? and password == ?",
                           [request.form['username'],request.form['password']])
        if len(cur.fetchall()) == 0:
            error = "Invalid username or password"
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('after_party'))
    else:
        return render_template('login.html', error=error)
        

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select username from users where username == ?',
                           [request.form['username']])
        if len(cur.fetchall()) > 0:
            error = "Username already exists"
            return render_template('signup.html', error=error)
        else:
            g.db.execute('insert into users (username,password,email) values (?, ?, ?)',
                         [request.form['username'], request.form['password'], request.form['email']])
            g.db.commit()
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('after_party'))
    else:
        return render_template('signup.html', error=error)
# @app.route('/calendar')
# def calendar():
#     return render_template('calendar.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
