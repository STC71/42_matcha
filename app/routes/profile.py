from flask import Blueprint, render_template
from app.utils.decorators import login_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/me")
@login_required
def me():
    return render_template("profile/me.html")

@profile_bp.route("/<int:user_id>")
@login_required
def view(user_id):
    return render_template("profile/view.html", user_id=user_id)
