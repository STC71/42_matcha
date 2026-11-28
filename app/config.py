"""
Configuración de la aplicación según el entorno.
Todas las variables sensibles se leen desde el archivo .env
"""

"""
Qué hace:
Centraliza toda la configuración. 
Lee las variables del .env y define clases distintas según el entorno (development / production / testing).
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ----------------------------------------------------------
    # Aplicación
    # ----------------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    APP_NAME = os.getenv("APP_NAME", "Matcha")
    APP_URL = os.getenv("APP_URL", "http://localhost:5000")

    # ----------------------------------------------------------
    # Base de datos
    # ----------------------------------------------------------
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://matcha:matcha_secret_change_me@db:5432/matcha",
    )

    # ----------------------------------------------------------
    # Sesiones
    # ----------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv("PERMANENT_SESSION_LIFETIME", 604800))  # 7 días
    )
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ----------------------------------------------------------
    # Seguridad y uploads
    # ----------------------------------------------------------
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", 8))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # ----------------------------------------------------------
    # Email (MailHog en desarrollo)
    # ----------------------------------------------------------
    MAIL_SERVER = os.getenv("MAIL_SERVER", "mailhog")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 1025))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@matcha.local")

    # ----------------------------------------------------------
    # Real-time (SocketIO)
    # ----------------------------------------------------------
    SOCKETIO_MESSAGE_QUEUE = os.getenv("SOCKETIO_MESSAGE_QUEUE", "redis://redis:6379/0")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
