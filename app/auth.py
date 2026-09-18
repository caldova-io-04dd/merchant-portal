import hashlib
import hmac

from functools import wraps

from flask import g, redirect, session, url_for

from app import db


def _hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _row_value(row, *keys):
    if row is None:
        return None
    if isinstance(row, dict):
        for key in keys:
            value = row.get(key)
            if value is not None:
                return value
        return None
    for key in keys:
        if key in row.keys():
            value = row[key]
            if value is not None:
                return value
    return None


def verify_password(user, password):
    expected = user["password_hash"]
    candidate = _hash_password(password, user["password_salt"])
    return hmac.compare_digest(expected, candidate)


def login_user(user):
    user = dict(user) if not isinstance(user, dict) else user
    session["user_id"] = user["id"]
    session["facility_id"] = _row_value(user, "facility_id", "restaurant_id")
    session["restaurant_id"] = session["facility_id"]


def logout_user():
    session.clear()


def current_facility_id():
    if "facility_id" in session:
        return session["facility_id"]
    if "restaurant_id" in session:
        return session["restaurant_id"]
    user = current_user()
    if user is None:
        return None
    return _row_value(user, "facility_id", "restaurant_id")


def current_user():
    if "user" not in g:
        user_id = session.get("user_id")
        g.user = db.get_user(user_id) if user_id else None
        if g.user is not None:
            g.user = dict(g.user)
            g.user["facility_id"] = _row_value(g.user, "facility_id", "restaurant_id")
    return g.user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
