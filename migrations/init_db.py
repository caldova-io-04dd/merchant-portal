"""Create the merchant portal schema and seed a couple of partner accounts."""

import hashlib
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS orders;

CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    receipt_template TEXT
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
);

CREATE TABLE menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    available INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    total_cents INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
);
"""


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def seed(conn):
    restaurants = [
        ("Caldova Pharmacy", "owner@caldova.io"),
    ]
    for name, email in restaurants:
        conn.execute(
            "INSERT INTO restaurants (name, contact_email) VALUES (?, ?)",
            (name, email),
        )

    accounts = [
        (1, "owner@caldova.io", "caldova123", "cald"),
    ]
    for restaurant_id, email, password, salt in accounts:
        conn.execute(
            "INSERT INTO users (restaurant_id, email, password_hash, "
            "password_salt) VALUES (?, ?, ?, ?)",
            (restaurant_id, email, hash_password(password, salt), salt),
        )

    items = [
        (1, "Amoxicillin 500mg", 1450),
        (1, "Insulin Pen", 2300),
        (1, "Vitamin D3", 850),
    ]
    for restaurant_id, name, price in items:
        conn.execute(
            "INSERT INTO menu_items (restaurant_id, name, price_cents) "
            "VALUES (?, ?, ?)",
            (restaurant_id, name, price),
        )

    orders = [
        (1, "Dana P.", 1850, "new"),
        (1, "Miguel R.", 1200, "preparing"),
        (1, "Aiko T.", 1900, "ready"),
        (1, "Sam W.", 500, "delivered"),
    ]
    for restaurant_id, customer, total, status in orders:
        conn.execute(
            "INSERT INTO orders (restaurant_id, customer_name, total_cents, "
            "status) VALUES (?, ?, ?, ?)",
            (restaurant_id, customer, total, status),
        )

    conn.commit()


def main():
    path = Config.DATABASE_PATH
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    seed(conn)
    conn.close()
    print("Initialized database at", path)


if __name__ == "__main__":
    main()
