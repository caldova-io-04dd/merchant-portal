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
from app.services.pricing import normalize_price, format_price

bp = Blueprint("menus", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    restaurant = db.get_restaurant(user["restaurant_id"])
    items = db.list_menu_items(user["restaurant_id"])
    orders = db.list_orders(user["restaurant_id"])
    return render_template(
        "dashboard.html",
        restaurant=restaurant,
        items=items,
        open_orders=[o for o in orders if o["status"] != "delivered"],
        format_price=format_price,
    )


@bp.route("/menu")
@login_required
def menu():
    user = current_user()
    items = db.list_menu_items(user["restaurant_id"])
    return render_template("menu.html", items=items, format_price=format_price)


@bp.route("/menu/search")
@login_required
def search():
    user = current_user()
    term = request.args.get("q", "")
    results = db.search_menu_items(user["restaurant_id"], term)
    return render_template(
        "menu.html", items=results, format_price=format_price, term=term
    )


@bp.route("/menu/item/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = db.get_menu_item(item_id)
    if item is None:
        flash("That item no longer exists.")
        return redirect(url_for("menus.menu"))

    if request.method == "POST":
        name = request.form.get("name", item["name"]).strip()
        price_cents = normalize_price(request.form.get("price", ""))
        available = request.form.get("available") == "on"
        db.update_menu_item(item_id, name, price_cents, available)
        flash("Menu item updated.")
        return redirect(url_for("menus.menu"))

    return render_template("edit_item.html", item=item, format_price=format_price)


@bp.route("/menu/item/new", methods=["POST"])
@login_required
def create_item():
    user = current_user()
    name = request.form.get("name", "").strip()
    price_cents = normalize_price(request.form.get("price", ""))
    if not name:
        flash("Give the item a name first.")
        return redirect(url_for("menus.menu"))
    db.create_menu_item(user["restaurant_id"], name, price_cents)
    flash("Menu item added.")
    return redirect(url_for("menus.menu"))
