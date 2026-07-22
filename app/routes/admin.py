from flask import Blueprint, redirect, render_template, request, url_for

from app import db

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/restaurants")
def restaurants():
    rows = db.list_restaurants()
    return render_template("admin_restaurants.html", restaurants=rows)


@bp.route("/restaurants/<int:restaurant_id>/toggle", methods=["POST"])
def toggle_restaurant(restaurant_id):
    restaurant = db.get_restaurant(restaurant_id)
    if restaurant is not None:
        db.set_restaurant_active(restaurant_id, not restaurant["active"])
    return redirect(url_for("admin.restaurants"))
