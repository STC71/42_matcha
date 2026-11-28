"""
Rutas de autenticación: registro, login, verificación y reset de contraseña.
"""
from flask import (
    Blueprint, render_template, redirect, url_for,
    session, flash, request
)
from app.utils.decorators import guest_required, login_required
from app.services.auth_service import (
    register_user, verify_email, login_user,
    request_password_reset, reset_password, AuthError
)
from app.repositories import user_repository as user_repo

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
@guest_required
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        password = request.form.get("password", "")

        # Validaciones básicas de campos obligatorios
        if not all([email, username, first_name, last_name, password]):
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        try:
            register_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            flash(
                "Account created! Please check your email (MailHog) to verify your account.",
                "success",
            )
            return redirect(url_for("auth.login"))
        except AuthError as e:
            flash(e.message, "error")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@guest_required
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("auth/login.html")

        try:
            user = login_user(username, password)

            # Guardamos datos mínimos en la sesión
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["first_name"] = user["first_name"]

            flash(f"Welcome back, {user['first_name']}!", "success")

            # Redirigimos a la página que intentaba visitar o a suggestions
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("browse.suggestions"))

        except AuthError as e:
            flash(e.message, "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    user_id = session.get("user_id")
    if user_id:
        user_repo.set_offline(user_id)
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))


@auth_bp.route("/verify/<token>")
def verify(token):
    try:
        verify_email(token)
        flash("Your email has been verified! You can now log in.", "success")
    except AuthError as e:
        flash(e.message, "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@guest_required
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if email:
            request_password_reset(email)
        # Siempre mostramos el mismo mensaje (seguridad)
        flash(
            "If an account with that email exists, a reset link has been sent.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@guest_required
def reset_password_route(token):
    if request.method == "POST":
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if password != password2:
            flash("Passwords do not match.", "error")
            return render_template("auth/reset_password.html", token=token)

        try:
            reset_password(token, password)
            flash("Your password has been updated. You can now log in.", "success")
            return redirect(url_for("auth.login"))
        except AuthError as e:
            flash(e.message, "error")

    return render_template("auth/reset_password.html", token=token)
