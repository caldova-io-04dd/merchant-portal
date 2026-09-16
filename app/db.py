import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


# --- Users / facilities ---------------------------------------------------

def get_user_by_email(email):
    db = get_db()
    return db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()


def get_user(user_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def get_facility(facility_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM restaurants WHERE id = ?", (facility_id,)
    ).fetchone()


def get_restaurant(restaurant_id):
    return get_facility(restaurant_id)


def list_facilities():
    db = get_db()
    return db.execute(
        "SELECT * FROM restaurants ORDER BY name"
    ).fetchall()


def list_restaurants():
    return list_facilities()


def set_facility_active(facility_id, active):
    db = get_db()
    cursor = db.execute(
        "UPDATE restaurants SET active = ? WHERE id = ?",
        (1 if active else 0, facility_id),
    )
    db.commit()
    return cursor.rowcount == 1


def set_restaurant_active(restaurant_id, active):
    return set_facility_active(restaurant_id, active)


def get_receipt_template(facility_id):
    db = get_db()
    row = db.execute(
        "SELECT receipt_template FROM restaurants WHERE id = ?",
        (facility_id,),
    ).fetchone()
    return row["receipt_template"] if row else None


def set_receipt_template(facility_id, template):
    db = get_db()
    db.execute(
        "UPDATE restaurants SET receipt_template = ? WHERE id = ?",
        (template, facility_id),
    )
    db.commit()


# --- Menu ----------------------------------------------------------------

def list_menu_items(facility_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM menu_items WHERE restaurant_id = ? ORDER BY name",
        (facility_id,),
    ).fetchall()


def search_menu_items(facility_id, term):
    """Look up menu items for a facility whose name matches `term`."""
    db = get_db()
    query = (
        "SELECT * FROM menu_items "
        "WHERE restaurant_id = ? AND name LIKE ? "
        "ORDER BY name"
    )
    return db.execute(query, (facility_id, f"%{term}%")).fetchall()


def get_menu_item(item_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM menu_items WHERE id = ?", (item_id,)
    ).fetchone()


def update_menu_item(item_id, name, price_cents, available):
    db = get_db()
    db.execute(
        "UPDATE menu_items SET name = ?, price_cents = ?, available = ? "
        "WHERE id = ?",
        (name, price_cents, 1 if available else 0, item_id),
    )
    db.commit()


def create_menu_item(facility_id, name, price_cents):
    db = get_db()
    cur = db.execute(
        "INSERT INTO menu_items (restaurant_id, name, price_cents, available) "
        "VALUES (?, ?, ?, 1)",
        (facility_id, name, price_cents),
    )
    db.commit()
    return cur.lastrowid


# --- Orders --------------------------------------------------------------

def list_orders(facility_id, status=None):
    db = get_db()
    if status:
        return db.execute(
            "SELECT * FROM orders WHERE restaurant_id = ? AND status = ? "
            "ORDER BY created_at DESC",
            (facility_id, status),
        ).fetchall()
    return db.execute(
        "SELECT * FROM orders WHERE restaurant_id = ? ORDER BY created_at DESC",
        (facility_id,),
    ).fetchall()


def get_order(order_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM orders WHERE id = ?", (order_id,)
    ).fetchone()


def update_order_status(order_id, status):
    db = get_db()
    db.execute(
        "UPDATE orders SET status = ? WHERE id = ?", (status, order_id)
    )
    db.commit()
