from flask import Blueprint, render_template, redirect, url_for
from ssl_decorators import no_ssl_required
import os

blueprint = Blueprint('ezine', __name__)

@blueprint.route('/ezine')
@no_ssl_required
def view():
    issues = os.listdir(os.path.dirname(__file__)+"/../static/ezine")
    issues = reversed(sorted(issues))
    return render_template('ezine.html', issues=issues)

@blueprint.route('/ezine/<issue>/<page>')
@no_ssl_required
def page_view(issue, page='1'):
    issues = os.listdir(os.path.dirname(__file__)+"/../static/ezine")

    if issue not in issues:
        return redirect(url_for('ezine.view'))

    pages = os.listdir(os.path.dirname(__file__)+"/../static/ezine/"+issue)

    if page+".jpg" not in pages:
        return redirect(url_for('ezine.view'))

    image = url_for('static', filename='ezine/'+issue+'/'+page) + '.jpg'
    return render_template('ezine_issue.html', image=image)

@blueprint.route('/ezine/<issue>')
@no_ssl_required
def issue_view(issue):
    return redirect('/ezine/'+issue+'/1')

