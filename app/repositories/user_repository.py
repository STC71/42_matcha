"""
Repositorio de usuarios.
Todas las consultas SQL se escriben a mano (sin ORM).
"""
from app.utils.db import execute, get_db


def create_user(email: str, username: str, first_name: str, last_name: str,
                 password_hash: str, verification_token: str):
    """Crea un nuevo usuario y su perfil vacío. Devuelve el id."""
    query = """
        INSERT INTO users (
            email, username, first_name, last_name,
            password_hash, verification_token, verification_sent_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        RETURNING id
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (
                email.lower().strip(),
                username.lower().strip(),
                first_name.strip(),
                last_name.strip(),
                password_hash,
                verification_token,
            ))
            user_id = cur.fetchone()["id"]

            # Creamos el perfil vacío asociado
            cur.execute(
                "INSERT INTO profiles (user_id) VALUES (%s)",
                (user_id,)
            )
            return user_id


def find_by_email(email: str):
    """Busca un usuario por email."""
    return execute(
        "SELECT * FROM users WHERE email = %s",
        (email.lower().strip(),),
        fetchone=True,
    )


def find_by_username(username: str):
    """Busca un usuario por username."""
    return execute(
        "SELECT * FROM users WHERE username = %s",
        (username.lower().strip(),),
        fetchone=True,
    )


def find_by_id(user_id: int):
    """Busca un usuario por id."""
    return execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,),
        fetchone=True,
    )


def find_by_verification_token(token: str):
    """Busca un usuario por token de verificación de email."""
    return execute(
        "SELECT * FROM users WHERE verification_token = %s",
        (token,),
        fetchone=True,
    )


def find_by_reset_token(token: str):
    """Busca un usuario por token de reset de contraseña (y que no haya expirado)."""
    return execute(
        """
        SELECT * FROM users
        WHERE reset_token = %s
          AND reset_token_expires > NOW()
        """,
        (token,),
        fetchone=True,
    )


def mark_as_verified(user_id: int):
    """Marca el email del usuario como verificado."""
    execute(
        """
        UPDATE users
        SET is_verified = TRUE,
            verification_token = NULL,
            updated_at = NOW()
        WHERE id = %s
        """,
        (user_id,),
    )


def set_reset_token(user_id: int, token: str, expires_minutes: int = 60):
    """Guarda el token de reset de contraseña."""
    execute(
        """
        UPDATE users
        SET reset_token = %s,
            reset_token_expires = NOW() + (%s || ' minutes')::INTERVAL,
            updated_at = NOW()
        WHERE id = %s
        """,
        (token, str(expires_minutes), user_id),
    )


def update_password(user_id: int, password_hash: str):
    """Actualiza la contraseña y limpia el token de reset."""
    execute(
        """
        UPDATE users
        SET password_hash = %s,
            reset_token = NULL,
            reset_token_expires = NULL,
            updated_at = NOW()
        WHERE id = %s
        """,
        (password_hash, user_id),
    )


def update_last_seen(user_id: int):
    """Actualiza la última conexión del usuario."""
    execute(
        "UPDATE users SET last_seen = NOW(), is_online = TRUE WHERE id = %s",
        (user_id,),
    )


def set_offline(user_id: int):
    """Marca al usuario como offline."""
    execute(
        "UPDATE users SET is_online = FALSE, last_seen = NOW() WHERE id = %s",
        (user_id,),
    )
