from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app import auth, db

bp = Blueprint("auth", __name__)


def _is_same_origin_request():
    origin = request.headers.get("Origin")
    referer = request.headers.get("Referer")
    app_origin = request.host_url.rstrip("/")

    if origin:
        return origin.rstrip("/") == app_origin
    if referer:
        return referer.startswith(request.host_url)
    return False


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not _is_same_origin_request():
            abort(400)

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.get_user_by_email(email)
        if user and auth.verify_password(user, password):
            auth.login_user(user)
            return redirect(url_for("menus.dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    if not _is_same_origin_request():
        abort(400)
    auth.logout_user()
    return redirect(url_for("auth.login"))
