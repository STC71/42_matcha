"""
Decoradores de autenticación.
"""

"""
Qué hace:
    login_required → protege las rutas privadas.
    guest_required → evita que un usuario logueado vuelva a ver login/register.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(f):
    """Obliga a que el usuario esté autenticado para acceder a la ruta."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def guest_required(f):
    """Solo permite acceso a usuarios NO autenticados (login/register)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            return redirect(url_for("browse.suggestions"))
        return f(*args, **kwargs)
    return decorated_function
