"""
Servicio de autenticación.
Contiene la lógica de negocio: registro, login, verificación y reset.
"""
from flask import current_app, url_for
from flask_mail import Message

from app.extensions import mail
from app.repositories import user_repository as user_repo
from app.utils.security import (
    hash_password,
    check_password,
    validate_password,
    generate_token,
)


class AuthError(Exception):
    """Error de negocio de autenticación."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def register_user(email: str, username: str, first_name: str,
                  last_name: str, password: str) -> int:
    """
    Registra un nuevo usuario.
    - Valida la contraseña
    - Comprueba que email y username no existan
    - Hashea la contraseña
    - Crea el usuario + perfil
    - Envía email de verificación
    """
    # 1. Validar contraseña
    min_len = current_app.config.get("PASSWORD_MIN_LENGTH", 8)
    is_valid, error_msg = validate_password(password, min_len)
    if not is_valid:
        raise AuthError(error_msg)

    # 2. Comprobar unicidad
    if user_repo.find_by_email(email):
        raise AuthError("An account with this email already exists.")
    if user_repo.find_by_username(username):
        raise AuthError("This username is already taken.")

    # 3. Crear usuario
    password_hash = hash_password(password)
    verification_token = generate_token()

    user_id = user_repo.create_user(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password_hash=password_hash,
        verification_token=verification_token,
    )

    # 4. Enviar email de verificación
    _send_verification_email(email, first_name, verification_token)

    return user_id


def verify_email(token: str) -> bool:
    """Verifica el email del usuario mediante el token."""
    user = user_repo.find_by_verification_token(token)
    if not user:
        raise AuthError("Invalid or expired verification link.")
    if user["is_verified"]:
        return True  # ya estaba verificado

    user_repo.mark_as_verified(user["id"])
    return True


def login_user(username: str, password: str) -> dict:
    """
    Autentica al usuario.
    Devuelve el diccionario del usuario si todo es correcto.
    """
    user = user_repo.find_by_username(username)
    if not user:
        # Mensaje genérico para no filtrar información
        raise AuthError("Invalid username or password.")

    if not check_password(password, user["password_hash"]):
        raise AuthError("Invalid username or password.")

    if not user["is_verified"]:
        raise AuthError(
            "Please verify your email before logging in. "
            "Check your inbox (or MailHog)."
        )

    if not user["is_active"]:
        raise AuthError("This account has been deactivated.")

    user_repo.update_last_seen(user["id"])
    return user


def request_password_reset(email: str):
    """Genera y envía un token de reset de contraseña."""
    user = user_repo.find_by_email(email)
    if not user:
        # Por seguridad no revelamos si el email existe
        return

    token = generate_token()
    user_repo.set_reset_token(user["id"], token, expires_minutes=60)
    _send_reset_email(user["email"], user["first_name"], token)


def reset_password(token: str, new_password: str):
    """Cambia la contraseña usando el token de reset."""
    min_len = current_app.config.get("PASSWORD_MIN_LENGTH", 8)
    is_valid, error_msg = validate_password(new_password, min_len)
    if not is_valid:
        raise AuthError(error_msg)

    user = user_repo.find_by_reset_token(token)
    if not user:
        raise AuthError("Invalid or expired reset link.")

    password_hash = hash_password(new_password)
    user_repo.update_password(user["id"], password_hash)


# ------------------------------------------------------------------
# Helpers privados de email
# ------------------------------------------------------------------
def _send_verification_email(email: str, first_name: str, token: str):
    verify_url = url_for("auth.verify", token=token, _external=True)
    msg = Message(
        subject="Verify your Matcha account",
        recipients=[email],
        body=(
            f"Hi {first_name},\n\n"
            f"Welcome to Matcha! Please verify your email by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            f"If you did not create an account, you can ignore this email.\n"
        ),
        html=(
            f"<p>Hi <strong>{first_name}</strong>,</p>"
            f"<p>Welcome to Matcha! Please verify your email:</p>"
            f'<p><a href="{verify_url}">Verify my account</a></p>'
            f"<p>If you did not create an account, you can ignore this email.</p>"
        ),
    )
    mail.send(msg)


def _send_reset_email(email: str, first_name: str, token: str):
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    msg = Message(
        subject="Reset your Matcha password",
        recipients=[email],
        body=(
            f"Hi {first_name},\n\n"
            f"We received a request to reset your password. "
            f"Click the link below (valid for 1 hour):\n\n"
            f"{reset_url}\n\n"
            f"If you did not request this, you can ignore this email.\n"
        ),
        html=(
            f"<p>Hi <strong>{first_name}</strong>,</p>"
            f"<p>We received a request to reset your password:</p>"
            f'<p><a href="{reset_url}">Reset my password</a></p>'
            f"<p>This link is valid for 1 hour.</p>"
        ),
    )
    mail.send(msg)
