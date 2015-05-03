from flask import Blueprint, render_template
from ssl_decorators import no_ssl_required
import os

blueprint = Blueprint('home', __name__)

@blueprint.route('/')
@no_ssl_required
def view():
    scrolling_images = os.listdir(os.path.dirname(__file__)+"/../static/home_images")
    scrolling_images = ["home_images/"+img for img in scrolling_images]
    return render_template('home.html', scrolling_images=scrolling_images)

