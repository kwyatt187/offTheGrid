from flask import Blueprint, render_template, redirect, url_for, session, flash
from ssl_decorators import no_ssl_required

blueprint = Blueprint('logout',__name__)

@blueprint.route('/logout')
@no_ssl_required
def view():
    session.pop('logged_in', None)
    session.pop('account_current', None)
    flash('You were logged out')
    return redirect(url_for('home.view'))
