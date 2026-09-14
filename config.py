import os


class Config:
    """Runtime configuration for the merchant portal."""

    SECRET_KEY = os.environ.get("MERCHANT_PORTAL_SECRET")
    if not SECRET_KEY:
        raise RuntimeError("MERCHANT_PORTAL_SECRET must be set in the environment")

    DATABASE_PATH = os.environ.get(
        "MERCHANT_PORTAL_DB",
        os.path.join(os.path.dirname(__file__), "merchant_portal.db"),
    )
    SESSION_COOKIE_HTTPONLY = True
    ORDERS_PER_PAGE = 25
