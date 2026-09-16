from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app import db
from app.auth import current_user, login_required
from app.services.pricing import normalize_price, format_price

bp = Blueprint("menus", __name__)


def _is_same_origin_post():
    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")
    app_origin = request.host_url.rstrip("/")
    if origin:
        return origin.rstrip("/") == app_origin
    if referer:
        return referer.startswith(request.host_url)
    return False


@bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    facility = db.get_facility(facility_id)
    items = db.list_menu_items(facility_id)
    orders = db.list_orders(facility_id)
    return render_template(
        "dashboard.html",
        facility=facility,
        items=items,
        open_orders=[o for o in orders if o["status"] != "delivered"],
        format_price=format_price,
    )


@bp.route("/menu")
@login_required
def menu():
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    items = db.list_menu_items(facility_id)
    return render_template("menu.html", items=items, format_price=format_price)


@bp.route("/menu/search")
@login_required
def search():
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    term = request.args.get("q", "")
    results = db.search_menu_items(facility_id, term)
    return render_template(
        "menu.html", items=results, format_price=format_price, term=term
    )


@bp.route("/menu/item/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    item = db.get_menu_item(item_id)
    if item is None:
        flash("That item no longer exists.")
        return redirect(url_for("menus.menu"))
    if item["restaurant_id"] != facility_id:
        flash("You can only edit menu items for your facility.")
        return redirect(url_for("menus.menu"))

    if request.method == "POST":
        if not _is_same_origin_post():
            abort(400)
        name = request.form.get("name", item["name"]).strip()
        price_cents = normalize_price(request.form.get("price", ""))
        if price_cents is None:
            flash("Price must be a valid amount under the supported limit.")
            return redirect(url_for("menus.menu"))
        available = request.form.get("available") == "on"
        db.update_menu_item(item_id, name, price_cents, available)
        flash("Menu item updated.")
        return redirect(url_for("menus.menu"))

    return render_template("edit_item.html", item=item, format_price=format_price)


@bp.route("/menu/item/new", methods=["POST"])
@login_required
def create_item():
    if not _is_same_origin_post():
        abort(400)
    user = current_user()
    facility_id = user.get("facility_id") or user.get("restaurant_id")
    name = request.form.get("name", "").strip()
    price_cents = normalize_price(request.form.get("price", ""))
    if not name or price_cents is None:
        flash("Give the item a name and a valid price.")
        return redirect(url_for("menus.menu"))
    db.create_menu_item(facility_id, name, price_cents)
    flash("Menu item added.")
    return redirect(url_for("menus.menu"))
