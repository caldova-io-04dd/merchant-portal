import hashlib
import hmac

from functools import wraps

from flask import g, redirect, session, url_for

from app import db


def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def verify_password(user, password):
    expected = user["password_hash"]
    candidate = _hash_password(password, user["password_salt"])
    return hmac.compare_digest(expected, candidate)


def login_user(user):
    session["user_id"] = user["id"]
    session["restaurant_id"] = user["restaurant_id"]


def logout_user():
    session.clear()


def current_user():
    if "user" not in g:
        user_id = session.get("user_id")
        g.user = db.get_user(user_id) if user_id else None
    return g.user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
