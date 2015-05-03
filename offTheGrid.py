from flask import Flask
import os
import config
from importlib import import_module
from glob import glob

app = Flask(__name__)
app.config.from_object('config')

views = ['home', 'account', 'after_party', 'add_after_party', 'edit_after_parties', 'book_event', 'buy_ad', 'forgot_password', 'locations', 'login', 'logout', 'update_credit_card', 'signup', 'verify', 'cancel']

for module_name in views:
    module = import_module('views.'+module_name)
    app.register_blueprint(module.blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
