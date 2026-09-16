from flask import Blueprint, redirect, render_template, request, url_for

from app import db
from app.auth import current_user, login_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/facilities")
def facilities():
    rows = db.list_facilities()
    return render_template("admin_restaurants.html", restaurants=rows)


@bp.route("/facilities/<int:facility_id>/toggle", methods=["POST"])
def toggle_facility(facility_id):
    facility = db.get_facility(facility_id)
    if facility is not None:
        db.set_facility_active(facility_id, not facility["active"])
    return redirect(url_for("admin.facilities"))
