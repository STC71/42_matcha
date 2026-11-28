"""
Utilidades de seguridad:
- Hash y verificación de contraseñas (bcrypt)
- Rechazo de contraseñas comunes / de diccionario (obligatorio del subject)
- Generación y validación de tokens (verificación de email y reset de password)
"""

"""
Qué hace:
Implementa todo lo relacionado con contraseñas y tokens de forma segura. 
    Un token es un string aleatorio que se usa para verificar la identidad del usuario, 
    por ejemplo, para confirmar su email o restablecer su contraseña.
    Suelen ser de corta duración y se firman con la clave secreta de la app para que no puedan ser falsificados.
    La firma del token permite verificar que no ha sido modificado por un atacante.
    Un ejemplo de token es: 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImlhdCI6MT
     Y4NzQyMzQwMCwiZXhwIjoxNjg3NDI3MDAwfQ.abc123def456ghi789jkl012mno345
     pqr678stu901vwx234yz567890"
    Los token se generan con generate_timed_token() y se validan con confirm_timed_token().
Cumple el requisito del subject de rechazar contraseñas de diccionario.
"""

import re
import secrets
import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app


# ------------------------------------------------------------------
# Hash de contraseñas
# ------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contraseña."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    """Comprueba si la contraseña coincide con el hash almacenado."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


# ------------------------------------------------------------------
# Contraseñas comunes (el subject obliga a rechazarlas)
# ------------------------------------------------------------------
COMMON_PASSWORDS = {
    "password", "password1", "password123", "123456", "12345678", "123456789",
    "1234567890", "qwerty", "abc123", "monkey", "letmein", "dragon", "baseball",
    "iloveyou", "trustno1", "sunshine", "master", "welcome", "shadow", "ashley",
    "football", "jesus", "michael", "ninja", "mustang", "123123", "admin",
    "welcome1", "login", "princess", "solo", "qwerty123", "starwars",
    "passw0rd", "hello", "freedom", "whatever", "qazwsx", "donald", "batman",
    "zaq1zaq1", "qwertyuiop", "123qwe", "password!", "p@ssw0rd", "pass1234",
    "contraseña", "contrasena", "clave", "usuario", "bienvenido", "hola123",
    "amor123", "spain", "espana", "madrid", "barcelona", "valencia",
    "azerty", "motdepasse", "bonjour", "soleil", "chocolat", "loulou",
    "password123!", "iloveyou1", "welcome123", "admin123", "root", "toor",
    "test", "test123", "guest", "guest123", "changeme", "secret", "secret123",
}


def is_common_password(password: str) -> bool:
    """Devuelve True si la contraseña es demasiado común o predecible."""
    if not password:
        return True
    normalized = password.lower().strip()
    if normalized in COMMON_PASSWORDS:
        return True
    # Solo números y longitud corta
    if re.fullmatch(r"\d+", normalized) and len(normalized) <= 10:
        return True
    # Caracteres repetidos (aaaa, 1111...)
    if re.fullmatch(r"(.)\1{3,}", normalized):
        return True
    return False


def validate_password(password: str, min_length: int = 8) -> tuple[bool, str]:
    """
    Valida la fortaleza de la contraseña.
    Retorna (es_valida, mensaje_de_error).
    """
    if not password or len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    if is_common_password(password):
        return False, "This password is too common. Please choose a stronger one."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""


# ------------------------------------------------------------------
# Tokens (verificación de email y reset de contraseña)
# ------------------------------------------------------------------
def generate_token() -> str:
    """Genera un token aleatorio seguro (URL-safe)."""
    return secrets.token_urlsafe(48)


def generate_timed_token(data: str, salt: str = "matcha-token") -> str:
    """Genera un token firmado con tiempo de expiración."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(data, salt=salt)


def confirm_timed_token(token: str, salt: str = "matcha-token", max_age: int = 3600) -> str | None:
    """
    Valida un token firmado.
    Devuelve el contenido original o None si es inválido/expirado.
    max_age por defecto = 1 hora.
    """
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return serializer.loads(token, salt=salt, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
