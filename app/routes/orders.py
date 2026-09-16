from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

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


@bp.route("/orders/<int:order_id>")
@login_required
def detail(order_id):
    user = current_user()
    order = db.get_order(order_id)
    if order is None or order["restaurant_id"] != user["restaurant_id"]:
        flash("Order not found.")
        return redirect(url_for("orders.board"))

    restaurant = db.get_restaurant(user["restaurant_id"])
    template = db.get_receipt_template(user["restaurant_id"]) or (
        "{{ restaurant.name }}\n"
        "Order #{{ order.id }}\n"
        "Total: {{ total }}\n"
        "Thanks for ordering with Caldova!"
    )
    total = format_price(order["total_cents"])
    rendered_receipt = (
        template.replace("{{ restaurant.name }}", str(restaurant["name"]))
        .replace("{{ order.id }}", str(order["id"]))
        .replace("{{ total }}", str(total))
        .replace("{{ order.customer_name }}", str(order.get("customer_name", "")))
    )

    return render_template(
        "order_detail.html",
        order=order,
        restaurant=restaurant,
        format_price=format_price,
        receipt=rendered_receipt,
        template=template,
    )


@bp.route("/orders/<int:order_id>/survey")
@login_required
def survey_redirect(order_id):
    user = current_user()
    order = db.get_order(order_id)
    if order is None or order["restaurant_id"] != user["restaurant_id"]:
        flash("Order not found.")
        return redirect(url_for("orders.board"))

    return redirect(url_for("orders.board"))


@bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def set_status(order_id):
    if not request.method == "POST":
        return redirect(url_for("orders.board"))

    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")
    app_origin = request.host_url.rstrip("/")
    if origin:
        if origin.rstrip("/") != app_origin:
            abort(400)
    elif referer and not referer.startswith(request.host_url):
        abort(400)

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
