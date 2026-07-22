from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.auth import current_user, login_required
from app.services.pricing import format_price

bp = Blueprint("orders", __name__)

ALLOWED_STATUSES = {"new", "preparing", "ready", "delivered"}


@bp.route("/orders")
@login_required
def board():
    user = current_user()
    status = request.args.get("status")
    if status and status not in ALLOWED_STATUSES:
        status = None
    orders = db.list_orders(user["restaurant_id"], status)
    return render_template(
        "orders.html", orders=orders, status=status, format_price=format_price
    )


@bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def set_status(order_id):
    user = current_user()
    order = db.get_order(order_id)
    if order is None or order["restaurant_id"] != user["restaurant_id"]:
        flash("Order not found.")
        return redirect(url_for("orders.board"))

    new_status = request.form.get("status", "")
    if new_status not in ALLOWED_STATUSES:
        flash("Unknown status.")
        return redirect(url_for("orders.board"))

    db.update_order_status(order_id, new_status)
    return redirect(url_for("orders.board"))
