from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app import auth, db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)
        if user and auth.verify_password(user, password):
            auth.login_user(user)
            return redirect(url_for("menus.dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    auth.logout_user()
    return redirect(url_for("auth.login"))
