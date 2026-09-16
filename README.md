# Merchant Portal

The Merchant Portal is the web application Caldova partners use to run their
pharmacy fulfillment operations. Pharmacy teams sign in to manage medication
catalogs, adjust availability, and monitor patient orders as fulfillment work
moves through the network.

## Features

- Menu management: create, edit, and retire menu items with per-item pricing.
- Live order board: see new, in-progress, and delivered orders at a glance.
- Clickable order detail pages with a more polished Caldova-branded merchant experience.
- Availability controls: pause an item or a whole facility during a rush.
- Search across your menu by item name.
- Printable order receipts with a customizable per-facility template.
- Lightweight admin tools for the Caldova operations team.

## Tech stack

- Python 3.11
- Flask
- SQLite (via the standard library `sqlite3` module)
- Jinja2 templates

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python migrations/init_db.py
python run.py
```

The app starts on http://127.0.0.1:5000.

For the Docker-based MDASH demo, build and run the stack from the repo root:

```bash
docker compose up --build
```

Then use the exploit CLI from the workspace root:

```bash
python exploit --target http://localhost:8100 --portal-target http://localhost:5000 --mode all
```

A couple of seed accounts are created by the migration script so you can log in
right away:

| Email                    | Password     |
|--------------------------|--------------|
| `owner@caldova.io`       | `caldova123` |

## Project layout

```
merchant-portal/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── db.py                # SQLite helpers and queries
│   ├── auth.py              # Session login / decorators
│   ├── routes/              # Blueprints
│   └── services/            # Pricing + receipt rendering
├── migrations/
│   └── init_db.py           # Schema + seed data
├── run.py
└── requirements.txt
```

## Usage

Sign in with a partner account, land on the dashboard, and use the left nav to
jump between **Menu**, **Orders**, and **Receipts**. Menu edits are saved
immediately. The order board polls every few seconds so you don't have to
refresh during a busy service.

## License

MIT. See [LICENSE](LICENSE).
