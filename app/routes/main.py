from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("browse.suggestions"))
    return render_template("index.html")
