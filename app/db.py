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


# --- Users / restaurants -------------------------------------------------

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


def get_restaurant(restaurant_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM restaurants WHERE id = ?", (restaurant_id,)
    ).fetchone()


def list_restaurants():
    db = get_db()
    return db.execute(
        "SELECT * FROM restaurants ORDER BY name"
    ).fetchall()


def set_restaurant_active(restaurant_id, active, authorized_restaurant_id):
    db = get_db()
    cursor = db.execute(
        "UPDATE restaurants SET active = ? WHERE id = ? AND id = ?",
        (1 if active else 0, restaurant_id, authorized_restaurant_id),
    )
    db.commit()
    return cursor.rowcount == 1


def get_receipt_template(restaurant_id):
    db = get_db()
    row = db.execute(
        "SELECT receipt_template FROM restaurants WHERE id = ?",
        (restaurant_id,),
    ).fetchone()
    return row["receipt_template"] if row else None


def set_receipt_template(restaurant_id, template):
    db = get_db()
    db.execute(
        "UPDATE restaurants SET receipt_template = ? WHERE id = ?",
        (template, restaurant_id),
    )
    db.commit()


# --- Menu ----------------------------------------------------------------

def list_menu_items(restaurant_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM menu_items WHERE restaurant_id = ? ORDER BY name",
        (restaurant_id,),
    ).fetchall()


def search_menu_items(restaurant_id, term):
    """Look up menu items for a restaurant whose name matches `term`."""
    db = get_db()
    query = (
        "SELECT * FROM menu_items "
        "WHERE restaurant_id = ? AND name LIKE ? "
        "ORDER BY name"
    )
    return db.execute(query, (restaurant_id, f"%{term}%")).fetchall()


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


def create_menu_item(restaurant_id, name, price_cents):
    db = get_db()
    cur = db.execute(
        "INSERT INTO menu_items (restaurant_id, name, price_cents, available) "
        "VALUES (?, ?, ?, 1)",
        (restaurant_id, name, price_cents),
    )
    db.commit()
    return cur.lastrowid


# --- Orders --------------------------------------------------------------

def list_orders(restaurant_id, status=None):
    db = get_db()
    if status:
        return db.execute(
            "SELECT * FROM orders WHERE restaurant_id = ? AND status = ? "
            "ORDER BY created_at DESC",
            (restaurant_id, status),
        ).fetchall()
    return db.execute(
        "SELECT * FROM orders WHERE restaurant_id = ? ORDER BY created_at DESC",
        (restaurant_id,),
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
