from functools import wraps
from flask import request, redirect, current_app


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
