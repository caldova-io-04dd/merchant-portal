from html import escape

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app import db
from app.auth import current_user, login_required
from app.services.pricing import format_price

bp = Blueprint("receipts", __name__)

DEFAULT_TEMPLATE = (
    "{{ facility.name }}\n"
    "Order #{{ order.id }}\n"
    "Total: {{ total }}\n"
    "Thanks for ordering with Caldova!"
)


def _row_value(row, key, default=None):
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    return row[key] if key in row.keys() else default


def _render(template, order, facility):
    total = format_price(order["total_cents"]) if order else "$0.00"
    rendered = template
    if order is not None:
        rendered = rendered.replace("{{ facility.name }}", escape(str(facility["name"])))
        rendered = rendered.replace("{{ order.id }}", escape(str(order["id"])))
        rendered = rendered.replace("{{ total }}", escape(str(total)))
        rendered = rendered.replace("{{ order.customer_name }}", escape(str(_row_value(order, "customer_name", ""))))
    else:
        rendered = rendered.replace("{{ facility.name }}", escape(str(facility["name"])))
        rendered = rendered.replace("{{ order.id }}", "0")
        rendered = rendered.replace("{{ total }}", escape(str(total)))
    return rendered


@bp.route("/receipts", methods=["GET", "POST"])
@login_required
def editor():
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    facility = db.get_facility(facility_id)
    template = db.get_receipt_template(facility_id) or DEFAULT_TEMPLATE

    preview = None
    if request.method == "POST":
        template = request.form.get("template", "")
        if request.form.get("action") == "save":
            db.set_receipt_template(facility_id, template)
            flash("Receipt template saved.")
        sample = db.list_orders(facility_id)
        order = sample[0] if sample else None
        preview = _render(template, order, facility)

    return render_template(
        "receipts.html",
        facility=facility,
        template=template,
        preview=preview,
    )


@bp.route("/receipts/order/<int:order_id>")
@login_required
def print_receipt(order_id):
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    order = db.get_order(order_id)
    if order is None or order["restaurant_id"] != facility_id:
        flash("Order not found.")
        return redirect(url_for("orders.board"))
    facility = db.get_facility(facility_id)
    template = db.get_receipt_template(facility_id) or DEFAULT_TEMPLATE
    return _render(template, order, facility)
