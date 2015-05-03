from flask import Blueprint, render_template, url_for, session, flash
from pymongo import MongoClient
from ssl_decorators import no_ssl_required

blueprint = Blueprint('forgot_password', __name__)

@blueprint.route('/forgotpassword', methods=['GET','POST'])
@no_ssl_required
def view():
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
            s.sendmail("Off_The_Grid_Account@offthegridadvertising.com", [request.form['email']], msg.as_string())
            s.quit()
            flash("Email with password sent to "+request.form['email']+". Don't forget to check your spam.")
            return redirect(url_for('forgot_password'))
    else:
        return render_template('forgotpassword.html', error=error)
