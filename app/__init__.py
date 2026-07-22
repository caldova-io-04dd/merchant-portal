from flask import Flask, redirect, url_for

from config import Config
from app import db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)

    from app.routes.auth_routes import bp as auth_bp
    from app.routes.menus import bp as menus_bp
    from app.routes.orders import bp as orders_bp
    from app.routes.receipts import bp as receipts_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(menus_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        return redirect(url_for("menus.dashboard"))

    return app
