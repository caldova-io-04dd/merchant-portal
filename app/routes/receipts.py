from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    render_template_string,
    request,
    url_for,
)

from app import db
from app.auth import current_user, login_required
from app.services.pricing import format_price

bp = Blueprint("receipts", __name__)

DEFAULT_TEMPLATE = (
    "{{ restaurant.name }}\n"
    "Order #{{ order.id }}\n"
    "Total: {{ total }}\n"
    "Thanks for ordering with Robobites!"
)


def _render(template, order, restaurant):
    total = format_price(order["total_cents"]) if order else "$0.00"
    return render_template_string(
        template, order=order, restaurant=restaurant, total=total
    )


@bp.route("/receipts", methods=["GET", "POST"])
@login_required
def editor():
    user = current_user()
    restaurant = db.get_restaurant(user["restaurant_id"])
    template = db.get_receipt_template(user["restaurant_id"]) or DEFAULT_TEMPLATE

    preview = None
    if request.method == "POST":
        template = request.form.get("template", "")
        if request.form.get("action") == "save":
            db.set_receipt_template(user["restaurant_id"], template)
            flash("Receipt template saved.")
        sample = db.list_orders(user["restaurant_id"])
        order = sample[0] if sample else None
        preview = _render(template, order, restaurant)

    return render_template(
        "receipts.html",
        restaurant=restaurant,
        template=template,
        preview=preview,
    )


@bp.route("/receipts/order/<int:order_id>")
@login_required
def print_receipt(order_id):
    user = current_user()
    order = db.get_order(order_id)
    if order is None or order["restaurant_id"] != user["restaurant_id"]:
        flash("Order not found.")
        return redirect(url_for("orders.board"))
    restaurant = db.get_restaurant(user["restaurant_id"])
    template = db.get_receipt_template(user["restaurant_id"]) or DEFAULT_TEMPLATE
    return _render(template, order, restaurant)
