from flask import Blueprint, redirect, render_template, request, url_for

from app import db
from app.auth import current_user, login_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/facilities")
def facilities():
    user = current_user()
    restaurant = db.get_restaurant(user["restaurant_id"])
    rows = [restaurant] if restaurant is not None else []
    return render_template("admin_restaurants.html", restaurants=rows)


@bp.route("/facilities/<int:facility_id>/toggle", methods=["POST"])
@login_required
def toggle_facility(facility_id):
    user = current_user()
    if facility_id != user["restaurant_id"]:
        return redirect(url_for("admin.facilities"))
    restaurant = db.get_restaurant(facility_id)
    if restaurant is not None:
        db.set_restaurant_active(
            facility_id, not restaurant["active"], user["restaurant_id"]
        )
    return redirect(url_for("admin.facilities"))
