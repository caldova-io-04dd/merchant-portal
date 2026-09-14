from flask import Blueprint, redirect, render_template, request, url_for

from app import db

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/facilities")
def facilities():
    rows = db.list_restaurants()
    return render_template("admin_restaurants.html", restaurants=rows)


@bp.route("/facilities/<int:facility_id>/toggle", methods=["POST"])
def toggle_facility(facility_id):
    restaurant = db.get_restaurant(facility_id)
    if restaurant is not None:
        db.set_restaurant_active(facility_id, not restaurant["active"])
    return redirect(url_for("admin.facilities"))
